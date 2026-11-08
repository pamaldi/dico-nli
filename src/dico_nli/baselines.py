"""Baseline senza apprendimento e misura dell'artefatto strutturale su NEGATIVE_OTHER."""
from __future__ import annotations

import collections

from .labels import BE, EQ, FE, NO
from .metrics import score


def length_rule(r: dict) -> str:
    """Il testo piu' lungo (in parole) implica il piu' corto; a parita', equivalenza."""
    a, b = len(r["text1"].split()), len(r["text2"].split())
    return FE if a > b else BE if b > a else EQ


def structure_report(rows: list[dict]) -> dict:
    """Quanto NEGATIVE_OTHER e' deducibile dalla sola struttura del file, senza leggere il testo."""
    by_pid = collections.Counter(r["pair_id"] for r in rows)
    texts = {(r["text1"], r["text2"]) for r in rows}
    is_no = [r["label"] == NO for r in rows]
    return {
        "n": len(rows),
        "NEGATIVE_OTHER": sum(is_no),
        "acc_pair_id_singolo": sum((by_pid[r["pair_id"]] == 1) == y
                                   for r, y in zip(rows, is_no, strict=True)) / len(rows),
        # senza pair_id: nel file manca la coppia con i testi scambiati?
        "acc_testi_scambiati_assenti": sum(((r["text2"], r["text1"]) not in texts) == y
                                           for r, y in zip(rows, is_no, strict=True)) / len(rows),
    }


def rule_predictions(rows: list[dict]) -> dict[str, dict[str, str]]:
    by_pid = collections.Counter(r["pair_id"] for r in rows)
    return {
        "costante EQUIVALENCE": {r["instance_id"]: EQ for r in rows},
        "regola lunghezza": {r["instance_id"]: length_rule(r) for r in rows},
        "regola lunghezza + struttura": {
            r["instance_id"]: NO if by_pid[r["pair_id"]] == 1 else length_rule(r) for r in rows},
    }


def rule_baselines(rows: list[dict]) -> dict[str, dict[str, float]]:
    """Valide per i track 1-3 (nel 4 ogni pair_id compare in piu' combinazioni di lingue)."""
    return {name: score(rows, pred) for name, pred in rule_predictions(rows).items()}
