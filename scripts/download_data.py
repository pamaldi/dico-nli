"""Scarica train/dev e lo scorer ufficiale dal repository degli organizzatori, a una revisione fissata.

Uso:  uv run python scripts/download_data.py [--revision SHA]

Scrive data/raw/final_data/{train,dev}/*.csv, data/raw/evaluation_functions/*.py e data/raw/REVISION.txt.
Il repository e' GPL-3.0; i dati restano fuori da git e si riscaricano da qui.
"""
from __future__ import annotations

import argparse
import json
import urllib.request
from pathlib import Path

REPO = "ilopezgazpio/SemEval-2027-Task-2-DiCo-NLI"
API = f"https://api.github.com/repos/{REPO}"
DEST = Path(__file__).resolve().parents[1] / "data" / "raw"
# ultimo commit al 8 novembre 2026 ("codabench alive", 8 settembre 2026)
DEFAULT_REVISION = "588968e610"


def get_json(url: str):
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json",
                                               "User-Agent": "dico-nli-download"})
    with urllib.request.urlopen(req) as r:
        return json.load(r)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--revision", default=DEFAULT_REVISION, help="SHA (anche abbreviato) o 'main'")
    args = ap.parse_args()
    sha = get_json(f"{API}/commits/{args.revision}")["sha"]
    tree = get_json(f"{API}/git/trees/{sha}?recursive=1")["tree"]
    wanted = [t["path"] for t in tree if t["type"] == "blob" and (
        (t["path"].startswith("final_data/") and t["path"].endswith(".csv"))
        or (t["path"].startswith("evaluation_functions/") and t["path"].endswith(".py")))]
    for p in wanted:
        out = DEST / p
        out.parent.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(f"https://raw.githubusercontent.com/{REPO}/{sha}/{p}", out)
    (DEST / "REVISION.txt").write_text(f"{REPO}\n{sha}\n", encoding="utf-8")
    print(f"Scaricati {len(wanted)} file di {REPO} @ {sha[:10]} in {DEST}")


if __name__ == "__main__":
    main()
