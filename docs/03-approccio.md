# 03 — Approccio: classificatore neurale + vincoli simbolici

## Termini usati

| Termine | Definizione |
|---|---|
| **log-probabilità** | logaritmo della probabilità che il modello assegna a ogni etichetta; sommarle equivale a moltiplicare le probabilità |
| **decodifica vincolata** | scelta delle etichette che massimizza la probabilità congiunta **fra le sole combinazioni ammesse** dal vincolo |
| **decodifica indipendente** | ogni istanza riceve la sua etichetta più probabile, senza guardare le altre |
| **encoder** | modello tipo BERT (qui mdeberta-v3-base, multilingue) addestrato a classificare la coppia di testi |

## Domanda di ricerca

Quanto della consistenza ottenibile è **garantito** dal vincolo simbolico e quanto è **correttezza appresa**? In quali condizioni imporre il vincolo migliora anche la correttezza (wF1, HardCons) invece di rendere solo coerenti gli errori?

## Ipotesi

- **H1.** La decodifica congiunta sulla coppia migliora HardCons, perché combina due stime indipendenti della stessa relazione.
- **H2.** Il vincolo cross-lingue (stessa etichetta nelle tre traduzioni) aiuta soprattutto il basco, lingua con meno risorse.
- **H3.** I guadagni di HardCons si concentrano sulle coppie in cui la regola di lunghezza fallisce.

H1 e H2 hanno già indicazioni positive sul dev ([04](04-risultati.md)); H3 non è stata misurata.

## I vincoli (`src/dico_nli/decoding.py`)

Il modello classifica le due direzioni **separatamente**. Il vincolo di inversione sceglie, fra (EQ, EQ), (FE, BE), (BE, FE) e (NO, NO), la combinazione con somma di log-probabilità massima.

Esempio numerico (verificato da un test):

| | EQ | FE | BE | NO |
|---|---|---|---|---|
| originale (*shrine* → *war shrine*) | 0,30 | 0,10 | **0,55** | 0,05 |
| invertita (*war shrine* → *shrine*) | **0,50** | 0,40 | 0,05 | 0,05 |

Indipendente: (BE, EQ), incoerente. Vincolata:

| Combinazione | Punteggio |
|---|---|
| (EQ, EQ) | 0,30 × 0,50 = 0,150 |
| **(BE, FE)** | **0,55 × 0,40 = 0,220** |
| (FE, BE) | 0,10 × 0,05 = 0,005 |
| (NO, NO) | 0,05 × 0,05 = 0,0025 |

Vince (BE, FE): la direzione più sicura trascina l'altra.

| Variante | Che cosa fa | Uso |
|---|---|---|
| `indipendente` | argmax per istanza | riferimento |
| `+ inversione` | la coppia riceve (l, r(l)) o (NO, NO) | metodo |
| `+ cross-lingue` | somma le log-probabilità delle traduzioni della stessa coppia e direzione | metodo, da confermare ammesso (issue #1) |
| `+ inversione + cross-lingue` | entrambi | metodo |
| `+ … + artefatto` | istanza senza inversa ⇒ NO; alle coppie reversibili NO non si assegna | **solo misura dell'artefatto**, riportata a parte |

**Che cosa il vincolo non fa.** Non aggiunge conoscenza: usa le probabilità che il modello ha già. Può peggiorare: se il modello è più sicuro sulla direzione sbagliata, trascina nell'errore anche quella giusta. La coerenza sale sempre; la wF1 può salire o scendere.

**SoftCons = 1 e artefatto coincidono.** Finché (NO, NO) è ammessa, una parte delle coppie viene decodificata così e lo scorer la conta incoerente. Escludere NO dalle coppie reversibili richiede di sapere quali coppie sono reversibili, cioè proprio l'informazione dell'artefatto. Va detto esplicitamente nel paper.

## Piano

1. **Fatto:** baseline senza apprendimento, mdeberta-v3-base con 3 seed e cinque decodifiche, Claude Opus 5 zero-shot e 8-shot (settembre).
2. **Encoder più grande** con le stesse decodifiche: DeBERTa-v3-large (solo inglese) o XLM-R large, se entra negli 8 GB (batch 16, bf16). `scripts/train_encoder.py --model ...`.
3. **Vincolo in addestramento:** perdita di consistenza sulla coppia (divergenza fra *p*(· | ρ(*x*)) e *p*(· | *x*) permutata da *r*), o augmentation con le coppie invertite; confronto con la sola decodifica vincolata (H1).
4. **Analisi d'errore:** coppie corrette dal vincolo, coppie "coerentemente sbagliate", stratificazione per esito della regola di lunghezza (H3).
5. **Opzionale, circa 2–4 dollari per variante:** Claude Opus 5.5 con esempi distribuiti come i dati e linee guida di annotazione nel prompt. Serve alla storia "LLM di frontiera vs modello piccolo + struttura", la stessa proposta per AgentRisk.

## Legame con AgentRisk

Stessa struttura argomentativa: un modello statistico stima, un livello simbolico impone vincoli noti a priori (qui l'inversione, in AgentRisk la policy e il vincolo congiunto della classe «senza rischio»). DiCo-NLI è il caso più pulito: il vincolo è esatto e lo scorer lo misura direttamente.
