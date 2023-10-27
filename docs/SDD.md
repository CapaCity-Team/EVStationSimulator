# Simulazione

1. Generazione di stazioni in una griglia
2. Posizionamento dei veicoli nelle stazioni
3. Creazione di utenti basati su dati reali
4. Run della simulazione
5. Analisi dei risultati

# Metriche di performance

1. Tempo di attesa medio
2. Tempo di attesa massimo
3. Tempo di attesa minimo
4. Tempo di attesa medio per stazione

# Classi

### Stazione:
1. Potenza
2. Capacità
3. Max concurrent charging
4. Min battery level for unlocking (could be a global variable)
5. Posizione
6. Monopattini in stazione
    - charge
    - lock
    - unlock
    - request_to_lock
    - request_to_unlock

### Abstract Vehicle:
1. Id
2. Livello batteria
    - Move

### Monopattino (Vehicle):
1. Capacità batteria (variabile di classe)
2. Consumo per unità di spazio (variabile di classe)

### User:
1. Partenza
2. Arrivo
3. Wait time unlock
4. Wait time lock
5. Time of lock
    - Ride

# Dettagli da definire

1. **Come funziona la ricarica?**
    * Veicoli caricati dal primo al ultimo:
        1. Se il numero di veicoli scarichi è minore di n, dove n è il concurrent charging, tutta la potenza viene divisa equamente tra tutti i veicoli scarichi. Se il numero di veicoli scarichi è maggiore di n, tutta la potenza viene divisa equamente tra i primi n veicoli scarichi e il resto dei veicoli non viene caricato.
        2. Ogni veicolo può assorbire una potenza massima. La stazione carica i veicoli scarichi in ordine di arrivo. Quindi, partendo dal primo arrivato, se non è carico, gli fornisce la potenza richiesta. Se è carico, passa al successivo e continua così finché non esaurisce tutta la potenza.

    * Si può scegliere i veicoli da caricare, quindi si possono usare politiche di scheduling per decidere quali veicoli caricare.

2. **I veicoli fanno da resistenza per i veicoli successivi? Sia carichi che scarichi? L'energia viene dissipata? Il veicolo più vicino alla stazione vede una potenza maggiore?**

3. **Cosa succede se una stazione è vuota e un utente vuole sbloccare un veicolo? E per una stazione piena in cui un utente vuole bloccare un veicolo? Vengono considerati i tempi di attesa oppure ci interessano solo i tempi di attesa dovuti alla ricarica?**
