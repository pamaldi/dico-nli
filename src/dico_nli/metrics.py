"""Metriche ufficiali: F1 pesato, SoftCons, HardCons.

Reimplementazione di evaluation_functions/metrics.py del repository ufficiale (verificata contro lo
scorer ufficiale in tests/, quando e' stato scaricato). Le coppie reversibili sono le righe con
`reverse_pair_id` non vuoto, contate una volta sola.
"""
from __future__ import annotations

import collections

from .labels import LABELS, is_consistent


def weighted_f1(gold: list[str], pred: list[str]) -> float:
    n = len(gold)
    conf = collections.Counter(zip(gold, pred, strict=True))
    out = 0.0
    for l in LABELS:
        tp = conf[(l, l)]
        support = sum(conf[(l, x)] for x in LABELS)
        npred = sum(conf[(x, l)] for x in LABELS)
        p = tp / npred if npred else 0.0
        r = tp / support if support else 0.0
        out += support / n * (2 * p * r / (p + r) if p + r else 0.0)
    return out


def reversible_pairs(rows: list[dict]) -> list[tuple[str, str]]:
    seen, pairs = set(), []
    for r in rows:
        rev = r.get("reverse_pair_id")
        if not rev:
            continue
        key = frozenset((r["instance_id"], rev))
        if key not in seen:
            seen.add(key)
            pairs.append((r["instance_id"], rev))
    return pairs


def score(rows: list[dict], pred: dict[str, str]) -> dict[str, float]:
    """`rows` dal file reference (servono `label` e `reverse_pair_id`); `pred` da instance_id a etichetta."""
    gold = {r["instance_id"]: r["label"] for r in rows}
    pairs = reversible_pairs(rows)
    soft = sum(is_consistent(pred[a], pred[b]) for a, b in pairs)
    hard = sum(pred[a] == gold[a] and pred[b] == gold[b] for a, b in pairs)
    return {
        "wF1": weighted_f1([r["label"] for r in rows], [pred[r["instance_id"]] for r in rows]),
        "SoftCons": soft / len(pairs),
        "HardCons": hard / len(pairs),
    }
