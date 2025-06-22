PROGETTO: Random Walk con Accelerazione di Fermi

-----------

DESCRIZIONE:
Questo script Python simula un random walk unidimensionale in cui il walker può subire accelerazioni in funzione di condizioni specifiche (attraversamento dell'origine, riflessione o superamento di una barriera).
Il modello si ispira ai meccanismi di accelerazione di Fermi.

Tre configurazioni fisiche sono simulate:
1. attraversamento_origine
2. doppia_riflessione
3. doppia_accelerazione

Per ciascuna configurazione, viene:
- simulati più cammini,
- mostrata l'evoluzione della posizione e della lunghezza del passo nel tempo,
- stimata la distribuzione dell'energia (proporzionale al quadrato della lunghezza dell' ultimo passo di ogni cammino),
- eseguito un fit a legge di potenza per stimare l'indice spettrale gamma (γ).

-----------

UTILIZZO:
Eseguire lo script da terminale specificando 5 parametri numerici nell'ordine indicato e separati da uno spazio:

python3 accelerazione_fermi_piastrelli.py <n_walkers> <step_init> <n_steps> <x_init> <gain>

Dove:
- n_walkers : numero totale dei walker (es. 6000)
- step_init : lunghezza iniziale del passo (es. 1.0)
- n_steps   : numero totale di passi (es. 10000)
- x_init    : posizione iniziale del walker (es. 10.0)
- gain      : fattore moltiplicativo di accelerazione (es. 1.05)

Esempio:
python3 accelerazione_fermi_piastrelli.py 1.0 1000 10.0 1.01

-----------

NOTE:
- Il parametro xmax (massimo valore raggiungibile nella direzione positiva) è fissato a 80.0 all'interno del codice.
- La stima dell'indice spettrale gamma viene effettuata senza l'uso della scala logaritmica.
- Se il fit della legge di potenza fallisce (a volte avviene perché ci sono pochi dati utili), il programma lo segnala ma prosegue per le altre configurazioni.


------
Autore:
Alessandro Piastrelli


