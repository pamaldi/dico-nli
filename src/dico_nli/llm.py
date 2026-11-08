"""Baseline con Claude via API: prompt, schema di uscita, richieste batch, lettura delle risposte.

L'API non espone le log-probabilita'. Il modello restituisce, in output strutturato, un'etichetta e una
distribuzione di probabilita' dichiarata sulle quattro etichette: l'etichetta alimenta la decodifica
indipendente, la distribuzione quella vincolata (stessa `decode` usata per gli encoder).
Ogni istanza e' una richiesta separata: il modello non vede mai la coppia inversa.

Prompt identico a analisi/dico_nli_claude.py di settembre (ai-resources), cosi' i run di allora
(runs/claude/*.jsonl) restano confrontabili: l'hash del prompt e' registrato in ogni run.
"""
from __future__ import annotations

import hashlib
import json
import math
import random

from .labels import LABELS, LANG_NAMES, NO, TRACKS

MODEL = "claude-opus-5-5"
# dollari per milione di token (ingresso, uscita), prezzi API standard (tabella del 6 ottobre 2026);
# la Batches API costa la meta'
PRICES = {
    "claude-opus-5-5": (4.0, 20.0),
    "claude-opus-5": (5.0, 25.0),
    "claude-sonnet-5-5": (2.0, 10.0),
    "claude-haiku-5-5": (0.10, 0.50),
    "claude-fable-5-1": (10.0, 50.0),
}

INSTRUCTION = """You classify the semantic relation between two short texts.

Options:
EQUIVALENCE: Text 1 and Text 2 mean the same thing.
FORWARD_ENTAILMENT: Text 1 entails Text 2 (Text 1 is more specific; if Text 1 is true, Text 2 is true), \
but not vice versa.
BACKWARD_ENTAILMENT: Text 2 entails Text 1 (Text 2 is more specific; if Text 2 is true, Text 1 is true), \
but not vice versa.
NEGATIVE_OTHER: none of the above (unrelated, contradictory, or only partially overlapping).

Return the label and your probability for each of the four labels (summing to 1)."""

SCHEMA = {
    "type": "object",
    "properties": {
        "label": {"type": "string", "enum": list(LABELS)},
        "probabilities": {"type": "object", "properties": {l: {"type": "number"} for l in LABELS},
                          "required": list(LABELS), "additionalProperties": False},
    },
    "required": ["label", "probabilities"],
    "additionalProperties": False,
}


def item(r: dict) -> str:
    return f"Text 1: {r['text1']}\nText 2: {r['text2']}"


def system_prompt(lang: str, shots: list[dict]) -> str:
    s = INSTRUCTION + f"\nThe texts are in {LANG_NAMES[lang]}."
    if shots:
        s += "\n\nLabelled examples:\n\n" + "\n\n".join(item(x) + f"\nLabel: {x['label']}" for x in shots)
    return s


def pick_shots(train: list[dict], k: int, seed: int = 0) -> list[dict]:
    """k esempi bilanciati per etichetta (k/4 ciascuna), come a settembre."""
    if k == 0:
        return []
    rnd = random.Random(seed)
    per = k // len(LABELS)
    shots = [r for l in LABELS for r in rnd.sample([x for x in train if x["label"] == l], per)]
    rnd.shuffle(shots)
    return shots


def prompt_hash(system: str) -> str:
    return hashlib.sha256((system + json.dumps(SCHEMA, sort_keys=True)).encode()).hexdigest()[:12]


def request_params(r: dict, system: str, model: str, effort: str) -> dict:
    """Parametri di una richiesta Messages (per la Batches API: nessun `fallbacks`, non e' accettato)."""
    return dict(
        model=model,
        max_tokens=16000,
        thinking={"type": "adaptive"},
        output_config={"effort": effort, "format": {"type": "json_schema", "schema": SCHEMA}},
        system=system,
        messages=[{"role": "user", "content": item(r)}],
    )


def parse(raw: list[dict]) -> tuple[dict[str, str], dict[str, list[float]], list[str]]:
    """Etichette dichiarate, log-probabilita' normalizzate e istanze senza risposta valida.

    Rifiuti, troncamenti ed errori ricevono NO e distribuzione uniforme, e sono contati a parte.
    """
    labels, logp, missing = {}, {}, []
    for rec in raw:
        try:
            if rec["type"] != "succeeded" or rec["stop_reason"] != "end_turn":
                raise ValueError(rec.get("stop_reason") or rec["type"])
            d = json.loads(rec["text"])
            p = [max(float(d["probabilities"][l]), 1e-4) for l in LABELS]
            if d["label"] not in LABELS:
                raise ValueError(d["label"])
            labels[rec["id"]] = d["label"]
            logp[rec["id"]] = [math.log(x / sum(p)) for x in p]
        except (KeyError, ValueError, TypeError):
            missing.append(rec["id"])
            labels[rec["id"]] = NO
            logp[rec["id"]] = [math.log(1 / len(LABELS))] * len(LABELS)
    return labels, logp, missing


def cost(tokens_in: int, tokens_out: int, model: str, batch: bool = True) -> float:
    pin, pout = PRICES.get(model, (math.nan, math.nan))
    return (tokens_in * pin + tokens_out * pout) / 1e6 * (0.5 if batch else 1.0)


def tag(model: str, effort: str, shots: int, tracks: list[int], sample_pairs: int = 0) -> str:
    """Nome del run, compatibile con i file di settembre (es. claude-opus-5_high_0shot_t1)."""
    t = f"{model}_{effort}_{shots}shot_t{''.join(map(str, tracks))}"
    return t + (f"_sample{sample_pairs}" if sample_pairs else "")


__all__ = ["MODEL", "PRICES", "INSTRUCTION", "SCHEMA", "TRACKS", "item", "system_prompt", "pick_shots",
           "prompt_hash", "request_params", "parse", "cost", "tag"]
