"""Caricamento dei file ufficiali e struttura degli identificativi.

instance_id = <pair_id>__<lingua1>-<lingua2>__<original|flipped>
La coppia invertita di `pid__a-b__original` e' `pid__b-a__flipped` (e viceversa): vale anche nel track 4,
dove le lingue dei due testi sono diverse.
"""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"
SPLITS = ("train", "dev")
KINDS = ("reference", "participant_labeled", "submission_template")


def path(split: str, track: int, kind: str = "reference", raw: Path = RAW) -> Path:
    return raw / "final_data" / split / f"dico_nli_{split}_track{track}_{kind}.csv"


def parse_id(instance_id: str) -> tuple[str, str, str, str]:
    """(pair_id, lingua del testo 1, lingua del testo 2, direzione)."""
    pid, langs, direction = instance_id.split("__")
    l1, l2 = langs.split("-")
    return pid, l1, l2, direction


def reverse_id(instance_id: str) -> str:
    """Identificativo della coppia invertita, ricavato dal solo identificativo."""
    pid, l1, l2, direction = parse_id(instance_id)
    other = "flipped" if direction == "original" else "original"
    return f"{pid}__{l2}-{l1}__{other}"


def load(split: str, track: int, kind: str = "reference", raw: Path = RAW) -> list[dict]:
    """Righe del file come dizionari, con `direction` e `track` aggiunti."""
    p = path(split, track, kind, raw)
    if not p.exists():
        raise FileNotFoundError(f"{p} mancante: eseguire `uv run python scripts/download_data.py`")
    with p.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        r["direction"] = parse_id(r["instance_id"])[3]
        r["track"] = track
    return rows


def revision(raw: Path = RAW) -> str:
    p = raw / "REVISION.txt"
    return p.read_text(encoding="utf-8").strip().replace("\n", " @ ") if p.exists() else "sconosciuta"


def write_predictions(pred: dict[str, str], out: Path, template: list[dict] | None = None) -> None:
    """File di sottomissione: esattamente le colonne `instance_id,label`, nell'ordine del template."""
    ids = [r["instance_id"] for r in template] if template else sorted(pred)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["instance_id", "label"])
        w.writerows([i, pred[i]] for i in ids)
