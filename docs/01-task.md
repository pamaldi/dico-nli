# 01 — Il task

Questa pagina spiega il task da zero. Tutti gli esempi sono **reali**, presi dai file ufficiali, e hanno accanto la **traduzione italiana** (in corsivo fra virgolette basse: «…»). I dettagli sul dataset sono in [02](02-dati.md); qui c'è quanto basta per capire il task.

## Termini usati

| Termine | Definizione |
|---|---|
| **NLI** | *Natural Language Inference*, inferenza in linguaggio naturale: decidere se un testo implica un altro |
| **implicazione** (*entailment*) | *A* implica *B* se, ogni volta che *A* è vero, anche *B* è per forza vero: «un cane nero» implica «un cane» |
| **sintagma** | pezzo di frase con un senso unitario, più corto di una frase: «nella morte di Bhutto», «un cane nero», «che indossa» |
| **coppia** | due sintagmi messi a confronto: (testo 1, testo 2) |
| **istanza** | una riga del file: una coppia letta in un certo ordine. La stessa coppia può comparire come due istanze, `original` (ordine di partenza) e `flipped` (testi scambiati) |
| **coppia reversibile** | coppia presente nel file in entrambi gli ordini; sono le sole su cui si misura la coerenza |
| **gold** | l'etichetta giusta, cioè quella scelta dagli annotatori umani |
| **track** | sottogara per lingua: 1 inglese, 2 spagnolo, 3 basco, 4 misto |
| **wF1, SoftCons, HardCons** | i tre punteggi ufficiali, spiegati più sotto |

## In parole semplici

Il sistema riceve **due pezzi di frase** e deve dire **quale dei due "contiene" l'altro**, nel senso del significato:

- «visita al santuario di guerra» dice tutto quello che dice «visita al santuario», più un dettaglio. Se è vera la prima, è vera anche la seconda: la prima **implica** la seconda.
- Il contrario non vale: una visita al santuario non è per forza a un santuario *di guerra*.

Quindi la relazione ha un **verso**: dal testo più specifico a quello più generico. Il task chiede di riconoscere quel verso.

Poi c'è la parte che dà il nome al task (*Directional Consistency*, coerenza direzionale): ogni coppia viene presentata **due volte, con i testi scambiati**, e le due risposte devono essere coerenti fra loro. Se in un ordine dico "il primo implica il secondo", nell'altro devo dire "il secondo implica il primo".

## Come si decide l'etichetta: due domande

Per ogni coppia (testo 1, testo 2) bastano due domande:

1. Se è vero il **testo 1**, è per forza vero il **testo 2**?
2. Se è vero il **testo 2**, è per forza vero il **testo 1**?

| Domanda 1 (1 ⇒ 2) | Domanda 2 (2 ⇒ 1) | Etichetta | Sigla |
|---|---|---|---|
| sì | no | `FORWARD_ENTAILMENT` (implicazione in avanti) | FE |
| no | sì | `BACKWARD_ENTAILMENT` (implicazione all'indietro) | BE |
| sì | sì | `EQUIVALENCE` (equivalenza) | EQ |
| no | no | `NEGATIVE_OTHER` (nessuna implicazione) | NO |

"In avanti" vuol dire nel verso di lettura (dal testo 1 al testo 2); "all'indietro" vuol dire dal testo 2 al testo 1.

### Le due domande applicate

| Testo 1 | Testo 2 | 1 ⇒ 2? | 2 ⇒ 1? | Etichetta |
|---|---|---|---|---|
| *Moscow meeting* «incontro a Mosca» | *meeting* «incontro» | sì | no: un incontro può essere altrove | FE |
| *hospital* «ospedale» | *British hospital* «ospedale britannico» | no: può non essere britannico | sì | BE |
| *dressed in* «vestito con» | *wearing* «che indossa» | sì | sì | EQ |
| *A man* «un uomo» | *A child* «un bambino» | no | no | NO |

### Attenzione: "giusto" vuol dire "come l'annotatore"

Le etichette sono state messe da persone, con convenzioni proprie, non da un logico. Esempio: *over Bhutto murder* «sull'omicidio di Bhutto» / *In Bhutto Death* «nella morte di Bhutto» è **EQ** nel gold. A rigore un omicidio implica una morte, ma non il contrario (sarebbe FE); l'annotatore li ha considerati la stessa notizia. Il sistema viene premiato se riproduce il gold, non se ragiona in modo impeccabile. Altri casi discutibili sono elencati in [02](02-dati.md).

## Un esempio completo, dall'inizio alla fine

**La coppia di partenza.** Nel dataset ci sono due sintagmi presi da titoli di giornale:

- *'s shrine visit* → «visita al santuario (di qualcuno)»
- *'s war shrine visit* → «visita al santuario di guerra (di qualcuno)»

Il *'s* iniziale è il genitivo sassone inglese (*Abe's visit* = «la visita di Abe»). Il nome della persona è rimasto fuori quando il sintagma è stato ritagliato dal titolo; per questo il frammento comincia con *'s*. È normale nei dati: i testi sono pezzi, non frasi complete.

