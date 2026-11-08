# 02 — Dati

## Termini usati

| Termine | Definizione |
|---|---|
| **reference** | file con le etichette gold e la colonna `reverse_pair_id` (l'identificativo dell'istanza invertita); serve allo scorer |
| **participant_labeled** | file per l'addestramento: come il reference ma senza `reverse_pair_id` |
| **submission_template** | elenco degli `instance_id` con la colonna `label` vuota: il modello del file da consegnare |
| **artefatto** | regolarità introdotta dalla costruzione del dataset, che permette di indovinare l'etichetta senza leggere il testo |
| **pair_id** | identificativo della coppia sorgente PhrasIS, uguale nelle due direzioni e in tutte le lingue |
| **sintagma** | gruppo di parole con una funzione unitaria nella frase (*the war shrine visit*, *in Bhutto death*), più corto di una frase |

Tutti i numeri di questa pagina sono calcolati sui file alla revisione `588968e610`; quelli marcati come **ipotesi** non lo sono. Accanto agli esempi c'è la traduzione italiana fra virgolette basse «…»; una panoramica più discorsiva del dataset è in [01](01-task.md#il-dataset-in-breve).

## Da dove vengono i testi

I testi sono sintagmi del benchmark **PhrasIS** (López-Gazpio et al., 2024), allineati a coppie e annotati con una relazione. Dagli esempi si riconoscono due tipi di fonte:

| Tipo | Come si riconosce | Esempi |
|---|---|---|
| titoli di notizie | nomi propri, eventi, preposizioni iniziali, frammenti come *'s* | *in 2007 Bhutto assassination* «nell'assassinio di Bhutto del 2007», *Moscow meeting* «incontro a Mosca», *'s shrine visit* «visita al santuario (di qualcuno)» |
| didascalie di immagini | descrizioni visive, spesso con articolo e maiuscola iniziale | *A brown and white cow* «una mucca marrone e bianca», *A man* «un uomo», *A close-up view* «una vista ravvicinata» |

I file non indicano la fonte di ogni coppia; le due fonti sono mescolate lungo tutto l'intervallo dei `pair_id`. Le versioni spagnola e basca sono traduzioni delle coppie inglesi; come sono state prodotte (manuale, automatica, revisionata) non è documentato nel repository.

I testi sono brevi:

| Lingua | Parole per testo, media | Mediana | Minimo – massimo | Caratteri del testo 1, media |
|---|---:|---:|---:|---:|
| inglese | 3,0 | 3 | 1 – 15 | 15,8 |
| spagnolo | 3,6 | 3 | 1 – 13 | 20,0 |
| basco | 2,7 | 2 | 1 – 10 | 19,5 |

Il basco ha meno parole ma più caratteri: è una lingua agglutinante, preposizioni e articoli diventano suffissi (*santutegira* «al santuario», *Mediterraneoan* «nel Mediterraneo»). Una regola che conta le parole si comporta quindi diversamente nelle tre lingue.

## File

