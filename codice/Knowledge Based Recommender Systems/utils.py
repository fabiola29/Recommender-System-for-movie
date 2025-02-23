import streamlit as st
import pandas as pd
import re
from SPARQLWrapper import SPARQLWrapper, JSON

def load_css():
    """
    Funzione per caricare il foglio di stile CSS personalizzato nella pagina Streamlit.

    Questa funzione legge il contenuto del file CSS specificato e lo applica alla pagina utilizzando il
    metodo `st.markdown`. L'uso del parametro `unsafe_allow_html=True` consente l'inclusione di HTML
    e CSS personalizzati direttamente nel layout di Streamlit.

    Il file CSS deve trovarsi nella stessa directory del programma o essere specificato con il percorso relativo.

    Returns:
        None: La funzione non restituisce nulla, ma applica il CSS alla pagina Streamlit.
    """
    with open("style/layout_main.css") as f:
        css = f.read()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def load_data():
    """
    Funzione per caricare i dataset di MovieLens.

    Questa funzione carica i file CSV contenenti le informazioni sui film, i tag e le valutazioni degli utenti dal disco.

    Args:
        None

    Returns:
        tuple: Una tupla contenente tre DataFrame:
            - movies (DataFrame): Contiene le informazioni sui film (movieId, title, genres).
            - tags (DataFrame): Contiene le informazioni sui tag associati ai film (userId, movieId, tag, timestamp).
            - ratings (DataFrame): Contiene le valutazioni degli utenti per i film (userId, movieId, rating, timestamp).
    """
    movies = pd.read_csv("../../dataset/archive/movies.csv")
    tags = pd.read_csv("../../dataset/archive/tags.csv")
    ratings = pd.read_csv("../../dataset/archive/ratings.csv")

    return movies, tags, ratings


def normalize_title(movie_title):
    """
    Normalizza i titoli dei film:
    - Rimuove l'anno tra parentesi
    - Sposta eventuali articoli dal fondo al davanti (es. "Lord of the Rings, The" → "The Lord of the Rings")
    """
    # Rimuovere l'anno tra parentesi (es. "Lord of the Rings, The (1978)" → "Lord of the Rings, The")
    cleaned_title = re.sub(r"\(\d{4}\)", "", movie_title).strip()

    # Spostare articoli ('The', 'A', 'An') all'inizio se sono alla fine
    match = re.match(r"(.+), (The|A|An)$", cleaned_title)
    if match:
        cleaned_title = f"{match.group(2)} {match.group(1)}"

    return cleaned_title


def fetch_director_from_dbpedia(title):
    """
    Funzione per ottenere il regista di un film da DBpedia utilizzando una query SPARQL.

    Args:
        title (str): Il titolo del film per il quale si desidera ottenere il regista.

    Returns:
        str: Il nome del regista del film, se trovato.
    """

    # Pulisce e normalizza il titolo del film per una ricerca precisa
    movie_title_clean = normalize_title(title)

    print(f"Searching for director of: {movie_title_clean}")  # Debug: mostra il titolo del film in ricerca

    # Imposta il servizio SPARQL di DBpedia
    sparql = SPARQLWrapper("https://dbpedia.org/sparql")
    sparql.setReturnFormat(JSON)  # Imposta il formato di ritorno dei risultati come JSON

    # Query SPARQL per ottenere il regista del film
    query = f"""
     SELECT ?director
     WHERE {{
         ?film rdf:type dbo:Film .
         ?film foaf:name "{movie_title_clean}"@en .
         ?film dbo:director ?directorResource .
         ?directorResource foaf:name ?director .
     }}
     """

    # Imposta la query SPARQL
    sparql.setQuery(query)

    # Esegue la query e converte i risultati in formato JSON
    results = sparql.query().convert()

    print(f"Query result: {results}")  # Debug: mostra i risultati della query

    director = None  # Variabile per memorizzare il regista trovato
    if results['results']['bindings']:
        # Se ci sono risultati, estrai il regista
        for result in results['results']['bindings']:
            director = result['director']['value']
            print(f"Director found: {director}")  # Debug: mostra il regista trovato
    else:
        print(f"No director found for: {movie_title_clean}")  # Debug: mostra che non è stato trovato un regista

    return director  # Restituisce il nome del regista, se trovato

