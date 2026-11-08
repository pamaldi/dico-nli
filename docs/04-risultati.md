# 04 — Risultati

## Termini usati

| Termine | Definizione |
|---|---|
| **wF1, SoftCons, HardCons** | vedi [01](01-task.md) e [07](07-test-e-indicatori.md) |
| **seed** | seme casuale dell'addestramento; si riportano media ± deviazione standard su più seed |
| **zero-shot / 8-shot** | il prompt non contiene esempi / ne contiene 8 (2 per etichetta) presi dal train |
| **struttura / artefatto** | uso del fatto che le istanze senza inversa sono NO (vedi [02](02-dati.md)) |

Tutti i risultati sono sul **dev** (660 istanze e 277 coppie reversibili per lingua). Sono indicazioni per il piano, non risultati da pubblicare: un solo modello per famiglia, iperparametri non ottimizzati.

## 22 settembre 2026 — baseline e mdeberta

mdeberta-v3-base addestrato sui train dei track 1–3 uniti; 5 epoche, learning rate 3·10⁻⁵, batch 32, iperparametri fissati a priori; seed 13, 42, 2027. Riepilogo in `results/2026-09-22/mdeberta_e_regole.json`.

| Sistema | Lingua | wF1 | SoftCons | HardCons |
|---|---|---:|---:|---:|
| Costante EQ | tutte | 0,110 | 1,000 | 0,314 |
| Regola di lunghezza | en / es / eu | 0,467 / 0,482 / 0,444 | 1,000 | 0,614 / 0,639 / 0,574 |
| Regola di lunghezza + struttura | en / es / eu | 0,667 / 0,687 / 0,645 | 1,000 | 0,614 / 0,639 / 0,574 |
| mdeberta, indipendente | en | 0,828 ± 0,001 | 0,874 ± 0,011 | 0,835 ± 0,013 |
| | es | 0,786 ± 0,008 | 0,848 ± 0,010 | 0,787 ± 0,006 |
| | eu | 0,771 ± 0,005 | 0,848 ± 0,019 | 0,781 ± 0,006 |
| + inversione | en | 0,831 ± 0,002 | 0,917 ± 0,004 | 0,863 ± 0,006 |
| | es | 0,784 ± 0,004 | 0,905 ± 0,011 | 0,819 ± 0,010 |
| | eu | 0,776 ± 0,012 | 0,893 ± 0,004 | 0,813 ± 0,015 |
| + cross-lingue | tutte | 0,826 ± 0,006 | 0,875 ± 0,004 | 0,838 ± 0,000 |
| + inversione + cross-lingue | tutte | 0,832 ± 0,004 | 0,909 ± 0,013 | **0,865 ± 0,002** |
| + inversione + cross-lingue + artefatto | tutte | 0,934 ± 0,011 | 1,000 | 0,922 ± 0,013 |

Con il vincolo cross-lingue le tre lingue ricevono le stesse etichette, quindi i punteggi coincidono.

**Lettura.**

1. **L'inversione migliora la correttezza di coppia, non quella della singola istanza** (H1): HardCons +2,8–3,2 punti in tutte le lingue, wF1 invariata entro la variabilità fra seed.
2. **Il cross-lingue trasferisce informazione verso il basco** (H2): wF1 da 0,771 a 0,826, HardCons da 0,781 a 0,838; per l'inglese non cambia nulla. I due vincoli si sommano: 0,865 di HardCons in ogni lingua.
3. **SoftCons resta sotto 1 anche con l'inversione:** fra l'8% e l'11% delle coppie viene decodificato (NO, NO). La distinzione fra NO e le relazioni direzionali è l'errore principale del modello.
4. **L'artefatto vale circa 10 punti di wF1** e 5,7 di HardCons.

## 22 settembre 2026 — Claude Opus 5 sul dev inglese

