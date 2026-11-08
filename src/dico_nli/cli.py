"""Comando `dico-nli`: statistiche, artefatto, baseline senza apprendimento, scoring di un file."""
from __future__ import annotations

import collections
import csv
from pathlib import Path

import typer
from rich import print
from rich.table import Table

from . import data
from .baselines import rule_baselines, structure_report
from .labels import LABELS, TRACKS
from .metrics import score

app = typer.Typer(help="SemEval 2027 Task 2 - DiCo-NLI")


@app.command()
def stats() -> None:
    """Dimensioni e distribuzione delle etichette per split e track."""
    print(f"Revisione dati: {data.revision()}")
    t = Table()
    for c in ("split", "track", "istanze", "coppie reversibili", "EQ", "FE", "BE", "NO"):
        t.add_column(c)
    for split in data.SPLITS:
        for track, lang in TRACKS.items():
            rows = data.load(split, track)
            c = collections.Counter(r["label"] for r in rows)
            nrev = sum(bool(r["reverse_pair_id"]) for r in rows) // 2
            t.add_row(split, f"{track} ({lang})", str(len(rows)), str(nrev), *(str(c[k]) for k in LABELS))
    print(t)


@app.command()
def artifact() -> None:
    """Quanto NEGATIVE_OTHER si riconosce dalla sola struttura del file (track 1-3)."""
    for split in data.SPLITS:
        for track in (1, 2, 3):
            print(split, TRACKS[track], structure_report(data.load(split, track)))


@app.command()
def baselines() -> None:
    """Baseline senza apprendimento sul dev (attese en: wF1 0,110 / 0,467 / 0,667)."""
    for track in (1, 2, 3):
        for name, m in rule_baselines(data.load("dev", track)).items():
            print(f"{TRACKS[track]} {name:30} " + "  ".join(f"{k} {v:.3f}" for k, v in m.items()))


@app.command("score")
def score_file(predictions: Path, split: str = "dev", track: int = 1) -> None:
    """Punteggi di un file `instance_id,label` contro il reference locale."""
    rows = data.load(split, track)
    with predictions.open(encoding="utf-8", newline="") as f:
        pred = {r["instance_id"]: r["label"] for r in csv.DictReader(f)}
    missing = [r["instance_id"] for r in rows if r["instance_id"] not in pred]
    if missing:
        print(f"[red]{len(missing)} istanze senza predizione, es. {missing[0]}[/red]")
        raise typer.Exit(2)
    print({k: round(v, 4) for k, v in score(rows, pred).items()})


if __name__ == "__main__":
    app()