def fetch_actors_from_dbpedia(title):
    """
    Funzione per ottenere gli attori di un film da DBpedia utilizzando una query SPARQL.

    Args:
        title (str): Il titolo del film per il quale si desiderano ottenere gli attori.

    Returns:
        list: Una lista contenente gli attori del film, se trovati.
    """

    # Pulisce e normalizza il titolo del film per una ricerca precisa
    movie_title_clean = normalize_title(title)

    print(f"Searching for actors of: {movie_title_clean}")  # Debug: mostra il titolo del film in ricerca

    # Imposta il servizio SPARQL di DBpedia
    sparql = SPARQLWrapper("https://dbpedia.org/sparql")
    sparql.setReturnFormat(JSON)  # Imposta il formato di ritorno dei risultati come JSON

    # Query SPARQL per ottenere gli attori del film
    query = f"""
    SELECT ?actor
    WHERE {{
        ?film foaf:name "{movie_title_clean}"@en .
        ?film dbo:starring ?actorResource .
        ?actorResource foaf:name ?actor .
    }}
    """

    # Imposta la query SPARQL
    sparql.setQuery(query)

    # Esegue la query e converte i risultati in formato JSON
    results = sparql.query().convert()

    print(f"Query result: {results}")  # Debug: mostra i risultati della query

    actors = []  # Lista per memorizzare gli attori trovati
    if results['results']['bindings']:
        # Se ci sono risultati, estrai gli attori per ogni film
        for result in results['results']['bindings']:
            actor = result['actor']['value']
            actors.append(actor)  # Aggiungi l'attore alla lista
            print(f"Actor found: {actor}")  # Debug: mostra l'attore trovato
    else:
        print(f"No actors found for: {movie_title_clean}")  # Debug: mostra che non sono stati trovati attori

    return actors  # Restituisce la lista degli attori trovati

def fetch_nationality_from_dbpedia(title):
    """
    Funzione per ottenere la nazionalità di un film da DBpedia utilizzando una query SPARQL.

    Args:
        title (str): Il titolo del film di cui si desidera ottenere la nazionalità.

    Returns:
        list: Una lista contenente la nazionalità del film, se trovata.
    """

    # Pulisce e normalizza il titolo del film per una ricerca accurata
    movie_title_clean = normalize_title(title)
    print(f"Searching for nationality of: {movie_title_clean}")  # Debug: mostra il titolo del film in ricerca

    # Imposta il servizio SPARQL di DBpedia
    sparql = SPARQLWrapper("https://dbpedia.org/sparql")
    sparql.setReturnFormat(JSON)  # Imposta il formato di ritorno dei risultati come JSON

    # Query SPARQL per ottenere la nazionalità del film
    query = f"""
    SELECT  ?country
    WHERE {{
        ?film foaf:name "{movie_title_clean}"@en .
        ?film dbo:country ?countryResource .
        ?countryResource foaf:name ?country .
    }}
    """

    # Imposta la query SPARQL
    sparql.setQuery(query)

    # Esegue la query e converte i risultati in formato JSON
    results = sparql.query().convert()

    print(f"Query result: {results}")  # Debug: mostra i risultati della query

    nationalities = []  # Lista per memorizzare le nazionalità trovate
    if results['results']['bindings']:
        # Se ci sono risultati, estrai la nazionalità per ogni film
        for result in results['results']['bindings']:
            country = result['country']['value']
            nationalities.append(country)  # Aggiungi la nazionalità alla lista
            print(f"Nationality found: {country}")  # Debug: mostra la nazionalità trovata
    else:
        print(f"No nationality found for: {movie_title_clean}")  # Debug: mostra che non è stata trovata una nazionalità

    return nationalities  # Restituisce la lista delle nazionalità trovate