**Le due istanze.** La coppia compare due volte nel file del track inglese:

| `instance_id` | Testo 1 | Testo 2 | Gold |
|---|---|---|---|
| `dico_phrasis_0000002__en-en__original` | *'s shrine visit* «visita al santuario» | *'s war shrine visit* «visita al santuario di guerra» | BE |
| `dico_phrasis_0000002__en-en__flipped` | *'s war shrine visit* «visita al santuario di guerra» | *'s shrine visit* «visita al santuario» | FE |

- Nella riga `original` il testo più specifico è il **secondo**: il testo 2 implica il testo 1, quindi BE.
- Nella riga `flipped` gli stessi testi sono scambiati: ora il più specifico è il **primo**, quindi FE.

**Che cosa deve consegnare il sistema.** Una riga per istanza:

```text
instance_id,label
dico_phrasis_0000002__en-en__flipped,FORWARD_ENTAILMENT
dico_phrasis_0000002__en-en__original,BACKWARD_ENTAILMENT
```

**Come viene giudicato.**

| Risposta del sistema (`original`, `flipped`) | Giudizio |
|---|---|
| (BE, FE) | giuste entrambe e coerenti fra loro: il caso ideale |
| (FE, BE) | sbagliate entrambe, ma coerenti fra loro: il sistema ha capito che c'è un'implicazione ma ha sbagliato il verso |
| (BE, EQ) | una giusta e una sbagliata, e incoerenti: nello stesso momento dice "il secondo è più specifico" e "sono equivalenti" |

## Le quattro etichette nel dettaglio

Esempi reali dal dev, ordine `original`. Le etichette valgono per l'ordine scritto (testo 1 a sinistra).

### FE e BE: un testo è più specifico dell'altro

FE e BE sono la **stessa relazione** vista dai due lati: conta solo se il testo più specifico sta a sinistra (FE) o a destra (BE). Negli esempi qui sotto il più specifico è sempre a sinistra, quindi sono scritti come FE; nel dataset compaiono anche nell'ordine opposto, come BE.

| Fenomeno | Più specifico (testo 1) | Più generico (testo 2) |
|---|---|---|
| si aggiunge un aggettivo o un complemento | *Moscow meeting* «incontro a Mosca» | *meeting* «incontro» |
| | *in Syria chemical weapons attack* «nell'attacco con armi chimiche in Siria» | *in Syria attack* «nell'attacco in Siria» |
| | *British hospital* «ospedale britannico» | *hospital* «ospedale» |
| una categoria più ristretta al posto di una più ampia | *A biker* «un ciclista» | *A person* «una persona» |
| | *The German shepherd dark dog* «il cane scuro, un pastore tedesco» | *A black dog* «un cane nero» |
| una quantità più precisa | *Several people* «diverse persone» | *People* «persone» |
| un evento più preciso | *in 2007 Bhutto assassination* «nell'assassinio di Bhutto del 2007» | *in Bhutto death* «nella morte di Bhutto» |
| un dettaglio sull'azione | *driving down* «che guida in discesa» | *driving* «che guida» |
| | *looking up* «che guarda in alto» | *looking* «che guarda» |
| il plurale per il singolare (convenzione del gold) | *anti-protest laws* «leggi anti-proteste» | *anti-protest law* «legge anti-proteste» |

