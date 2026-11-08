# Documentazione

Riassume ciò che è stato discusso e stabilito su DiCo-NLI fino all'8 novembre 2026. Le fonti originali restano nell'archivio `ai-resources`, cartella `lavori/2026-09_semeval-2027`: [scheda formale](../../ai-resources/lavori/2026-09_semeval-2027/schede-task-fattibili.md) (§ 1), [task spiegato e confronto con Claude](../../ai-resources/lavori/2026-09_semeval-2027/dico-nli-claude-e-obiettivi.md), [organizzatori e risorse](../../ai-resources/lavori/2026-09_semeval-2027/task-2-dico-nli-organizzatori.md), script in `analisi/`.

| File | Contenuto |
|---|---|
| [01-task.md](01-task.md) | il task spiegato da zero (metodo delle due domande, esempio completo, etichette con fenomeni), il dataset in breve, metriche con esempi, domande frequenti; ogni esempio ha la traduzione italiana |
| [02-dati.md](02-dati.md) | fonte dei testi, file e colonne, track 4 per esteso, statistiche per verso, segnali superficiali (lunghezza, parole in comune), train contro dev, artefatto `NEGATIVE_OTHER`, gold discutibile |
| [03-approccio.md](03-approccio.md) | domanda di ricerca, ipotesi, vincoli simbolici in decodifica, piano |
| [04-risultati.md](04-risultati.md) | risultati del 22 settembre (regole, mdeberta, Claude Opus 5) e verifica di riproduzione dell'8 novembre |
| [05-ambiente.md](05-ambiente.md) | librerie, gruppi uv, GPU, costi, riproducibilità |
| [06-decisioni-e-domande-aperte.md](06-decisioni-e-domande-aperte.md) | stato della decisione, issue #1, domande agli organizzatori, rischi, prossimi passi |
| [07-test-e-indicatori.md](07-test-e-indicatori.md) | i 16 test automatici e le metriche spiegate con esempi |

Convenzione: ciò che è **verificato sui dati o sul sito** è scritto come fatto; ciò che è **proposta o ipotesi** è dichiarato tale.