def fetch_runtime_from_dbpedia(title):
    """
    Funzione per ottenere la durata del film da DBpedia utilizzando una query SPARQL.

    Args:
        title (str): Il titolo del film di cui si desidera ottenere la durata.

    Returns:
        list: Una lista contenente la durata del film in formato stringa, se trovata.
    """

    # Pulisce e normalizza il titolo del film per una ricerca accurata
    movie_title_clean = normalize_title(title)
    print(f"Searching for runtime of: {movie_title_clean}")  # Debug: mostra il titolo del film in ricerca

    # Imposta il servizio SPARQL di DBpedia
    sparql = SPARQLWrapper("https://dbpedia.org/sparql")
    sparql.setReturnFormat(JSON)  # Imposta il formato di ritorno dei risultati come JSON

    # Query SPARQL per ottenere la durata del film
    query = f"""
    SELECT  ?runtime
    WHERE {{
        ?film foaf:name "{movie_title_clean}"@en .
        ?film dbo:runtime ?runtime .
    }}
    """

    # Imposta la query SPARQL
    sparql.setQuery(query)

    # Esegue la query e converte i risultati in formato JSON
    results = sparql.query().convert()

    print(f"Query result: {results}")  # Debug: mostra i risultati della query

    runtimes = []  # Lista per memorizzare i risultati delle durate trovate
    if results['results']['bindings']:
        # Se ci sono risultati, estrai la durata per ogni film
        for result in results['results']['bindings']:
            runtime = result['runtime']['value']
            runtimes.append(runtime)  # Aggiungi la durata alla lista
            print(f"Runtime found: {runtime}")  # Debug: mostra la durata trovata
    else:
        print(f"No runtime found for: {movie_title_clean}")  # Debug: mostra che non è stata trovata durata

    return runtimes  # Restituisce la lista delle durate trovate

def categorize_movies_by_votes(ratings, movies):
    """
    Funzione per categorizzare i film in base al numero di voti ricevuti.

    Args:
        ratings (DataFrame): DataFrame contenente le valutazioni dei film, con 'movieId' e 'rating'.
        movies (DataFrame): DataFrame contenente i dettagli dei film, con 'movieId' e 'title'.

    Returns:
        DataFrame: Un DataFrame contenente i film con i rispettivi conteggi di voti e la categoria.
    """

    # Conta il numero di valutazioni per ciascun film (raggruppa per 'movieId' e conta le righe per ogni film)
    vote_counts = ratings.groupby('movieId')['rating'].count().reset_index()
    vote_counts.rename(columns={'rating': 'vote_count'}, inplace=True)  # Rinomina la colonna in 'vote_count'

    # Unisci il conteggio dei voti con i dettagli dei film nel DataFrame 'movies'
    movies_with_votes = pd.merge(movies, vote_counts, on='movieId', how='left')

    # Categorizza i film in base al numero di voti ricevuti
    movies_with_votes['category'] = movies_with_votes['vote_count'].apply(
        lambda x: 'Popular' if 30 <= x <= 100  # Se il numero di voti è tra 30 e 100, il film è "Popular"
        else 'Niche' if x < 30  # Se il numero di voti è inferiore a 30, il film è "Niche"
        else 'Blockbuster'  # Se il numero di voti è maggiore di 100, il film è "Blockbuster", ovvero campione di incassi
    )

    return movies_with_votes  # Restituisce il DataFrame con i film e la loro categoria


def save_criteria(selected_genres, selected_director, selected_actors, selected_nationality, filtered_movies, selected_decade, duration, selected_tags):
    """
    Funzione per salvare i criteri selezionati dall'utente e passare alla pagina dei risultati.

    Args:
        selected_genres (list): Lista di generi selezionati.
        selected_director (list): Lista di registi selezionati.
        selected_actors (list): Lista di attori selezionati.
        selected_nationality (str): Nazionalità selezionata.
        filtered_movies (DataFrame): Film filtrati in base alla preferenza di popolarità.
        selected_decade (str): Decade selezionata.
        duration (str): Durata selezionata.
        selected_tags (list): Lista di tag selezionati.

    """
    # Verifica che tutti i campi obbligatori siano selezionati
    if not selected_genres or not selected_director or not selected_actors or not selected_nationality or not selected_decade or not duration:
        # Se manca almeno un campo obbligatorio, mostra un avviso
        st.warning(" ⚠️ Please select all required fields before proceeding.")
    else:
        # Salva i criteri selezionati nello stato della sessione
        st.session_state.criteria = {
            "genres": selected_genres,  # Generi selezionati
            "director": selected_director,  # Registi selezionati
            "actor": selected_actors,  # Attori selezionati
            "nationality": selected_nationality,  # Nazionalità selezionata
            "popularity_preference": filtered_movies,  # Film filtrati in base alla popolarità
            "year": selected_decade,  # Decade selezionata
            "duration": duration,  # Durata selezionata
            "tags": selected_tags,  # Tag selezionati
        }

        # Cambia la pagina per mostrare i risultati
        st.session_state.page = "results"


