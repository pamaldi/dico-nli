"""Baseline con Claude via Message Batches API (meta' prezzo): zero-shot e few-shot sul dev.

Uso:
  uv run python scripts/llm_claude.py estimate --shots 0 8          # prompt d'esempio e costo, nessuna spesa
  uv run python scripts/llm_claude.py run --confirm --shots 0       # invia (o riprende) il batch
  uv run python scripts/llm_claude.py evaluate --shots 0 8          # metriche sui risultati salvati

I risultati grezzi vanno in runs/claude/<tag>.jsonl: se il file esiste nessuna richiesta viene rifatta.
I run di settembre (claude-opus-5, effort high, track 1) sono gia' in runs/claude: per rivalutarli
  uv run python scripts/llm_claude.py evaluate --model claude-opus-5 --effort high --shots 0 8
La chiave API va in `.env` (ANTHROPIC_API_KEY=...), ignorato da git.
"""
from __future__ import annotations

import argparse
import json
import os
import random
import sys
import time
from pathlib import Path

import anthropic
from anthropic.types.message_create_params import MessageCreateParamsNonStreaming
from anthropic.types.messages.batch_create_params import Request
from dotenv import load_dotenv

from dico_nli import data, llm
from dico_nli.decoding import DECODINGS, decode
from dico_nli.labels import LABELS, TRACKS
from dico_nli.metrics import score

ROOT = Path(__file__).resolve().parents[1]
RUNS = ROOT / "runs" / "claude"
# token medi per richiesta osservati a settembre (claude-opus-5, effort high, 0-shot): 773 in, 192 out
OBSERVED_OUT_PER_REQ = 192


def dev_rows(args) -> dict[int, list[dict]]:
    dev = {t: data.load("dev", t) for t in args.tracks}
    if args.sample_pairs:
        pids = sorted({r["pair_id"] for r in dev[args.tracks[0]]})
        keep = set(random.Random(0).sample(pids, args.sample_pairs))
        dev = {t: [r for r in rows if r["pair_id"] in keep] for t, rows in dev.items()}
    return dev


def systems_for(args, k: int) -> dict[int, str]:
    return {t: llm.system_prompt(TRACKS[t], llm.pick_shots(data.load("train", t), k)) for t in args.tracks}


def client() -> anthropic.Anthropic:
    load_dotenv(ROOT / ".env")
    if not (os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN")):
        sys.exit(f"Manca ANTHROPIC_API_KEY: scriverla in {ROOT / '.env'}")
    ws = os.environ.get("ANTHROPIC_WORKSPACE_ID")
    return anthropic.Anthropic(default_headers={"anthropic-workspace-id": ws} if ws else None)


def cmd_estimate(args) -> None:
    dev = dev_rows(args)
    rows = [r for t in args.tracks for r in dev[t]]
    for k in args.shots:
        systems = systems_for(args, k)
        # 4 caratteri per token, +35% per il tokenizer dei modelli recenti
        tin = sum(int((len(systems[r["track"]]) + len(llm.item(r))) / 4 * 1.35) + 20 for r in rows)
        tout = OBSERVED_OUT_PER_REQ * len(rows)
        print(f"== {k}-shot: {len(rows)} richieste, ~{tin:,} token in, ~{tout:,} out (stima), "
              f"prompt {llm.prompt_hash(systems[args.tracks[0]])}")
        print(f"   costo batch stimato con {args.model}: {llm.cost(tin, tout, args.model):.2f} dollari "
              f"(x2 se il ragionamento raddoppia l'uscita)")
        if args.show:
            print("--- system\n" + systems[args.tracks[0]] + "\n--- user\n" + llm.item(rows[0]) + "\n")


def run_batch(c: anthropic.Anthropic, requests: list[Request], name: str) -> None:
    out, id_file = RUNS / f"{name}.jsonl", RUNS / f"{name}.batch_id"
    if out.exists():
        print(f"  {out.name} esiste gia': nessuna nuova richiesta")
        return
    RUNS.mkdir(parents=True, exist_ok=True)
    if id_file.exists():
        batch_id = id_file.read_text().strip()
        print(f"  riprendo il batch {batch_id}")
    else:
        batch_id = c.messages.batches.create(requests=requests).id
        id_file.write_text(batch_id)
        print(f"  batch {batch_id} inviato ({len(requests)} richieste)")
    while (b := c.messages.batches.retrieve(batch_id)).processing_status != "ended":
        n = b.request_counts
        print(f"  in corso: {n.processing} da elaborare, {n.succeeded} completate")
        time.sleep(30)
    recs = []
    for res in c.messages.batches.results(batch_id):
        rec = {"id": res.custom_id, "type": res.result.type}
        if res.result.type == "succeeded":
            m = res.result.message
            rec |= {"stop_reason": m.stop_reason,
                    "text": next((bl.text for bl in m.content if bl.type == "text"), ""),
                    "input_tokens": m.usage.input_tokens, "output_tokens": m.usage.output_tokens}
        recs.append(rec)
    out.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in recs), encoding="utf-8")
    id_file.unlink()