L'esempio del cane mostra di nuovo la convenzione degli annotatori: «scuro» non implica rigorosamente «nero», ma il gold lo accetta.

### EQ: i due testi dicono la stessa cosa

Sono **parafrasi**: parole diverse, stesso significato. Spesso non hanno nessuna parola in comune, e questo le rende difficili per i metodi che confrontano le parole.

| Testo 1 | Testo 2 |
|---|---|
| *2 French Journalists* «2 giornalisti francesi» | *Two French journalists* «due giornalisti francesi» |
| *a monochrome photograph* «una fotografia monocromatica» | *a black and white photo* «una foto in bianco e nero» |
| *in the direction of the shoreline* «in direzione della linea di costa» | *towards the shore* «verso la riva» |
| *dressed in* «vestito con» | *wearing* «che indossa» |
| *a bovine with brown-and-white coloring* «un bovino dal mantello marrone e bianco» | *A brown and white cow* «una mucca marrone e bianca» |
| *Bangladesh building disaster* «disastro dell'edificio in Bangladesh» | *Bangladesh building collapse* «crollo dell'edificio in Bangladesh» |

L'ultimo è un'equivalenza "larga": disastro e crollo non sono sinonimi, ma nel titolo indicano lo stesso evento.

### NO: nessuno dei due implica l'altro

NO raccoglie casi molto diversi fra loro: cose incompatibili, ma anche cose compatibili e semplicemente indipendenti.

| Che tipo di caso | Testo 1 | Testo 2 | Perché è NO |
|---|---|---|---|
| alternative della stessa categoria | *A man* «un uomo» | *A child* «un bambino» | o l'uno o l'altro |
| | *A close-up view* «una vista ravvicinata» | *A side view* «una vista laterale» | due inquadrature diverse |
| | *out of the water* «fuori dall'acqua» | *through the water* «attraverso l'acqua» | due posizioni diverse |
| proprietà indipendenti | *A dining table* «un tavolo da pranzo» | *A wooden table* «un tavolo di legno» | possono essere veri insieme, ma nessuno garantisce l'altro |
| contrasto | *Syria opposition unity* «unità dell'opposizione siriana» | *Syria divided opposition* «opposizione siriana divisa» | si contraddicono |
| eventi collegati ma diversi | *catches fire* «prende fuoco» | *after fire* «dopo l'incendio» | uno è l'evento, l'altro il momento dopo |
| forme grammaticali diverse | *'s integration* «l'integrazione (di qualcuno)» | *to join* «unirsi» | un nome e un verbo |
| casi al limite | *two people* «due persone» | *2* «2» | manca il "che cosa" |
| | *Nigeria lawmaker* «legislatore della Nigeria» | *Nigerian MP* «deputato nigeriano» | sembrerebbe un'implicazione, ma il gold dice NO |

## La regola di inversione

Scambiando i due testi, l'etichetta cambia in modo **prevedibile**:

| Etichetta nell'ordine originale | Etichetta con i testi scambiati | Perché |
|---|---|---|
| EQ | EQ | se si implicano a vicenda, l'ordine non conta |
| FE | BE | il testo specifico passa da sinistra a destra |
| BE | FE | idem, al contrario |
| NO | (non valutato) | nei dati la NO compare in un solo ordine |

Formalmente: sia *x* = (*a*, *b*) e ρ(*x*) = (*b*, *a*). Sulle prime tre etichette è definita *r*: EQ ↦ EQ, FE ↦ BE, BE ↦ FE. Per ogni coppia reversibile si chiede ŷ(ρ(*x*)) = *r*(ŷ(*x*)).

Il vincolo si può **controllare senza conoscere il gold**: basta guardare le due risposte del sistema. È questo che il progetto sfrutta ([03](03-approccio.md)).