def select_genres(movies):
    """
    Funzione che permette all'utente di selezionare uno o più generi cinematografici preferiti.

    Args:
        movies (DataFrame): DataFrame contenente i film e i relativi dettagli.

    Returns:
        list: Una lista di generi selezionati dall'utente.
    """

    # Mostra un'intestazione per la selezione dei generi preferiti
    st.markdown('<div class="subheader"> What genres of movies do you prefer? </div>', unsafe_allow_html=True)

    # Estrai i generi unici dai film (considerando che i generi sono separati da "|")
    unique_genres = sorted(set(genre for genres in movies['genres'].dropna() for genre in genres.split("|")))

    # Mostra la multiselectbox per la selezione dei generi preferiti
    selected_genres = st.multiselect("Choose your preferred genres ( 1 or more)",
                                     unique_genres)  # Multiselect per i generi

    return selected_genres  # Restituisce la lista di generi selezionati


def select_director(movies):
    """
    Funzione che permette all'utente di selezionare uno o più registi tra quelli presenti nei film.

    Args:
        movies (DataFrame): DataFrame contenente i film e i relativi dettagli.

    Returns:
        list: Una lista di registi selezionati dall'utente.
    """

    # Mostra un'intestazione per la selezione dei registi preferiti
    st.markdown('<div class="subheader">Do you have favorite director?</div>', unsafe_allow_html=True)

    # Estrai i titoli dei primi 20 film dal dataset
    movie_titles = movies['title'].head(20).tolist()

    print(f"Extracted {len(movie_titles)} movie titles.")  # Debug: mostra quanti titoli sono stati estratti

    # Dizionario per memorizzare i registi dei film
    directors = {}

    # Recupera i registi di ciascun film tramite DBpedia
    for title in movie_titles:
        director = fetch_director_from_dbpedia(title)  # Funzione per ottenere il regista da DBpedia
        if director:
            directors[title] = director  # Aggiunge il regista al dizionario
        else:
            print(f"Skipping {title} as no director was found.")  # Messaggio di errore se non trovato il regista
            continue  # Salta il film se non è stato trovato un regista

    print(f"Directors dictionary: {directors}")  # Debug: mostra il dizionario dei registi

    # Estrai i registi unici per popolare la selectbox
    unique_directors = sorted(set(directors.values()))  # Rimuove duplicati e ordina i registi

    print(f"Unique directors: {unique_directors}")  # Debug: mostra i registi unici trovati
    print(f"Total unique directors: {len(unique_directors)}")  # Debug: numero totale di registi unici

    # Mostra la multiselectbox per la selezione di uno o più registi
    selected_director = st.multiselect("Choose a director ( 1 or more)", unique_directors)  # Multiselect per i registi

    return selected_director  # Restituisce la lista di registi selezionati


