# 07 — Test e indicatori

## Termini usati

| Termine | Definizione |
|---|---|
| **precisione** di un'etichetta | fra le istanze predette con quell'etichetta, quota corretta |
| **richiamo** | fra le istanze che hanno davvero quell'etichetta, quota trovata |
| **F1** | media armonica di precisione e richiamo: 2·P·R / (P + R) |
| **F1 pesato (wF1)** | media delle F1 delle quattro etichette, pesata per il numero di istanze gold di ciascuna |
| **SoftCons / HardCons** | vedi [01](01-task.md): coppie compatibili / coppie con entrambe le direzioni giuste |
| **baseline** | sistema banale che fissa il livello minimo da superare |

## Gli indicatori con un esempio reale

La coppia *'s shrine visit* (testo 1) / *'s war shrine visit* (testo 2) ha gold BE in ordine originale e FE invertita. La regola di lunghezza predice BE (il testo 2 è più lungo) e, invertita, FE: la coppia conta per SoftCons **e** per HardCons. Sulla coppia *over Bhutto murder* / *In Bhutto Death* (gold EQ, EQ), la stessa regola dice EQ solo se le parole sono tante quante: qui 3 contro 3, quindi EQ, giusta. Su *Syria opposition unity* / *Syria divided opposition* (gold NO, in un solo verso) la regola dice EQ: errore per la wF1, ma l'istanza non entra nella consistenza perché non ha inversa.

**Perché la costante EQ ha wF1 0,110.** Prende tutte le 174 EQ del dev (richiamo 1) ma con precisione 174/660 = 0,264: F1(EQ) = 0,418, pesata per 174/660 dà 0,110; le altre etichette hanno F1 = 0. SoftCons è 1 perché (EQ, EQ) è sempre compatibile; HardCons 0,314 è la quota di coppie reversibili davvero EQ (87 su 277).

## I 16 test (`uv run pytest`)

| Test | Che cosa verifica | Che cosa non verifica |
|---|---|---|
| `test_reverse_map_is_involution` | r(r(l)) = l; (NO, NO) non è coerente | — |
| `test_reverse_id_also_for_mixed_track` | l'inversa di `…__en-es__flipped` è `…__es-en__original` | che il test mantenga questi identificativi |
| `test_consistency_metrics_table` (5 casi) | la tabella SoftCons/HardCons di [01](01-task.md) | — |
| `test_weighted_f1_perfect_and_singletons_ignored_by_consistency` | predizione perfetta = 1, 1, 1; le NO senza inversa non entrano nella consistenza | — |
| `test_decode_inversion_numeric_example` | l'esempio numerico di [03](03-approccio.md): (BE, EQ) → (BE, FE) | che il vincolo migliori su dati reali |
| `test_decode_crosslingual_and_leak` | la lingua più sicura trascina le altre; senza inversa ⇒ NO con l'artefatto | — |
| `test_length_rule` | la regola di lunghezza su due casi | — |
| `test_llm_schema_and_parse` | schema con le etichette ufficiali; rifiuti ed errori contati come "senza risposta" | nessuna chiamata all'API |
| `test_request_params_shape` | ragionamento adattivo, effort esplicito, nessun `fallbacks` nelle batch | — |
| `test_dataset_shape_parallel_tracks_and_artifact` | dimensioni dei quattro track, traduzioni parallele, artefatto al 100% | (salta se i dati non sono scaricati) |
| `test_rule_baselines_match_september` | baseline sul dev inglese uguali a settembre | |
| `test_metrics_match_official_scorer` | le nostre metriche coincidono con `evaluation_functions` ufficiale sui track 1 e 4 | (salta se lo scorer non è scaricato) |

## Baseline di riferimento sul dev

| Sistema | en wF1 | SoftCons | HardCons |
|---|---:|---:|---:|
| Costante EQ | 0,110 | 1,000 | 0,314 |
| Regola di lunghezza | 0,467 | 1,000 | 0,614 |
| Regola di lunghezza + struttura (artefatto) | 0,667 | 1,000 | 0,614 |

Spagnolo e basco in [04](04-risultati.md). Le regole hanno SoftCons 1 perché sono simmetriche per costruzione: invertire i testi inverte il confronto delle lunghezze.
