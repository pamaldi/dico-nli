# 02 — Dati

## Termini usati

| Termine | Definizione |
|---|---|
| **reference** | file con le etichette gold e la colonna `reverse_pair_id` (l'identificativo dell'istanza invertita); serve allo scorer |
| **participant_labeled** | file per l'addestramento: come il reference ma senza `reverse_pair_id` |
| **artefatto** | regolarità introdotta dalla costruzione del dataset, che permette di indovinare l'etichetta senza leggere il testo |
| **pair_id** | identificativo della coppia sorgente PhrasIS, uguale nelle due direzioni e in tutte le lingue |

## File

Scaricati da `scripts/download_data.py` in `data/raw/final_data/{train,dev}/`, revisione `588968e610` (8 settembre 2026, ultimo commit all'8 novembre). Per ogni split e track: `dico_nli_<split>_track<N>_{participant_labeled,reference,submission_template}.csv`. Il repository è GPL-3.0; la cartella non è versionata.

```text
instance_id,pair_id,text1_lang,text2_lang,text1,text2,reverse_pair_id,label
dico_phrasis_0000002__en-en__flipped,dico_phrasis_0000002,en,en,'s war shrine visit,'s shrine visit,dico_phrasis_0000002__en-en__original,FORWARD_ENTAILMENT
dico_phrasis_0000002__en-en__original,dico_phrasis_0000002,en,en,'s shrine visit,'s war shrine visit,dico_phrasis_0000002__en-en__flipped,BACKWARD_ENTAILMENT
```

**Identificativi.** `instance_id = <pair_id>__<lingua1>-<lingua2>__<original|flipped>`. L'inversa di `pid__a-b__original` è `pid__b-a__flipped`: nel track 4 `…__en-es__flipped` ha come inversa `…__es-en__original`. `data.reverse_id` la ricava dal solo identificativo, quindi la coppia è nota anche senza `reverse_pair_id`.

## Statistiche (`uv run dico-nli stats`)

| Split | Track | Istanze | Coppie reversibili | EQ | FE | BE | NO |
|---|---|---:|---:|---:|---:|---:|---:|
| train | 1, 2, 3 (ciascuno) | 3.042 | 1.282 | 802 | 881 | 881 | 478 |
| train | 4 | 18.252 | 7.692 | 4.812 | 5.286 | 5.286 | 2.868 |
| dev | 1, 2, 3 (ciascuno) | 660 | 277 | 174 | 190 | 190 | 106 |
| dev | 4 | 3.960 | 1.662 | 1.044 | 1.140 | 1.140 | 636 |

Il track 4 è sei volte i track monolingui: sei combinazioni di lingue (en-es, es-en, en-eu, …) per ogni coppia.

## Proprietà verificate

1. **I track 1–3 sono traduzioni parallele.** Stessi `pair_id`, stessa etichetta per ogni coppia e direzione nelle tre lingue (3.042/3.042 in train, 660/660 in dev). Verificato da un test.
2. **Artefatto su NO.** Gli esempi NO compaiono in un solo verso: un `pair_id` che compare una volta sola è NO, sempre, e viceversa (accuratezza 100% su train e dev, tutti i track). La stessa deduzione senza `pair_id`, cercando nel file la coppia con i testi scambiati, arriva al 99,8–100%: l'artefatto nasce dalla costruzione del dataset, non da una colonna. Si misura con `uv run dico-nli artifact`.
3. **Bias di lunghezza.** Nelle coppie reversibili del train inglese in cui il primo testo è più lungo, l'etichetta è FE in 682 casi su 1.008 e BE solo in 50. La regola "il più lungo implica il più corto" è quindi un pavimento alto (vedi [04](04-risultati.md)).

## Che cosa dice la struttura, e che cosa no

- Che due istanze siano l'una l'inversa dell'altra si legge dagli identificativi: è legittimo usarlo per imporre la regola di inversione, perché lo scorer stesso valuta la coppia.
- Che un'istanza **non abbia** l'inversa nel file rivela la sua etichetta (NO). È l'artefatto: usarlo è un'altra cosa, e va chiesto agli organizzatori ([06](06-decisioni-e-domande-aperte.md)).
- Se il test conserverà `pair_id`, suffissi di direzione e la presenza delle sole NO in un verso **non è noto**: il formato del test non è pubblicato.

## Esempi in cui il gold è discutibile

Dal pilota con Claude di settembre (30 coppie del dev inglese):

| Coppia | Claude | Gold | Nota |
|---|---|---|---|
| *on Thursday* / *Thursday* | EQ | implicazione | convenzione sulle preposizioni |
| *in Belgian bus crash* / *in Belgian coach crash* | implicazione | EQ | quasi-sinonimi |
| *Nine children* / *Five children* | — | FE | "cinque" letto come "almeno cinque" |
| *Saudi Women* / *Saudis* | "Saudi Women" implica "Saudis" | il contrario | gold probabilmente errato |

Il tetto reale dipende dall'accordo fra annotatori di PhrasIS, ancora da cercare nel paper (López-Gazpio et al., 2024, *Logic Journal of the IGPL*).