def select_actors(movies):
    """
    Funzione che permette all'utente di selezionare uno o più attori tra quelli presenti nei film.

    Args:
        movies (DataFrame): DataFrame contenente i film e i relativi dettagli.

    Returns:
        list: Una lista di attori selezionati dall'utente.
    """

    # Mostra un'intestazione per la selezione degli attori preferiti
    st.markdown('<div class="subheader">Do you have favorite actors?</div>', unsafe_allow_html=True)

    # Dizionario per memorizzare gli attori dei film
    actors = {}

    # Estrai i titoli dei primi 20 film dal dataset
    movie_titles = movies['title'].head(20).tolist()

    # Recupera gli attori di ciascun film tramite DBpedia
    for title in movie_titles:
        actor_list = fetch_actors_from_dbpedia(title)  # Funzione per ottenere gli attori da DBpedia
        if actor_list:
            actors[title] = actor_list  # Aggiunge gli attori al dizionario
        else:
            print(f"Skipping {title} as no actors were found.")  # Messaggio di errore se non trovati attori
            continue  # Salta il film se non sono stati trovati attori

    print(f"Actors dictionary: {actors}")  # Debug: mostra il dizionario degli attori

    # Estrai gli attori unici per popolare la selectbox
    all_actors = [actor for actor_list in actors.values() for actor in actor_list]
    unique_actors = sorted(set(all_actors))  # Rimuove duplicati e ordina gli attori
    print(f"Unique actors: {unique_actors}")  # Debug: mostra gli attori unici trovati
    print(f"Total unique actors: {len(unique_actors)}")  # Debug: numero totale di attori unici

    # Mostra la selectbox per la selezione di uno o più attori
    selected_actors = st.multiselect("Choose an actor ( 1 or more)", unique_actors)  # Multiselect per gli attori

    return selected_actors  # Restituisce la lista di attori selezionati

def select_nationality(movies):
    """
    Funzione che permette all'utente di selezionare una nazionalità per i film.

    Args:
        movies (DataFrame): DataFrame contenente i film e i relativi dettagli.

    Returns:
        str: La nazionalità selezionata dall'utente.
    """

    # Mostra un'intestazione per la selezione della nazionalità
    st.markdown('<div class="subheader">Nationality</div>', unsafe_allow_html=True)

    # Dizionario per memorizzare le nazionalità dei film
    nationality = {}

    # Estrai i titoli dei primi 20 film dal dataset
    movie_titles = movies['title'].head(20).tolist()

    # Recupera la nazionalità di ciascun film tramite DBpedia
    for title in movie_titles:
        nationality_list = fetch_nationality_from_dbpedia(title)  # Funzione per ottenere la nazionalità
        if nationality_list:
            nationality[title] = nationality_list  # Aggiunge la nazionalità al dizionario
        else:
            print(f"Skipping {title} as no nationality were found.")  # Messaggio di errore se non trovata nazionalità
            continue  # Salta il film se non è stata trovata la nazionalità

    print(f"Nationality dictionary: {nationality}")  # Debug: mostra il dizionario delle nazionalità

    # Estrai le nazionalità uniche per popolare la selectbox
    all_nationalities = [n.strip() for nationality_list in nationality.values() for n in nationality_list]
    unique_nationalities = sorted(set([n for n in all_nationalities if n]))  # Rimuove spazi vuoti e duplicati
    print(f"Unique nationalities: {unique_nationalities}")  # Debug: mostra le nazionalità uniche trovate
    print(f"Total unique nationalities: {len(unique_nationalities)}")  # Debug: numero totale di nazionalità uniche

    # Mostra la selectbox per selezionare una nazionalità
    selected_nationality = st.selectbox("Choose a nationality", unique_nationalities)  # Selectbox per la scelta

    return selected_nationality  # Restituisce la nazionalità selezionata


def select_popularity_preference(ratings, movies):
    """
    Funzione che permette all'utente di selezionare una preferenza in base alla popolarità del film
    (film popolari, di nicchia o indifferenti) e restituisce i film corrispondenti a tale preferenza.

    Args:
        ratings (DataFrame): DataFrame contenente le valutazioni dei film.
        movies (DataFrame): DataFrame contenente i film e i loro dettagli.

    Returns:
        DataFrame: I film filtrati in base alla preferenza di popolarità selezionata dall'utente.
    """

    # Classifica i film in base alle valutazioni (popolari, di nicchia, ecc.)
    categorized_movies = categorize_movies_by_votes(ratings, movies)

    # Mostra un'intestazione personalizzata per la selezione delle preferenze di popolarità
    st.markdown('<div class="subheader">Do you prefer popular movies or niche films?</div>', unsafe_allow_html=True)

    # Creazione di un radio button per permettere all'utente di scegliere tra film popolari, di nicchia o blockbuster
    popularity_preference = st.radio(
        "Preferisci film popolari, di nicchia o campione di incassi?",  # Testo della radio button
        ["Popular", "Niche", "Blockbuster"]  # Opzioni disponibili per la scelta
    )

    # Filtra i film in base alla preferenza selezionata (popolare, di nicchia, o blockbuster)
    filtered_movies = categorized_movies[categorized_movies['category'] == popularity_preference]

    # Visualizza la preferenza selezionata e i film corrispondenti
    st.write("Preferenza selezionata:", popularity_preference)
    st.write("Film nella categoria selezionata:", filtered_movies)

    # Restituisce i film filtrati in base alla selezione dell'utente
    return filtered_movies

