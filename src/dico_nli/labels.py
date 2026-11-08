"""Etichette, mappa di inversione e track."""
from __future__ import annotations

EQ = "EQUIVALENCE"
FE = "FORWARD_ENTAILMENT"
BE = "BACKWARD_ENTAILMENT"
NO = "NEGATIVE_OTHER"

# stesso ordine dello scorer ufficiale (evaluation_functions/labels.py) e degli script di settembre
LABELS = (EQ, FE, BE, NO)

# r: EQ -> EQ, FE -> BE, BE -> FE; NO non ha inversa nelle metriche ufficiali
REV = {EQ: EQ, FE: BE, BE: FE}

TRACKS = {1: "en", 2: "es", 3: "eu", 4: "mixed"}
LANG_NAMES = {"en": "English", "es": "Spanish", "eu": "Basque"}


def is_consistent(a: str, b: str) -> bool:
    """Coppia di predizioni (originale, invertita) coerente secondo SoftCons: (NO, NO) NON lo e'."""
    return a in REV and b == REV[a]