Scaricati da `scripts/download_data.py` in `data/raw/final_data/{train,dev}/`, revisione `588968e610` (8 settembre 2026, ultimo commit all'8 novembre). Per ogni split (train, dev) e track (1–4) ci sono tre file, 24 in tutto: `dico_nli_<split>_track<N>_<tipo>.csv`. Il repository è GPL-3.0; la cartella non è versionata.

| Tipo | Colonne | A che cosa serve |
|---|---|---|
| `participant_labeled` | `instance_id, pair_id, text1_lang, text2_lang, text1, text2, label` | addestramento |
| `reference` | le stesse + `reverse_pair_id` | valutazione con lo scorer |
| `submission_template` | `instance_id, label` (vuota) | ordine e insieme delle righe da consegnare |

### Le colonne

| Colonna | Contenuto | Esempio |
|---|---|---|
| `instance_id` | identificativo dell'istanza (struttura sotto) | `dico_phrasis_0000002__en-en__original` |
| `pair_id` | coppia sorgente, uguale nei due versi e nelle lingue | `dico_phrasis_0000002` |
| `text1_lang`, `text2_lang` | lingua di ciascun testo: `en`, `es`, `eu` | `en`, `es` (track 4) |
| `text1`, `text2` | i due sintagmi | *'s shrine visit* «visita al santuario», *'s war shrine visit* «visita al santuario di guerra» |
| `reverse_pair_id` | `instance_id` dell'istanza invertita; **vuoto per le NO** | `dico_phrasis_0000002__en-en__flipped` |
| `label` | una delle quattro etichette, per esteso | `BACKWARD_ENTAILMENT` |

```text
instance_id,pair_id,text1_lang,text2_lang,text1,text2,reverse_pair_id,label
dico_phrasis_0000002__en-en__flipped,dico_phrasis_0000002,en,en,'s war shrine visit,'s shrine visit,dico_phrasis_0000002__en-en__original,FORWARD_ENTAILMENT
dico_phrasis_0000002__en-en__original,dico_phrasis_0000002,en,en,'s shrine visit,'s war shrine visit,dico_phrasis_0000002__en-en__flipped,BACKWARD_ENTAILMENT
```

Le righe sono ordinate per `instance_id`, quindi `flipped` precede `original` della stessa coppia.

**Identificativi.** `instance_id = <pair_id>__<lingua1>-<lingua2>__<original|flipped>`. L'inversa di `pid__a-b__original` è `pid__b-a__flipped`: nel track 4 `…__en-es__flipped` ha come inversa `…__es-en__original`. `data.reverse_id` la ricava dal solo identificativo, quindi la coppia è nota anche senza `reverse_pair_id`.

### Il track 4 per esteso

Tutte le righe della coppia `0000004` (gold originale BE: *anti-protest law* «legge anti-proteste» / *anti-protest laws* «leggi anti-proteste»; in spagnolo *ley/leyes antiprotestas*, in basco *protesten aurkako legea/legeak*, stesso significato) nel dev del track 4:

| `instance_id` (suffisso) | text1 | text2 | label | inversa |
|---|---|---|---|---|
| `en-es__original` | *anti-protest law* | *leyes antiprotestas* | BE | `es-en__flipped` |
| `es-en__flipped` | *leyes antiprotestas* | *anti-protest law* | FE | `en-es__original` |
| `es-en__original` | *ley antiprotestas* | *anti-protest laws* | BE | `en-es__flipped` |
| `en-es__flipped` | *anti-protest laws* | *ley antiprotestas* | FE | `es-en__original` |
| `en-eu__original` | *anti-protest law* | *protesten aurkako legeak* | BE | `eu-en__flipped` |
| … | | | | |

In tutto 12 righe per coppia reversibile (6 combinazioni × 2 versi) e 6 per una NO (solo `original`). Il testo 1 di `en-es__original` e quello di `en-eu__original` sono lo stesso sintagma inglese: il track 4 riusa le tre traduzioni, non introduce testi nuovi. Per questo i suoi numeri sono esattamente sei volte quelli dei track monolingui.

## Come si arriva ai numeri

| Split | `pair_id` distinti | di cui reversibili (2 istanze) | di cui NO (1 istanza) | Istanze per lingua |
|---|---:|---:|---:|---:|
| train | 1.760 | 1.282 | 478 | 1.282 × 2 + 478 = 3.042 |
| dev | 383 | 277 | 106 | 277 × 2 + 106 = 660 |

### Statistiche (`uv run dico-nli stats`)

| Split | Track | Istanze | Coppie reversibili | EQ | FE | BE | NO |
|---|---|---:|---:|---:|---:|---:|---:|
| train | 1, 2, 3 (ciascuno) | 3.042 | 1.282 | 802 | 881 | 881 | 478 |
| train | 4 | 18.252 | 7.692 | 4.812 | 5.286 | 5.286 | 2.868 |
| dev | 1, 2, 3 (ciascuno) | 660 | 277 | 174 | 190 | 190 | 106 |
| dev | 4 | 3.960 | 1.662 | 1.044 | 1.140 | 1.140 | 636 |

Il track 4 è sei volte i track monolingui: sei combinazioni di lingue (en-es, es-en, en-eu, eu-en, es-eu, eu-es) per ogni coppia; nessuna combinazione monolingue.

### Etichette per verso

Train, un track monolingue:

| Verso | EQ | FE | BE | NO | Totale |
|---|---:|---:|---:|---:|---:|
| `original` | 401 | 436 | 445 | 478 | 1.760 |
| `flipped` | 401 | 445 | 436 | **0** | 1.282 |

Dev: `original` 87 / 94 / 96 / 106, `flipped` 87 / 96 / 94 / 0.

Si legge così:

- FE e BE totali sono uguali (881) perché ogni FE in un verso è BE nell'altro.
- Nell'ordine originale FE e BE sono bilanciate (436 contro 445): l'ordine sorgente non favorisce un verso, quindi `original`/`flipped` da solo non dice se è FE o BE.
- **Nessuna istanza `flipped` è NO.** Il suffisso dell'identificativo, da solo, esclude NO per il 42% delle istanze.

## Che cosa c'è nei testi: segnali superficiali

Due regolarità che un modello impara subito, e che spiegano perché le baseline senza apprendimento non sono basse.

**Lunghezza.** Ordine `original`, train inglese, parole contate con spazi:

| Testo 1 rispetto al testo 2 | EQ | FE | BE | NO |
|---|---:|---:|---:|---:|
| più lungo | 152 | **347** | 22 | 124 |
| uguale | 125 | 61 | 88 | **244** |
| più corto | 124 | 28 | **335** | 110 |

Contando entrambi i versi delle coppie reversibili: quando il primo testo è più lungo, l'etichetta è FE in 682 casi su 1.008 e BE solo in 50. La regola "il più lungo implica il più corto" è quindi un pavimento alto (vedi [04](04-risultati.md)); sbaglia sulle EQ di lunghezza diversa (*in the direction of the shoreline* «in direzione della linea di costa» / *towards the shore* «verso la riva») e sulle implicazioni in cui il testo specifico non è più lungo (*A biker* «un ciclista» → *A person* «una persona»: due parole ciascuno).

**Parole in comune.** Train inglese, tutte le 3.042 istanze, insiemi di parole in minuscolo:

| Relazione fra le parole | Istanze | EQ | FE | BE | NO |
|---|---:|---:|---:|---:|---:|
| le parole del testo 2 sono un sottoinsieme stretto di quelle del testo 1 | 441 | 24 | **395** | 18 | 4 |
| le parole del testo 1 sono un sottoinsieme stretto di quelle del testo 2 | 444 | 24 | 18 | **395** | 7 |
| stesse parole | 4 | 4 | 0 | 0 | 0 |
| sovrapposizione parziale | 1.515 | 456 | 356 | 356 | 347 |
| nessuna parola in comune | 638 | **294** | 112 | 112 | 120 |

Quando un testo contiene tutte le parole dell'altro più qualcosa (*Moscow meeting* «incontro a Mosca» / *meeting* «incontro»), è implicazione nel 90% dei casi. Il grosso della difficoltà sta nelle 1.515 istanze a sovrapposizione parziale, dove le quattro etichette sono quasi alla pari, e nelle parafrasi senza parole in comune.

## Train e dev

- **Nessun `pair_id` in comune** fra train (1.760) e dev (383).
- I `pair_id` vanno da 1 a 3.320 e i due split sono intercalati (il dev non è un blocco finale). Ne sono usati 2.143: 1.177 numeri mancano. **Ipotesi**: sono in tutto o in parte il test (circa metà di train + dev), oppure coppie scartate. Non verificabile prima della pubblicazione.
- **I testi si ripetono fra split.** 160 dei 660 testi 1 del dev inglese compaiono anche nel train (come testo 1 o 2), e 7 coppie (testo 1, testo 2) del dev sono identiche a coppie del train.
- **Lo stesso sintagma compare in molte coppie, con etichette diverse.** Ordine `original`, train + dev inglese: *a woman* «una donna» in 20 coppie (8 FE, 8 BE, 2 EQ, 2 NO), *a man* «un uomo» in 20 (7 BE, 5 FE, 7 NO, 1 EQ), *a dog* «un cane» in 19. L'etichetta dipende dall'altro testo, non dal sintagma: memorizzare i testi non basta.

## Proprietà verificate

1. **I track 1–3 sono traduzioni parallele.** Stessi `pair_id`, stessa etichetta per ogni coppia e direzione nelle tre lingue (3.042/3.042 in train, 660/660 in dev). Verificato da un test.
2. **Artefatto su NO.** Gli esempi NO compaiono in un solo verso, sempre `original`: un `pair_id` che compare una volta sola è NO, sempre, e viceversa (accuratezza 100% su train e dev, tutti i track). La stessa deduzione senza `pair_id`, cercando nel file la coppia con i testi scambiati, arriva al 99,8–100%: l'artefatto nasce dalla costruzione del dataset, non da una colonna. Si misura con `uv run dico-nli artifact`.
3. **`flipped` non è mai NO.** Conseguenza della 2, ma leggibile dal solo suffisso dell'identificativo, istanza per istanza.
4. **Bias di lunghezza.** Vedi la tabella sopra.

## Che cosa dice la struttura, e che cosa no

| Informazione | Da dove si legge | Uso |
|---|---|---|
| quale istanza è l'inversa di quale | identificativi (`data.reverse_id`) | legittimo: lo scorer stesso valuta la coppia; serve al vincolo di inversione |
| quali istanze sono traduzioni della stessa coppia | `pair_id` + direzione | vincolo cross-lingue, da confermare ammesso ([issue #1](https://github.com/ilopezgazpio/SemEval-2027-Task-2-DiCo-NLI/issues/1)) |
| che un'istanza **non abbia** l'inversa, o sia `original` senza `flipped` | presenza/assenza di righe | rivela l'etichetta (NO): è l'artefatto, va chiesto agli organizzatori ([06](06-decisioni-e-domande-aperte.md)) |

Se il test conserverà `pair_id`, suffissi di direzione e la presenza delle sole NO in un verso **non è noto**: il formato del test non è pubblicato.

## Esempi in cui il gold è discutibile

Dal pilota con Claude di settembre (30 coppie del dev inglese) e dalla lettura del dev per questa pagina:

| Coppia | Atteso a lume di logica | Gold | Nota |
|---|---|---|---|
| *on Thursday* «giovedì (nel giorno)» / *Thursday* «giovedì» | EQ | implicazione | convenzione sulle preposizioni |
| *in Belgian bus crash* «nell'incidente dell'autobus in Belgio» / *in Belgian coach crash* «nell'incidente del pullman in Belgio» | implicazione | EQ | quasi-sinonimi |
| *Nine children* «nove bambini» / *Five children* «cinque bambini» | NO | FE | "cinque" letto come "almeno cinque" |
| *Saudi Women* «donne saudite» / *Saudis* «sauditi» | "Saudi Women" implica "Saudis" | il contrario | gold probabilmente errato |
| *Girls* «ragazze» / *Two girls* «due ragazze» | BE | FE | verso invertito rispetto alla regola "il più specifico implica" |
| *at barn animals* «fra gli animali della stalla» / *a sheep* «una pecora» | BE o NO | FE | come sopra |
| *Nigeria lawmaker* «legislatore della Nigeria» / *Nigerian MP* «deputato nigeriano» | EQ o BE | NO | |
| *over Bhutto murder* «sull'omicidio di Bhutto» / *In Bhutto Death* «nella morte di Bhutto» | FE | EQ | tolleranza sui quasi-sinonimi |

Il tetto reale dipende dall'accordo fra annotatori di PhrasIS, ancora da cercare nel paper (López-Gazpio et al., 2024, *Logic Journal of the IGPL*).