def fetch_release_year_from_dbpedia(title):
    """
    Funzione per ottenere l'anno di uscita di un film da DBpedia utilizzando una query SPARQL.

    Questa funzione esegue una query SPARQL su DBpedia per ottenere l'anno di uscita di un film specificato dal titolo.
    La funzione normalizza il titolo del film per migliorare la corrispondenza e utilizza l'API SPARQL di DBpedia per
    cercare l'anno di rilascio.

    Args:
        title (str): Il titolo del film per il quale si desidera ottenere l'anno di uscita.

    Returns:
        list: Una lista contenente l'anno di uscita del film se trovato, altrimenti una lista vuota.
    """
    movie_title_clean = normalize_title(title)
    print(f"Searching for release year of: {movie_title_clean}")  # Debug

    sparql = SPARQLWrapper("https://dbpedia.org/sparql")
    sparql.setReturnFormat(JSON)

    # Query SPARQL per ottenere l'anno di uscita del film
    query = f"""
    SELECT  ?year
    WHERE {{
        ?film foaf:name "{movie_title_clean}"@en .
        ?film dbo:releaseDate ?releaseDate .
        BIND(year(?releaseDate) AS ?year)
    }}
    """

    sparql.setQuery(query)
    results = sparql.query().convert()

    print(f"Query result: {results}")  # Debug

    years = []
    if results['results']['bindings']:
        for result in results['results']['bindings']:
            year = result['year']['value']
            years.append(year)
            print(f"Release year found: {year}")  # Debug
    else:
        print(f"No release year found for: {movie_title_clean}")  # Debug

    return years

def select_decade(movies):
    """
    Funzione per permettere all'utente di selezionare una decada in base agli anni di rilascio dei film.

    Args:
        movies (DataFrame): DataFrame contenente i film e i relativi dettagli.

    Returns:
        str: La decada selezionata dall'utente.
    """

    # Mostra un'intestazione per la selezione dell'anno di rilascio
    st.markdown('<div class="subheader">Release Year</div>', unsafe_allow_html=True)

    # Dizionario per memorizzare gli anni di rilascio dei film
    years = {}

    # Estrai i titoli dei primi 20 film dal dataset
    movie_titles = movies['title'].head(20).tolist()

    # Recupera l'anno di rilascio di ogni film tramite DBpedia
    for title in movie_titles:
        years_list = fetch_release_year_from_dbpedia(title)  # Funzione per ottenere l'anno di rilascio
        if years_list:
            years[title] = years_list  # Aggiunge l'anno di rilascio al dizionario
        else:
            print(f"Skipping {title} as no nationality were found.")  # Messaggio di errore se non c'è anno
            continue  # Salta il film se non è stato trovato l'anno

    print(f"Year dictionary: {years}")  # Debug: mostra il dizionario con gli anni di rilascio

    # Estrai gli anni unici e rimuovi eventuali spazi vuoti
    all_years = [n.strip() for years_list in years.values() for n in years_list]
    unique_years = sorted(set([n for n in all_years if n]))  # Ordina gli anni e rimuove duplicati
    print(f"Unique year: {unique_years}")  # Debug: mostra gli anni unici
    print(f"Total unique year: {len(unique_years)}")  # Debug: mostra il numero totale di anni unici

    # Raggruppa gli anni in decadi (es. '50s, '60s, etc.)
    group_years_by_decade(years)

    # Raggruppa gli anni unici in base alla decada
    grouped_years = group_years_by_decade(unique_years)

    # Mostra una selectbox con le decadi disponibili
    decades = list(grouped_years.keys())  # Estrai le chiavi (decadi) dal dizionario
    selected_decade = st.selectbox("Choose a decade", decades)  # Mostra la selectbox per la scelta della decada

    return selected_decade  # Restituisce la decada selezionata dall'utente