Anche NO sarebbe invariante allo scambio (se nessuno implica l'altro, vale in entrambi gli ordini), ma il task non la include nella coerenza: le NO compaiono una volta sola.

## Il dataset in breve

### Da dove vengono i testi

I sintagmi vengono dal benchmark **PhrasIS** (López-Gazpio et al., 2024): coppie di pezzi di frase allineati e annotati. Le fonti sono di due tipi, riconoscibili dagli esempi:

| Fonte | Come sono i testi | Esempi |
|---|---|---|
| titoli di notizie | nomi propri, eventi, spesso cominciano con una preposizione o con *'s* | *in 2007 Bhutto assassination* «nell'assassinio di Bhutto del 2007», *Moscow meeting* «incontro a Mosca» |
| didascalie di immagini | descrizioni di ciò che si vede | *A brown and white cow* «una mucca marrone e bianca», *A close-up view* «una vista ravvicinata» |

Le coppie inglesi sono state tradotte in spagnolo e basco **con la stessa etichetta**. Chi e come abbia tradotto non è documentato.

I testi sono **brevissimi**: in media 3 parole in inglese, 3,6 in spagnolo, 2,7 in basco; il più lungo ha 15 parole.

### Com'è fatto un file

Ogni file è un CSV, una riga per istanza. Il file di addestramento (`participant_labeled`) ha queste colonne:

| Colonna | Che cosa contiene | Esempio |
|---|---|---|
| `instance_id` | nome dell'istanza: coppia, lingue, ordine | `dico_phrasis_0000002__en-en__original` |
| `pair_id` | nome della coppia, uguale nei due ordini e in tutte le lingue | `dico_phrasis_0000002` |
| `text1_lang`, `text2_lang` | lingua di ciascun testo | `en`, `en` |
| `text1`, `text2` | i due sintagmi | *'s shrine visit*, *'s war shrine visit* |
| `label` | l'etichetta gold | `BACKWARD_ENTAILMENT` |

Il file usato per la valutazione (`reference`) ha in più `reverse_pair_id`, il nome dell'istanza con i testi scambiati. Il file da consegnare ha solo `instance_id,label`.

Come si legge l'`instance_id`:

```text
dico_phrasis_0000002 __ en-en __ original
└── coppia ────────┘    └lingue┘  └ ordine: original o flipped
                        testo 1 - testo 2
```

### Le stesse coppie in tre lingue

I track 1, 2 e 3 contengono **le stesse coppie**, tradotte. Coppia `0000002`, ordine `original`:

| Track | Testo 1 | Testo 2 | Gold |
|---|---|---|---|
| 1 inglese | *'s shrine visit* | *'s war shrine visit* | BE |
| 2 spagnolo | *su visita a un santuario* | *su visita a un santuario de guerra* | BE |
| 3 basco | *hark santutegira egindako bisita* | *hark gerra-santutegira egindako bisita* | BE |
| | «la sua visita a un santuario» | «la sua visita a un santuario di guerra» | |

Un altro esempio, EQ, nelle tre lingue:

| Lingua | Testo 1 | Testo 2 |
|---|---|---|
| inglese | *a monochrome photograph* | *a black and white photo* |
| spagnolo | *una fotografía monocromática* | *una foto en blanco y negro* |
| basco | *argazki monokromo bat* | *zuri-beltzeko argazki bat* |
| italiano | «una fotografia monocromatica» | «una foto in bianco e nero» |

Il basco non è imparentato con le altre lingue e "incolla" preposizioni e articoli alle parole: *santutegira* = «al santuario», *argazki … bat* = «una foto». Per questo ha meno parole ma parole più lunghe.

### Il track 4: lingue mescolate

Nel track 4 i due testi della stessa istanza sono **in lingue diverse**. Si prendono le traduzioni dei track 1–3 e si combinano in tutti i modi possibili con lingue diverse: inglese-spagnolo, spagnolo-inglese, inglese-basco, basco-inglese, spagnolo-basco, basco-spagnolo. Coppia `0000004`, alcune righe:

| `instance_id` (finale) | Testo 1 | Testo 2 | Gold |
|---|---|---|---|
| `en-es__original` | *anti-protest law* «legge anti-proteste» (inglese) | *leyes antiprotestas* «leggi anti-proteste» (spagnolo) | BE |
| `es-en__flipped` | *leyes antiprotestas* «leggi anti-proteste» | *anti-protest law* «legge anti-proteste» | FE |
| `en-eu__original` | *anti-protest law* «legge anti-proteste» | *protesten aurkako legeak* «leggi contro le proteste» (basco) | BE |

Il sistema deve quindi confrontare il significato **attraverso le lingue**. Nel track 4 l'inversa di `en-es__original` è `es-en__flipped`: scambiando i testi si scambiano anche le lingue.

### Quanti sono

| Track | Lingua | Train (addestramento) | Dev (sviluppo) |
|---|---|---:|---:|
| 1 | inglese | 3.042 | 660 |
| 2 | spagnolo | 3.042 | 660 |
| 3 | basco | 3.042 | 660 |
| 4 | misto | 18.252 | 3.960 |

Il test non è ancora pubblicato. Il conto, per un track monolingue:

| Split | Coppie | che compaiono in 2 ordini (EQ, FE, BE) | che compaiono in 1 ordine (NO) | Istanze |
|---|---:|---:|---:|---:|
| train | 1.760 | 1.282 | 478 | 1.282 × 2 + 478 = 3.042 |
| dev | 383 | 277 | 106 | 277 × 2 + 106 = 660 |

Il track 4 ha esattamente sei volte questi numeri (sei combinazioni di lingue).

Etichette nel dev di un track monolingue:

| EQ | FE | BE | NO | Totale |
|---:|---:|---:|---:|---:|
| 174 (26%) | 190 (29%) | 190 (29%) | 106 (16%) | 660 |

FE e BE sono sempre in numero uguale, perché ogni FE in un ordine è una BE nell'altro.

### Tre cose da sapere sui dati

1. **Le NO compaiono solo una volta, sempre come `original`.** Quindi un'istanza senza la sua inversa nel file è NO, e un'istanza `flipped` non è mai NO. Questa regolarità (un *artefatto* della costruzione del dataset) permette di indovinare le NO senza leggere i testi. Se sia lecito usarla è una domanda aperta agli organizzatori ([06](06-decisioni-e-domande-aperte.md)).
2. **Il testo più lungo tende a implicare quello più corto.** Nell'inglese di train, quando il testo 1 è più lungo l'etichetta è FE in 682 casi su 1.008 e BE solo in 50. Una regola che guarda solo la lunghezza parte già da un punteggio non banale ([04](04-risultati.md)).
3. **Le parole in comune aiutano solo nei casi facili.** Se un testo contiene tutte le parole dell'altro più qualcosa (*Moscow meeting* / *meeting*), è un'implicazione nel 90% dei casi. Ma metà delle istanze (1.515 su 3.042) ha parole solo in parte condivise, e lì le quattro etichette sono quasi alla pari.

Numeri completi, tabelle e verifiche in [02](02-dati.md).

## Come si misura il risultato

Tre punteggi ufficiali, **nessuno principale**; l'eventuale classifica su CodaBench sarà annunciata.

| Punteggio | Domanda a cui risponde | Unità | Denominatore nel dev, per lingua |
|---|---|---|---|
| **wF1** (F1 pesato) | quante etichette sono giuste, istanza per istanza? | istanza | 660 istanze, NO comprese |
| **SoftCons** (coerenza "morbida") | quante coppie hanno risposte coerenti fra loro, giuste o sbagliate? | coppia reversibile | 277 coppie |
| **HardCons** (coerenza "dura") | quante coppie hanno **entrambe** le risposte giuste? | coppia reversibile | 277 coppie |

wF1 in dettaglio: per ogni etichetta si calcola la F1 (media armonica di precisione e richiamo), poi si fa la media delle quattro F1 pesata per quante istanze gold ha ciascuna. Un calcolo svolto (la costante EQ) è in [07](07-test-e-indicatori.md).

### Esempio su una coppia

Gold (BE, FE), cinque possibili risposte:

| Risposta `original` | Risposta `flipped` | Giuste | Coerenti | SoftCons | HardCons |
|---|---|---|---|---|---|
| BE | FE | entrambe | sì | ✅ | ✅ |
| FE | BE | nessuna | sì | ✅ | ❌ |
| BE | EQ | una | no | ❌ | ❌ |
| EQ | EQ | nessuna | sì | ✅ | ❌ |
| NO | NO | nessuna | **no**: lo scorer non la conta coerente | ❌ | ❌ |

### Esempio su un mini-file

Tre coppie reversibili (sei istanze) e una NO:

| Coppia | Gold (`original`, `flipped`) | Risposta | Coerente | Entrambe giuste |
|---|---|---|---|---|
| A | (FE, BE) | (FE, BE) | sì | sì |
| B | (EQ, EQ) | (FE, BE) | sì | no |
| C | (BE, FE) | (BE, EQ) | no | no |
| D (solo `original`) | NO | EQ | — | — |

SoftCons = 2/3 (A e B), HardCons = 1/3 (solo A). La coppia D conta solo per la wF1, come un errore.

### Che cosa ne segue

- SoftCons da sola non basta: rispondere sempre EQ dà SoftCons 1, perché (EQ, EQ) è sempre coerente.
- HardCons è la più difficile da aggirare: chiede risposte giuste **e** coerenti.
- Rispondere NO a una coppia reversibile costa due volte: sbagliato per la wF1 e incoerente per lo scorer.
- Lo scorer ufficiale, quando aggrega più track, fa la media con pesi uguali (`aggregation.py`).

## Perché non è banale

- **Frammenti senza contesto.** *'s shrine visit*, *dressed in*, *at barn animals* («fra gli animali della stalla»): manca il resto della frase.
- **Il verso conta.** Capire che due testi sono collegati non basta: sbagliare il verso è un errore pieno.
- **Convenzioni degli annotatori.** Plurale/singolare, preposizioni, numeri, quasi-sinonimi seguono scelte del gold non sempre prevedibili.
- **Tre lingue, e nel track 4 mescolate.** Il basco ha meno risorse e un modello lo conosce peggio.
- **Coerenza misurata a parte.** Un modello che risponde riga per riga può dare FE in un ordine ed EQ nell'altro.

## Domande frequenti

**Il testo 1 è sempre la "premessa", come nell'NLI classico?** No. È solo il testo scritto per primo. FE e BE dicono in che verso va l'implicazione rispetto a quell'ordine.

**Posso classificare solo l'ordine `original` e ricavare l'altro con la regola di inversione?** Sì: è il modo più semplice per avere coerenza alta. Però si spreca la seconda lettura, che il modello potrebbe capire meglio. La decodifica congiunta in [03](03-approccio.md) usa entrambe.

**Le etichette sono uguali nelle tre lingue?** Sì, per costruzione (verificato su train e dev). Una traduzione potrebbe cambiare una sfumatura, ma il gold resta quello inglese.

**Che cosa vuol dire "track 4 misto"?** Che in ogni istanza il testo 1 e il testo 2 sono in due lingue diverse, per esempio uno in basco e uno in inglese.

## Calendario

| Data | Evento |
|---|---|
| 8 settembre 2026 | train/dev, development su [CodaBench](https://www.codabench.org/competitions/18038/) |
| 10–31 gennaio 2027 | valutazione sul test (non pubblicato) |
| febbraio 2027 | system paper |
| marzo / aprile 2027 | notifica / camera-ready |

## Link

[Repository ufficiale](https://github.com/ilopezgazpio/SemEval-2027-Task-2-DiCo-NLI) · [scorer](https://github.com/ilopezgazpio/SemEval-2027-Task-2-DiCo-NLI/tree/main/evaluation_functions) · [starter kit](https://github.com/ilopezgazpio/SemEval-2027-Task-2-DiCo-NLI/tree/main/starter_kit) · [pagina SemEval](https://semeval.github.io/SemEval2027/tasks.html) · pilot degli organizzatori: Apaolaza Larraya et al., *[Assessing Logical Coherence of LLMs via Fine-Grained NLI](https://aclanthology.org/2026.lrec-1.423/)*, LREC 2026.
