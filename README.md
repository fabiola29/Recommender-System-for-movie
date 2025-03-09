# Recommender System for Movie

Un sistema di raccomandazione di film basato su un approccio Knowledge-Based, con dati estratti da DBpedia e MovieLens.
L'applicazione consente di selezionare preferenze cinematografiche per ottenere suggerimenti personalizzati, mentre un modulo di valutazione confronta diverse strategie di raccomandazione.

## Funzionalità principali
- **Raccomandazione di film** basata su preferenze dell'utente (genere, regista, attori, nazionalità, popolarità, durata, decade).

- **Interfaccia interattiva con Streamlit** per una navigazione semplice e intuitiva.

- **Estrazione dei dati da DBpedia** con generazione di un file RDF `.ttl`.

- **Confronto tra diverse strategie di raccomandazione**:
   - Knowledge-Based
   - Raccomandazioni casuali
   - Film più popolari

- **Valutazione delle raccomandazioni** con metriche di accuracy, diversity e serendipity.

## Struttura del progetto
```
Reccomander-System-for-movie/
│── codice/
│   ├── Knowledge Based Recommender Systems/
│   │   ├── style/
│   │   ├── confirmation_screen.py
│   │   ├── data_extraction.py
│   │   ├── main.py
│   │   ├── movies_rdf.ttl
│   │   ├── recommendation.py
│   │   ├── reference_film.py
│   │   ├── results.py
│   │   ├── script_evaluation.py
│   │   ├── systemEvaluation.py
│   │   ├── utils.py
│── dataset/
│   ├── archive/
│   │   ├── links.csv
│   │   ├── movies.csv
│   │   ├── ratings.csv
│   │   ├── README.txt
│   │   ├── tags.csv
│   ├── simulated_users.json
│── README.md
```

## Avvio del sistema di raccomandazione
### 1️⃣ **Popolare il file RDF con i dati dei film**
Prima di avviare l'applicazione, è necessario generare il file RDF con i dati estratti da DBpedia:
```bash
python codice/Knowledge Based Recommender Systems/data_extraction.py
```

### 2️⃣ **Avviare l'applicazione con Streamlit**
Una volta popolato il dataset RDF, eseguire l'interfaccia web con:
```bash
streamlit run codice/Knowledge Based Recommender Systems/main.py
```
L'app consentirà all'utente di inserire le proprie preferenze e ottenere film consigliati.

### 3️⃣ **Valutare le prestazioni del sistema di raccomandazione**
Per confrontare diverse strategie e raccogliere metriche di performance:
```bash
python codice/Knowledge Based Recommender Systems/script_evaluation.py
```
Il sistema valuterà l'accuracy, la diversity e la serendipity delle raccomandazioni e genererà un report.

## 🛠Requisiti
Assicurati di avere installate le seguenti librerie:
```bash
pip install streamlit rdflib pandas numpy SPARQLWrapper
```

## Note
- Il file RDF `movies_rdf.ttl` viene aggiornato periodicamente con nuovi dati.
- Se il file RDF non esiste, l'app mostrerà un messaggio di errore finché non verrà generato.
- L'algoritmo di raccomandazione utilizza un mix di filtri sui dati RDF e un modello epsilon-greedy per l'esplorazione.

