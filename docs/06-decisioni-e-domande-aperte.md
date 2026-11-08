# 06 — Decisioni, domande aperte, rischi

## Stato della decisione

- **22 settembre 2026:** DiCo-NLI era la proposta principale fra i task SemEval 2027 (scheda formale in `ai-resources`, § 1).
- **7 novembre 2026** (proposta in `agent-risk/docs/09` § 9): AgentRisk come impegno principale, con la storia "modello piccolo addestrato + struttura simbolica vs LLM di frontiera"; DiCo-NLI **in modalità leggera**. La decisione di partecipare resta aperta per entrambi.
- **8 novembre 2026:** creato questo progetto. Il costo marginale di DiCo-NLI è basso: dati piccoli, encoder base in 3 minuti, metriche e vincoli già pronti e verificati.

Una modalità leggera ragionevole (proposta): encoder più grande + inversione + cross-lingue (se ammesso), sottomissione sui quattro track, paper centrato su "quanto vale il vincolo simbolico sopra modelli diversi".

## Novità: issue #1 sul repository ufficiale

Il 6 novembre 2026 la squadra ZeroBug ha aperto la [issue #1](https://github.com/ilopezgazpio/SemEval-2027-Task-2-DiCo-NLI/issues/1), la prima del repository, chiedendo se sono ammessi:

1. la somma delle probabilità fra le versioni in lingue diverse della stessa coppia (il nostro vincolo cross-lingue);
2. dedurre NEGATIVE_OTHER dall'assenza dell'istanza invertita (il nostro artefatto). Cita "un'implementazione pubblica" che lo descrive come "in attesa di approvazione degli organizzatori".

Al 8 novembre: **nessuna risposta**. Conseguenze:

- L'artefatto è ormai noto anche ad altre squadre: aprire una nostra issue sullo stesso punto non serve più. Basta seguire la #1, eventualmente aggiungere un commento con le misure (100% su train e dev, anche senza `pair_id`) e la proposta di presentare le NO in entrambi i versi.
- Finché non c'è risposta, cross-lingue e artefatto restano **varianti riportate a parte**, non il sistema principale.

## Domande agli organizzatori

1. Artefatto e cross-lingue sono ammessi? (issue #1, aperta da altri)
2. Il test conserverà `pair_id`, i suffissi `__original`/`__flipped` e la presenza delle sole NO in un verso?
3. I track 1–3 del test saranno ancora traduzioni parallele?
4. Quale ordinamento userà CodaBench, visto che i punteggi ufficiali sono tre?
5. Qual è l'accordo fra annotatori di PhrasIS? (si può cercare prima nel paper)

Stato: nessuna domanda inviata da noi.

## Rischi e limiti

- **Formato del test.** Se conserva l'artefatto, la classifica premierà chi lo sfrutta; se non lo conserva, quel guadagno (circa 10 punti di wF1) sparisce.
- **Parallelismo del test.** Il vincolo cross-lingue vale solo se il test è parallelo.
- **Portata della garanzia.** Il vincolo garantisce compatibilità, non verità: una coppia può essere coerente e sbagliata in entrambi i versi.
- **Gold rumoroso** e convenzioni idiosincratiche (preposizioni, quasi-sinonimi): tetto incerto.
- **Contaminazione:** PhrasIS è pubblico dal 2024, train e dev sono su GitHub.
- **Dev piccolo:** 277 coppie reversibili per lingua; una coppia sposta SoftCons e HardCons di circa 0,36 punti percentuali (1/277).

## Organizzatori

HiTZ / Ixa NLP, UPV/EHU: Iñigo López-Gazpio (lead, PhrasIS, STS), Jon Felix Apaolaza Larraya (pilot, metriche, scorer), Aitor Soroa, Rodrigo Agerri (multilingue, basco). Profili e letture in `ai-resources/lavori/2026-09_semeval-2027/task-2-dico-nli-organizzatori.md`.

## Prossimi passi

- [ ] Seguire la issue #1; decidere se commentarla con le nostre misure.
- [ ] Cercare nel paper PhrasIS l'accordo fra annotatori.
- [ ] Ripetere i 3 seed di mdeberta con il nuovo codice (riprodotto 1 seed l'8 novembre, vedi [04](04-risultati.md)).
- [ ] Encoder più grande con le stesse decodifiche.
- [ ] Misurare H3 (guadagni del vincolo dove la regola di lunghezza fallisce).
- [ ] Provare il formato di sottomissione sul development di CodaBench (`data.write_predictions`).
- [ ] Opzionale, con via libera esplicito sulla spesa: Claude Opus 5.5 sul dev inglese.
