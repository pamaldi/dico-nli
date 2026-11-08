# 01 — Il task

## Termini usati

| Termine | Definizione |
|---|---|
| **NLI** | *Natural Language Inference*: decidere se un testo implica un altro |
| **coppia, istanza** | una *coppia* è (testo 1, testo 2); ogni coppia reversibile compare come due *istanze*, ordine originale (`original`) e invertito (`flipped`) |
| **coppia reversibile** | coppia presente nel file in entrambi gli ordini; sono le sole su cui si calcola la consistenza |
| **F1 pesato (wF1)** | per ogni etichetta, F1 = media armonica di precisione e richiamo; poi media delle quattro F1 pesata per il numero di esempi gold di ciascuna. Si calcola sulle singole istanze |
| **SoftCons** | quota di coppie reversibili con predizioni **compatibili** (rispettano la regola di inversione), giuste o sbagliate che siano |
| **HardCons** | quota di coppie reversibili con **entrambe** le predizioni corrette (quindi anche compatibili) |
| **track** | sottogara per lingua: 1 inglese, 2 spagnolo, 3 basco, 4 misto multilingue |

## In una frase

Dati due testi brevi, dire **in quale verso va l'implicazione**, e farlo in modo coerente quando si invertono i due testi.

## Le quattro etichette

Esempi reali dal dev inglese:

| Etichetta | Significato | Esempio (testo 1 → testo 2) |
|---|---|---|
| `FORWARD_ENTAILMENT` (FE) | il testo 1 implica il testo 2, non viceversa | *'s war shrine visit* → *'s shrine visit* |
| `BACKWARD_ENTAILMENT` (BE) | il testo 2 implica il testo 1, non viceversa | *'s shrine visit* → *'s war shrine visit* |
| `EQUIVALENCE` (EQ) | si implicano a vicenda | *over Bhutto murder* ↔ *In Bhutto Death* |
| `NEGATIVE_OTHER` (NO) | nessuna implicazione | *Syria opposition unity* / *Syria divided opposition* |

Il testo più specifico implica quello più generico. I testi sono sintagmi presi da titoli di giornale (benchmark PhrasIS). "Giusto" significa "come l'annotatore", non "logicamente valido": *over Bhutto murder* / *In Bhutto Death* è EQ nel gold, anche se un omicidio implica una morte e non viceversa.

## La regola di inversione

Formalmente: sia *x* = (*a*, *b*) e ρ(*x*) = (*b*, *a*). Sulle prime tre etichette è definita *r*: EQ ↦ EQ, FE ↦ BE, BE ↦ FE. Per ogni coppia reversibile si chiede ŷ(ρ(*x*)) = *r*(ŷ(*x*)).

| Etichetta originale | Etichetta della coppia invertita |
|---|---|
| EQ | EQ |
| FE | BE |
| BE | FE |
| NO | esclusa dalle metriche di consistenza; nei dati compare in un solo verso |

Il vincolo è **deterministico e verificabile senza conoscere il gold**. Le relazioni che confluiscono in NO (negazione, alternanza, copertura, indipendenza nella logica naturale di MacCartney e Manning) sono tutte simmetriche: *r*(NO) = NO sarebbe ben definita, ma il task non la usa.

## Le metriche, con un esempio

Gold (BE, FE) e quattro possibili risposte:

| Predizione originale | Predizione invertita | Corrette | Compatibili | SoftCons | HardCons |
|---|---|---|---|---|---|
| BE | FE | entrambe | sì | ✅ | ✅ |
| FE | BE | nessuna | sì | ✅ | ❌ |
| BE | EQ | una | no | ❌ | ❌ |
| EQ | EQ | nessuna | sì | ✅ | ❌ |
| NO | NO | nessuna | **no** (lo scorer non la conta) | ❌ | ❌ |

Sono **tre punteggi ufficiali, senza una metrica principale**; l'eventuale ordinamento su CodaBench sarà annunciato. Conseguenze:

- SoftCons da sola non distingue un sistema da una costante: "sempre EQ" ha SoftCons 1.
- HardCons è la metrica più difficile da aggirare: chiede risposte corrette **e** coerenti.
- Lo scorer ufficiale media i track con pesi uguali quando aggrega (`aggregation.py`).

## Track e formato

| Track | Lingua | Train | Dev |
|---|---|---:|---:|
| 1 | inglese | 3.042 | 660 |
| 2 | spagnolo | 3.042 | 660 |
| 3 | basco | 3.042 | 660 |
| 4 | misto (testo 1 e testo 2 in lingue diverse) | 18.252 | 3.960 |

Sottomissione: un CSV con esattamente le colonne `instance_id,label`, nell'ordine del template (`data.write_predictions`).

## Calendario

| Data | Evento |
|---|---|
| 8 settembre 2026 | train/dev, development su [CodaBench](https://www.codabench.org/competitions/18038/) |
| 10–31 gennaio 2027 | valutazione sul test (non pubblicato) |
| febbraio 2027 | system paper |
| marzo / aprile 2027 | notifica / camera-ready |

## Link

[Repository ufficiale](https://github.com/ilopezgazpio/SemEval-2027-Task-2-DiCo-NLI) · [scorer](https://github.com/ilopezgazpio/SemEval-2027-Task-2-DiCo-NLI/tree/main/evaluation_functions) · [starter kit](https://github.com/ilopezgazpio/SemEval-2027-Task-2-DiCo-NLI/tree/main/starter_kit) · [pagina SemEval](https://semeval.github.io/SemEval2027/tasks.html) · pilot degli organizzatori: Apaolaza Larraya et al., *[Assessing Logical Coherence of LLMs via Fine-Grained NLI](https://aclanthology.org/2026.lrec-1.423/)*, LREC 2026.
