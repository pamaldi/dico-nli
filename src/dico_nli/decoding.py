"""Decodifica sotto vincoli: dalle log-probabilita' per istanza alle etichette.

Il modello classifica ogni istanza da sola. Qui si impongono a posteriori:
- inversione: le due direzioni della stessa coppia ricevono (l, r(l)) con l in {EQ, FE, BE}, oppure
  (NO, NO); si sceglie l'opzione con somma di log-probabilita' massima;
- cross-lingue: la stessa coppia e direzione riceve la stessa etichetta in tutte le lingue presenti
  (si sommano le log-probabilita' delle traduzioni);
- artefatto: un'istanza senza inversa nel file e' NO, e alle coppie reversibili NO non si assegna.
  Sfrutta la struttura del file, non il testo: va sempre riportato a parte.

Rispetto a analisi/dico_nli_esperimento.py di settembre la coppia si ricava da `reverse_id`, quindi
funziona anche per il track 4 (lingue diverse nei due testi).
"""
from __future__ import annotations

import collections

from .data import parse_id, reverse_id
from .labels import LABELS, NO, REV

IDX = {l: i for i, l in enumerate(LABELS)}

DECODINGS = {
    "indipendente": dict(inversion=False, crossling=False, leak=False),
    "+ inversione": dict(inversion=True, crossling=False, leak=False),
    "+ cross-lingue": dict(inversion=False, crossling=True, leak=False),
    "+ inversione + cross-lingue": dict(inversion=True, crossling=True, leak=False),
    "+ inversione + cross-lingue + artefatto": dict(inversion=True, crossling=True, leak=True),
}


def _unit(iid: str, crossling: bool) -> tuple:
    pid, l1, l2, direction = parse_id(iid)
    return (pid, direction) if crossling else (iid,)


def _reverse_unit(u: tuple, crossling: bool) -> tuple:
    if crossling:
        return (u[0], "flipped" if u[1] == "original" else "original")
    return (reverse_id(u[0]),)


def decode(ids: list[str], logp: dict[str, list[float]], *, inversion: bool = False,
           crossling: bool = False, leak: bool = False) -> dict[str, str]:
    members: dict[tuple, list[str]] = collections.defaultdict(list)
    unit_lp: dict[tuple, list[float]] = {}
    for iid in ids:
        u = _unit(iid, crossling)
        members[u].append(iid)
        lp = logp[iid]
        unit_lp[u] = [a + b for a, b in zip(unit_lp[u], lp, strict=True)] if u in unit_lp else list(lp)

    choice: dict[tuple, str] = {}
    for u, lp in unit_lp.items():
        if u in choice:
            continue
        ru = _reverse_unit(u, crossling)
        has_rev = ru in unit_lp
        if inversion and has_rev:
            options = [(l, REV[l]) for l in REV] + ([] if leak else [(NO, NO)])
            a, b = max(options, key=lambda o: lp[IDX[o[0]]] + unit_lp[ru][IDX[o[1]]])
            choice[u], choice[ru] = a, b
        elif leak and not has_rev:
            choice[u] = NO
        else:
            allowed = LABELS[:3] if leak else LABELS
            choice[u] = max(allowed, key=lambda l: lp[IDX[l]])
    return {iid: choice[u] for u, iids in members.items() for iid in iids}