def group_years_by_decade(years):
    """
    Funzione per raggruppare gli anni per decada.

    Args:
        years (list): Lista di anni da raggruppare.

    Returns:
        dict: Un dizionario con le decadi come chiavi e le liste di anni associati a ciascuna decada.
    """

    # Dizionario per memorizzare gli anni raggruppati per decada
    grouped_years = {}

    # Itera su ogni anno nella lista
    for year in years:
        try:
            # Converte l'anno in intero
            year = int(year)

            # Calcola la decada (ad esempio 1950, 1960, 1970, ...)
            decade = (year // 10) * 10
            decade_str = f"{decade}'s"  # Rappresenta la decada come stringa (es. '60s)

            # Aggiungi l'anno alla lista corrispondente alla sua decada
            if decade_str not in grouped_years:
                grouped_years[decade_str] = []  # Se la decada non esiste, la crea
            grouped_years[decade_str].append(year)  # Aggiungi l'anno alla decada

        except ValueError:
            # Se non è possibile convertire l'anno, lo ignora (in caso di valori non validi)
            continue

            # Restituisce il dizionario con gli anni raggruppati per decada
    return grouped_years

def select_duration(movies):
    """
    Funzione per permettere all'utente di selezionare la durata preferita di un film.

    Args:
        movies (DataFrame): DataFrame contenente la lista dei film.

    Returns:
        str: Categoria di durata selezionata dall'utente.
    """

    # Mostra un'intestazione personalizzata per la selezione della durata
    st.markdown('<div class="subheader">Preferred Movie Duration</div>', unsafe_allow_html=True)

    # Dizionario per memorizzare la durata dei film
    movie_durations = {}

    # Estrai i titoli dei primi 20 film dal dataset
    movie_titles = movies['title'].head(20).tolist()

    # Recupera la durata di ogni film tramite DBpedia
    for title in movie_titles:
        runtimes = fetch_runtime_from_dbpedia(title)  # Funzione per ottenere la durata
        if runtimes:
            movie_durations[title] = runtimes  # Aggiunge il runtime al dizionario
        else:
            print(f"Skipping {title} as no runtime was found.")  # Debug: nessuna durata trovata

    print(f"Movie durations: {movie_durations}")  # Debug: mostra le durate recuperate

    # Liste per classificare i film in base alla durata
    short_movies = []  # Film < 90 minuti
    medium_movies = []  # Film tra 90 e 150 minuti
    long_movies = []  # Film > 150 minuti

    # Analizza la durata di ogni film e lo classifica
    for title, runtimes in movie_durations.items():
        for runtime in runtimes:
            try:
                # Converte il runtime da secondi a minuti
                runtime_minutes = float(runtime) / 60
                print(f"{title} - Runtime in minutes: {runtime_minutes}")  # Debug: mostra la durata convertita

                # Classifica il film in base alla durata
                if runtime_minutes < 90:
                    short_movies.append(title)
                elif 90 <= runtime_minutes <= 150:
                    medium_movies.append(title)
                elif runtime_minutes > 150:
                    long_movies.append(title)
            except ValueError as e:
                print(f"Error converting runtime for {title}: {e}")  # Debug: errore di conversione

    # Creazione di un'opzione a radio button per la selezione della durata preferita
    duration = st.radio(
        "Choose duration:",
        ["Short (< 90 min)", "Medium (90-150 min)", "Long (> 150 min)"]
    )

    return duration

def map_tags_to_categories(tags):
    """
    Funzione per mappare i tag ai generi di film.

    Questa funzione prende una lista di tag associati ai film e li categorizza in base a parole chiave specifiche
    per vari generi cinematografici. Ogni tag viene confrontato con un set di parole chiave per determinare
    in quale categoria di film appartiene.

    Args:
        tags (pd.DataFrame): Un DataFrame contenente i tag associati ai film. Si presume che il DataFrame
                              abbia una colonna chiamata 'tag' contenente le stringhe dei tag.

    Returns:
        dict: Un dizionario con categorie di film come chiavi (es. "Action Movies", "Comedy Movies")
              e una lista dei tag che appartengono a ciascuna categoria come valori.
    """
    # Parole chiave per le categorie
    action_keywords = ["action", "adventure", "thriller", "fight", "battle"]
    comedy_keywords = ["comedy", "romantic", "funny", "humor"]
    drama_keywords = ["drama", "romance", "emotional", "serious"]
    sci_fi_keywords = ["sci-fi", "fantasy", "space", "alien", "future"]
    horror_keywords = ["horror", "thriller", "scream", "scary", "fear"]

    # Dizionario per mappare i tag alle categorie
    tag_categories = {
        "Action Movies": [],
        "Comedy Movies": [],
        "Drama Movies": [],
        "Sci-Fi Movies": [],
        "Horror Movies": []
    }

    # Raggruppa i tag in base alla parola chiave
    for tag in tags['tag']:
        if any(keyword in tag.lower() for keyword in action_keywords):
            tag_categories["Action Movies"].append(tag)
        elif any(keyword in tag.lower() for keyword in comedy_keywords):
            tag_categories["Comedy Movies"].append(tag)
        elif any(keyword in tag.lower() for keyword in drama_keywords):
            tag_categories["Drama Movies"].append(tag)
        elif any(keyword in tag.lower() for keyword in sci_fi_keywords):
            tag_categories["Sci-Fi Movies"].append(tag)
        elif any(keyword in tag.lower() for keyword in horror_keywords):
            tag_categories["Horror Movies"].append(tag)

    return tag_categories

def select_tags(tags):
    """
    Funzione che permette all'utente di selezionare una categoria di genere cinematografico
    sulla base dei tag disponibili.

    Args:
        tags (list): Lista di tag associati ai film.

    Returns:
        str: La categoria di genere selezionata dall'utente.
    """

    # Mappa i tag forniti alle relative categorie di genere
    tag_categories = map_tags_to_categories(tags)

    # Mostra un'intestazione personalizzata con markdown e HTML per fornire un contesto all'utente
    st.markdown('<div class="subheader"> What aspects would you like to find in the film? </div>',
                unsafe_allow_html=True)

    # Crea una select box in Streamlit per permettere all'utente di selezionare una categoria di genere
    selected_tags = st.selectbox(
        "Select a genre category:",  # Testo della select box
        options=list(tag_categories.keys())  # Opzioni disponibili (categorie di genere mappate dai tag)
    )

    # Restituisce la categoria selezionata dall'utente
    return selected_tags

def save_and_navigate_to_results(selected_genres, selected_director, selected_actors, selected_nationality, filtered_movies, selected_decade, duration, selected_tags):
    # Salva le scelte nei criteri di sessione
    st.session_state.selected_genres = selected_genres
    st.session_state.selected_director = selected_director
    st.session_state.selected_actors = selected_actors
    st.session_state.selected_nationality = selected_nationality
    st.session_state.filtered_movies = filtered_movies
    st.session_state.selected_decade = selected_decade
    st.session_state.duration = duration
    st.session_state.selected_tags = selected_tags

    # Stampa i criteri salvati per il debug
    st.write("Selected Genres:", st.session_state.selected_genres)
    st.write("Selected Director:", st.session_state.selected_director)
    st.write("Selected Actors:", st.session_state.selected_actors)
    st.write("Selected Nationality:", st.session_state.selected_nationality)
    st.write("Filtered Movies:", st.session_state.filtered_movies)
    st.write("Selected Decade:", st.session_state.selected_decade)
    st.write("Duration:", st.session_state.duration)
    st.write("Selected Tags:", st.session_state.selected_tags)

    # Passa alla pagina dei risultati
    st.session_state.page = "results"