def cmd_run(args) -> None:
    if not args.confirm:
        sys.exit("Le chiamate costano: aggiungere --confirm (prima guardare `estimate`).")
    c = client()
    dev = dev_rows(args)
    rows = [r for t in args.tracks for r in dev[t]]
    for k in args.shots:
        systems = systems_for(args, k)
        name = llm.tag(args.model, args.effort, k, args.tracks, args.sample_pairs)
        reqs = [Request(custom_id=r["instance_id"], params=MessageCreateParamsNonStreaming(
            **llm.request_params(r, systems[r["track"]], args.model, args.effort))) for r in rows]
        meta = {"model": args.model, "effort": args.effort, "shots": k, "tracks": args.tracks,
                "sample_pairs": args.sample_pairs, "prompt_hash": llm.prompt_hash(systems[args.tracks[0]]),
                "data_revision": data.revision()}
        RUNS.mkdir(parents=True, exist_ok=True)
        (RUNS / f"{name}.config.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
        print(f"== {name}")
        run_batch(c, reqs, name)


def cmd_evaluate(args) -> None:
    dev = dev_rows(args)
    rows = [r for t in args.tracks for r in dev[t]]
    ids = [r["instance_id"] for r in rows]
    report = {}
    for k in args.shots:
        name = llm.tag(args.model, args.effort, k, args.tracks, args.sample_pairs)
        path = RUNS / f"{name}.jsonl"
        if not path.exists():
            print(f"== {name}: risultati assenti ({path})")
            continue
        raw = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
        labels, logp, missing = llm.parse(raw)
        tin = sum(r.get("input_tokens", 0) for r in raw)
        tout = sum(r.get("output_tokens", 0) for r in raw)
        spent = llm.cost(tin, tout, args.model)
        dist = {l: sum(v == l for v in labels.values()) for l in LABELS}
        print(f"== {name}: {len(raw)} risposte, senza risposta valida {len(missing)}, "
              f"token {tin} in / {tout} out, costo batch {spent:.2f} dollari")
        print(f"   distribuzione etichette: {dist}")
        decs = {"indipendente (etichetta)": labels,
                "indipendente (probabilita')": decode(ids, logp, **DECODINGS["indipendente"]),
                "+ inversione": decode(ids, logp, **DECODINGS["+ inversione"])}
        for dname, pred in decs.items():
            for t in args.tracks:
                m = score(dev[t], pred)
                report[f"{k}-shot | {dname} | {TRACKS[t]}"] = m
                print(f"   {TRACKS[t]} {dname:28} " + "  ".join(f"{a} {v:.3f}" for a, v in m.items()))
        report[f"{k}-shot | meta"] = {"token_in": tin, "token_out": tout, "costo_usd": spent,
                                      "senza_risposta": missing}
    if report:
        out = RUNS / f"metrics_{args.model}_{args.effort}.json"
        out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"Salvato {out}")


def main() -> None:
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--model", default=llm.MODEL, choices=list(llm.PRICES))
    common.add_argument("--effort", default="high", choices=["low", "medium", "high", "xhigh", "max"])
    common.add_argument("--tracks", type=int, nargs="+", default=[1], choices=[1, 2, 3])
    common.add_argument("--shots", type=int, nargs="+", default=[0])
    common.add_argument("--sample-pairs", type=int, default=0, help="solo questo numero di pair_id del dev")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    e = sub.add_parser("estimate", parents=[common], help="costo stimato, nessuna chiamata")
    e.add_argument("--show", action="store_true", help="mostra un prompt")
    r = sub.add_parser("run", parents=[common], help="invia il batch (a pagamento)")
    r.add_argument("--confirm", action="store_true", help="obbligatorio: conferma la spesa")
    sub.add_parser("evaluate", parents=[common], help="metriche sui risultati salvati")
    args = ap.parse_args()
    {"estimate": cmd_estimate, "run": cmd_run, "evaluate": cmd_evaluate}[args.cmd](args)


if __name__ == "__main__":
    main()
