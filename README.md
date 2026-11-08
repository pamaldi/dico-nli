# dico-nli

Progetto di lavoro per **SemEval 2027, Task 2 — DiCo-NLI** (*Directional Consistency in Fine-Grained Natural Language Inference*; sul sito SemEval ancora come CoCo-NLI): classificare la relazione di implicazione fra due testi brevi **in entrambi gli ordini**, con risposte corrette e coerenti fra loro. Creato l'8 novembre 2026 dall'archivio `ai-resources` (cartella `lavori/2026-09_semeval-2027`: schede, analisi e script del 22 settembre), con la stessa impostazione di `agent-risk`.

**Stato:** il codice di settembre è portato in un pacchetto con test. Le baseline senza apprendimento e i run di Claude Opus 5 di settembre si riproducono esattamente; lo scorer è verificato contro quello ufficiale. Il repository ufficiale è fermo all'8 settembre. Il 6 novembre un'altra squadra ha chiesto agli organizzatori se l'artefatto su `NEGATIVE_OTHER` e il vincolo cross-lingue sono ammessi ([issue #1](https://github.com/ilopezgazpio/SemEval-2027-Task-2-DiCo-NLI/issues/1), ancora senza risposta). Decisioni aperte in [docs/06](docs/06-decisioni-e-domande-aperte.md).

## Avvio in PyCharm

1. **File → Open** e scegliere `C:\svi\dico-nli`.
2. PyCharm riconosce `pyproject.toml` e `uv.lock`. Se non crea da solo l'interprete: **Settings → Project → Python Interpreter → Add Interpreter → Add Local Interpreter**, tipo **uv**, ambiente esistente `.venv` del progetto.
3. Marcare `src` come *Sources Root* e `tests` come *Test Sources Root*, se PyCharm non lo fa.

Da terminale, nella cartella del progetto:

```bash
uv sync
```

```bash
uv run python scripts/download_data.py
```

```bash
uv run pytest
```

```bash
uv run dico-nli stats
```

```bash
uv run dico-nli baselines
```

`uv sync` crea `.venv`; `download_data.py` scarica train, dev e lo scorer ufficiale in `data/raw` alla revisione fissata (`588968e610`); `pytest` esegue 16 test; gli ultimi due comandi stampano le statistiche dei quattro track e le baseline senza apprendimento sul dev.

Encoder (GPU, gruppo `ml`) e Claude (a pagamento, solo con `--confirm`):

```bash
uv run --group ml python scripts/train_encoder.py --seeds 13
```

```bash
uv run python scripts/llm_claude.py estimate --shots 0 8
```

## Contenuto

| Percorso | Che cosa |
|---|---|
| [docs/](docs/) | documentazione: task, dati, vincoli simbolici, risultati, ambiente, decisioni, test e indicatori |
| `data/raw/` | dati ufficiali (4 track, train e dev) e scorer `evaluation_functions`, revisione in `data/raw/REVISION.txt`. **Non versionato**: si riscarica |
| `src/dico_nli/labels.py` | etichette, mappa di inversione, track |
| `src/dico_nli/data.py` | caricamento, struttura degli identificativi, coppia invertita, file di sottomissione |
| `src/dico_nli/metrics.py` | F1 pesato, SoftCons, HardCons (verificate contro lo scorer ufficiale) |
| `src/dico_nli/baselines.py` | costante, regola di lunghezza, misura dell'artefatto `NEGATIVE_OTHER` |
| `src/dico_nli/decoding.py` | decodifica vincolata: inversione, cross-lingue, artefatto |
| `src/dico_nli/encoder.py` | fine-tuning di un encoder (mdeberta-v3-base di default); richiede `--group ml` |
| `src/dico_nli/llm.py` | baseline con Claude: prompt (identico a settembre), schema, parametri, lettura delle risposte |
| `scripts/` | `download_data.py`, `train_encoder.py`, `llm_claude.py` (estimate / run `--confirm` / evaluate) |
| `results/2026-09-22/` | riepiloghi JSON degli esperimenti di settembre, copiati da `ai-resources` |
| `runs/` | predizioni, risposte grezze dell'API, log-probabilità (ignorata da git; contiene i run Claude di settembre) |
| `notebooks/` | esplorazione (vuota) |

La chiave API va in `.env` (modello in `.env.example`); il file è ignorato da git.
