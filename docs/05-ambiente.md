# 05 — Ambiente

## Gestione con uv

- Python 3.12 (`.python-version`), pacchetto `dico-nli` in layout `src/`, build con `uv_build`.
- `uv sync` installa le dipendenze di base e il gruppo `dev`. `uv sync --group ml` aggiunge torch e transformers; eseguire con `uv run --group ml ...`, perché un `uv sync` senza il gruppo li rimuove.
- Comando installato: `dico-nli` (`stats`, `artifact`, `baselines`, `score`), in `src/dico_nli/cli.py`.
- Se la shell ha ancora attivo l'ambiente di `agent-risk` (`VIRTUAL_ENV=...agent-risk\.venv`), uv lo ignora e avvisa; chiudere il terminale o `deactivate`.

## Librerie

| Libreria | Uso |
|---|---|
| `pandas`, `numpy`, `scikit-learn`, `scipy` | analisi, eventuali classificatori classici |
| `anthropic`, `tenacity`, `python-dotenv` | Claude via Message Batches API, chiave in `.env` |
| `typer`, `rich`, `tqdm`, `pyyaml`, `pydantic` | riga di comando, tabelle, configurazioni |
| `pytest`, `ruff`, `jupyterlab`, `matplotlib`, `seaborn` | test, lint, esplorazione |
| gruppo `ml`: `torch` (CUDA 12.6), `transformers`, `accelerate`, `sentencepiece`, `protobuf`, `peft` | fine-tuning degli encoder, LoRA per LLM piccoli |

Rispetto ad `agent-risk` mancano `clingo` (il vincolo di inversione è una scelta fra quattro combinazioni, non serve un solutore) e `datasets`/`huggingface-hub` (i dati stanno su GitHub, non su Hugging Face).

## GPU

RTX 4060 Laptop, 8 GB. Verificato l'8 novembre 2026: torch 2.14.1+cu126 vede la GPU, transformers 5.22.2. Il blocco del driver osservato il 7 novembre in `agent-risk` non si è ripresentato.

- mdeberta-v3-base è nella cache di Hugging Face: circa 3 minuti per seed sui track 1–3 uniti (9.126 esempi, 5 epoche, frasi brevi, max 64 token).
- Modelli non in cache (DeBERTa-v3-large, XLM-R large): `train_encoder.py --download`.
- **Trappola di transformers 5** (8 novembre 2026): `from_pretrained` carica i pesi nel dtype del checkpoint, float16 per mdeberta-v3-base. Lo script di settembre, eseguito con transformers 5.22, addestrava pesi float16 con AdamW senza scaling: tutte le log-probabilità NaN, e il modello predice sempre EQUIVALENCE (wF1 0,110). `encoder.py` ora passa `dtype=torch.float32`; il bf16 resta solo nell'autocast.
- All'avvio transformers avvisa di un «incorrect regex pattern» e suggerisce `fix_mistral_regex=True`: per il tokenizer SentencePiece di mdeberta l'avviso sembra spurio (gli id dei token sono plausibili), ma non è verificato a fondo.

## Costi delle API

- Settembre, `claude-opus-5`, effort high, Batches API: 2,86 dollari per lo zero-shot e 2,85 per l'8-shot sul dev inglese (660 richieste), 0,22 per il pilota; in totale 5,93.
- `llm_claude.py estimate` stima per Claude Opus 5.5 (4/20 dollari per milione di token, metà con le batch) circa 1,6–1,8 dollari per variante, da raddoppiare se il ragionamento allunga l'uscita.
- **Nessuna chiamata parte senza `run --confirm`**; i risultati grezzi restano in `runs/claude/` e non si ripagano.
- La Batches API non accetta il parametro `fallbacks` (ripiego automatico in caso di rifiuto): un rifiuto viene contato come "senza risposta valida". A settembre non ce ne sono stati.

## Dati e riproducibilità

- `data/raw/` ignorata da git; `scripts/download_data.py --revision SHA` la ricostruisce (default `588968e610`) e scrive `REVISION.txt`.
- `runs/` ignorata: risposte API (`runs/claude/`), log-probabilità dell'encoder per seed (`runs/encoder/`), da cui si ridecodifica senza riaddestrare.
- `results/2026-09-22/` versionata: riepiloghi degli esperimenti di settembre.

## Verifiche dell'8 novembre 2026

- `uv run pytest`: 16 test passati, incluso il confronto con lo scorer ufficiale.
- `uv run dico-nli baselines`: identico a settembre.
- `llm_claude.py evaluate --model claude-opus-5 --effort high --shots 0 8`: identico a settembre (riletti i file grezzi, nessuna spesa).
- `ruff check`: nessun avviso.
