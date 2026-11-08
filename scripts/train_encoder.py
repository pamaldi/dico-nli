"""Encoder fine-tuned sui track 1-3 uniti, valutato sul dev con tutte le decodifiche.

Uso:
  uv run --group ml python scripts/train_encoder.py                         # mdeberta-v3-base, 3 seed
  uv run --group ml python scripts/train_encoder.py --seeds 13              # un seed (circa 3 minuti)
  uv run --group ml python scripts/train_encoder.py --model microsoft/deberta-v3-large --batch 16

Le log-probabilita' sul dev vanno in runs/encoder/<modello>_seed<N>.json (si possono ridecodificare
senza riaddestrare); il riepilogo in runs/encoder/<modello>_results.json.
"""
from __future__ import annotations

import argparse
import collections
import json
import statistics
from pathlib import Path

from dico_nli import data
from dico_nli.decoding import DECODINGS, decode
from dico_nli.encoder import train_and_predict
from dico_nli.labels import TRACKS
from dico_nli.metrics import score

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "runs" / "encoder"


def fmt(v: list[float]) -> str:
    return f"{statistics.mean(v):.3f}" + (f" ± {statistics.stdev(v):.3f}" if len(v) > 1 else "")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--model", default="microsoft/mdeberta-v3-base")
    ap.add_argument("--seeds", type=int, nargs="+", default=[13, 42, 2027])
    ap.add_argument("--epochs", type=int, default=5)
    ap.add_argument("--lr", type=float, default=3e-5)
    ap.add_argument("--batch", type=int, default=32)
    ap.add_argument("--download", action="store_true", help="consente di scaricare il modello da HF")
    args = ap.parse_args()

    tracks = (1, 2, 3)
    train = [r for t in tracks for r in data.load("train", t)]
    dev = {t: data.load("dev", t) for t in tracks}
    all_dev = [r for t in tracks for r in dev[t]]
    ids = [r["instance_id"] for r in all_dev]
    OUT.mkdir(parents=True, exist_ok=True)
    tag = args.model.split("/")[-1]
    res: dict = collections.defaultdict(lambda: collections.defaultdict(list))

    for seed in args.seeds:
        cache = OUT / f"{tag}_seed{seed}.json"
        if cache.exists():
            logp = json.loads(cache.read_text(encoding="utf-8"))
            print(f"seed {seed}: log-probabilita' gia' presenti in {cache.name}")
        else:
            logp = train_and_predict(train, all_dev, seed, model_name=args.model, epochs=args.epochs,
                                     lr=args.lr, batch=args.batch, local_only=not args.download)
            cache.write_text(json.dumps(logp), encoding="utf-8")
            print(f"seed {seed} completato")
        for name, cfg in DECODINGS.items():
            pred = decode(ids, logp, **cfg)
            for t in tracks:
                for k, v in score(dev[t], pred).items():
                    res[(name, TRACKS[t])][k].append(v)

    print(f"== {args.model}, train t1+t2+t3, {len(args.seeds)} seed (media ± dev. std.)")
    summary: dict = {}
    for (name, lang), m in res.items():
        summary.setdefault(name, {})[lang] = {
            k: {"media": statistics.mean(v), "valori": v} for k, v in m.items()}
        print(f"  {lang} {name:42} " + "  ".join(f"{k} {fmt(v)}" for k, v in m.items()))
    summary["config"] = vars(args) | {"data_revision": data.revision()}
    (OUT / f"{tag}_results.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False),
                                             encoding="utf-8")


if __name__ == "__main__":
    main()