`claude-opus-5`, effort high, ragionamento adattivo, Batches API; una richiesta per istanza (il modello non vede mai l'inversa); output strutturato con etichetta e probabilità dichiarate. Riepilogo in `results/2026-09-22/claude-opus-5_high.json`, risposte grezze in `runs/claude/`.

| Sistema | wF1 | SoftCons | HardCons |
|---|---:|---:|---:|
| Claude Opus 5, zero-shot | 0,665 | 0,812 | 0,639 |
| zero-shot + inversione | 0,662 | 0,899 | 0,682 |
| Claude Opus 5, 8-shot | 0,667 | 0,679 | 0,574 |
| 8-shot + inversione | 0,672 | 0,805 | 0,653 |
| *per confronto:* mdeberta + inversione | 0,831 | 0,917 | 0,863 |

Costo reale 5,93 dollari in tutto; nessun rifiuto, nessuna risposta malformata.

**Lettura.**

- Con un semplice prompt un LLM di frontiera vale, in wF1, quanto la regola di lunghezza con la struttura, ed è 16 punti sotto un encoder da 280 milioni di parametri addestrato in 3 minuti.
- **Il vincolo aiuta anche sopra un LLM:** +4 punti di HardCons nello zero-shot, +8 nell'8-shot.
- **Il pilota era ottimista:** su 30 coppie la coerenza era 0,957, sul dev completo 0,812.
- **L'8-shot sposta il problema:** la F1 su EQ sale (0,60 → 0,68), ma le predizioni NO salgono da 110 a 183 (106 nel gold), probabilmente perché gli esempi bilanciati danno a NO il 25% contro il 16% dei dati.
- Molti errori sono convenzioni di annotazione (preposizioni, quasi-sinonimi), vedi [02](02-dati.md).

Limiti: un prompt, una selezione di esempi, un livello di effort; probabilità dichiarate, non log-probabilità; possibile contaminazione (PhrasIS pubblico dal 2024).

## 8 novembre 2026 — verifica di riproduzione

Con il codice di questo progetto:

- **Baseline senza apprendimento:** identiche nelle tre lingue (test automatico per l'inglese).
- **Claude Opus 5:** rileggendo le risposte grezze di settembre con `llm_claude.py evaluate --model claude-opus-5 --effort high --shots 0 8`, tutti i numeri della tabella sopra coincidono alla terza cifra, anche il pilota (wF1 0,715, SoftCons 0,957). Nessuna spesa.
- **mdeberta:** un seed (13) con **batch 16** invece di 32: con pesi float32 e batch 32 la memoria della GPU si riempiva e il driver passava alla RAM di sistema, rendendo l'addestramento lentissimo. 10 minuti e mezzo invece dei 3 di settembre. Il primo tentativo, con transformers 5 e senza la correzione del dtype, era andato in NaN ([05](05-ambiente.md)). Numeri vicini a quelli di settembre, entro la variabilità fra seed, ma non identici, perché il batch è diverso:

| Decodifica | Lingua | wF1 8 nov (seed 13, batch 16) | wF1 sett. (3 seed) | HardCons 8 nov | HardCons sett. |
|---|---|---:|---:|---:|---:|
| indipendente | en | 0,834 | 0,828 ± 0,001 | 0,845 | 0,835 ± 0,013 |
| | eu | 0,778 | 0,771 ± 0,005 | 0,780 | 0,781 ± 0,006 |
| + inversione | en | 0,837 | 0,831 ± 0,002 | 0,859 | 0,863 ± 0,006 |
| | eu | 0,769 | 0,776 ± 0,012 | 0,794 | 0,813 ± 0,015 |
| + inversione + cross-lingue | tutte | 0,832 | 0,832 ± 0,004 | 0,863 | 0,865 ± 0,002 |
| + … + artefatto | tutte | 0,936 | 0,934 ± 0,011 | 0,924 | 0,922 ± 0,013 |

Le conclusioni di settembre reggono: l'inversione alza HardCons, e il cross-lingue porta il basco al livello dell'inglese. Per una riproduzione esatta servirebbe un batch effettivo di 32 (accumulo del gradiente su 2 passi da 16), non ancora implementato. Log in `runs/encoder/train_seed13_b16.log`.
