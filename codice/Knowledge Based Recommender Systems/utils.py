import pandas as pd
import re
import streamlit as st
from rdflib import Graph
from urllib.parse import urlparse

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

def is_valid_uri(uri):
    """
    Funzione per verificare se una URI è valida.
    """
    try:
        result = urlparse(uri)
        return all([result.scheme, result.netloc])  # Controlla se la URI ha uno schema e un netloc validi
    except Exception as e:
        return False

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
    selected_genres = st.multiselect(" 🎞️ Choose your preferred genres ( 1 or more)",
                                     unique_genres)  # Multiselect per i generi

    return selected_genres  # Restituisce la lista di generi selezionati

def load_movies_and_directors_from_ttl(file_path, movies_dataset):
    """
    Carica il file RDF/Turtle e recupera i film e i loro registi,
    filtrando solo quelli presenti nel dataset `movies`.

    Args:
        file_path (str): Percorso del file Turtle contenente i dati dei film.
        movies_dataset (pd.DataFrame): Dataset dei film da confrontare.

    Returns:
        dict: Dizionario {titolo_film: [registi]} con solo i film presenti nel dataset.
    """
    g = Graph()
    g.parse(file_path, format="turtle")

    movies_dict = {}

    query = """
        SELECT DISTINCT ?filmName ?director WHERE {
            ?film rdfs:label ?filmName .
            ?film dbo:director ?director .
            FILTER (lang(?filmName) = "en")
        }
    """

    results = g.query(query)

    # Normalizza i titoli dei film per il confronto (rimuovendo l'anno tra parentesi)
    dataset_movie_titles = set(movies_dataset['title'].apply(lambda x: normalize_title(x)).str.lower().tolist())

    for row in results:
        if row[0] and row[1]:  # Evita valori nulli
            # Normalizza il titolo del film (rimuovendo l'anno tra parentesi)
            film_name = normalize_title(str(row[0]))  # Chiamata alla funzione normalize_title

            # Verifica che l'URI del regista sia valido
            director_uri = str(row[1])
            if not is_valid_uri(director_uri):  # Se l'URI non è valido, salta l'iterazione
                continue

            director = str(row[1]).rsplit("/", 1)[-1].replace("_", " ")

            # Rimuovi spazi extra e metti tutto in minuscolo per un confronto robusto
            film_name_cleaned = film_name.strip().lower()

            # Filtra solo i film presenti nel dataset
            if film_name_cleaned in dataset_movie_titles:
                if film_name in movies_dict:
                    movies_dict[film_name].append(director)
                else:
                    movies_dict[film_name] = [director]

    return movies_dict

def display_director_selection(movies):
    """
    Interfaccia utente per selezionare un regista e visualizzare i film che ha diretto.
    """
    st.markdown('<div class="subheader"> Which director do you prefer?</div>', unsafe_allow_html=True)

    # **Carica i film e registi dal file RDF, filtrati per dataset**
    movies_dict = load_movies_and_directors_from_ttl("../../../movies_ontology.ttl", movies)


    # **Crea una lista di registi unici dal dizionario**
    directors = sorted(set(director for directors in movies_dict.values() for director in directors))

    # **Aggiungi "Choose an option" come opzione predefinita**
    directors.insert(0, "Choose an option")

    if directors:
        # **Selezione del regista**
        selected_director = st.selectbox("🎬 Choose a director:", directors)

        # **Se l'utente non seleziona nulla (ovvero "Choose an option"), restituiamo None**
        if selected_director == "Choose an option":
            selected_director = None
    else:
        st.error("⚠️ No directors found in the dataset.")

    return selected_director


def load_movies_and_actor_from_ttl(file_path, movies_dataset):
    """
    Carica il file RDF/Turtle e recupera i film e i loro registi,
    filtrando solo quelli presenti nel dataset `movies`.

    Args:
        file_path (str): Percorso del file Turtle contenente i dati dei film.
        movies_dataset (pd.DataFrame): Dataset dei film da confrontare.

    Returns:
        dict: Dizionario {titolo_film: [registi]} con solo i film presenti nel dataset.
    """
    g = Graph()
    g.parse(file_path, format="turtle")

    movies_act = {}

    query = """
        SELECT DISTINCT ?filmName ?starring WHERE {
            ?film rdfs:label ?filmName .
            ?film dbo:starring ?starring .
            FILTER (lang(?filmName) = "en")
        }
    """

    results = g.query(query)

    # Normalizza i titoli dei film per il confronto (rimuovendo l'anno tra parentesi)
    dataset_movie_titles = set(movies_dataset['title'].apply(lambda x: normalize_title(x)).str.lower().tolist())

    for row in results:
        if row[0] and row[1]:  # Evita valori nulli
            # Normalizza il titolo del film (rimuovendo l'anno tra parentesi)
            film_name = normalize_title(str(row[0]))  # Chiamata alla funzione normalize_title

            # Verifica che l'URI del regista sia valido
            actor_uri = str(row[1])
            if not is_valid_uri(actor_uri):  # Se l'URI non è valido, salta l'iterazione
                continue

            actor = str(row[1]).rsplit("/", 1)[-1].replace("_", " ")

            # Rimuovi spazi extra e metti tutto in minuscolo per un confronto robusto
            film_name_cleaned = film_name.strip().lower()

            # Filtra solo i film presenti nel dataset
            if film_name_cleaned in dataset_movie_titles:
                if film_name in movies_act:
                    movies_act[film_name].append(actor)
                else:
                    movies_act[film_name] = [actor]

    return movies_act

def display_actor_selection(movies):
    """
    Interfaccia utente per selezionare un regista e visualizzare i film che ha diretto.
    """
    st.markdown('<div class="subheader"> Which actor do you prefer?</div>', unsafe_allow_html=True)

    # **Carica i film e registi dal file RDF, filtrati per dataset**
    movies_act = load_movies_and_actor_from_ttl("../../../movies_ontology.ttl", movies)

    # **Crea una lista di attori unici dal dizionario**
    directors = sorted(set(director for directors in movies_act.values() for director in directors))

    if directors:
        # **Selezione gli attori**
        selected_actor = st.multiselect(" 🎭 Choose a actor (1 or more):", directors)

    else:
        st.error("⚠️ No directors found in the dataset.")

    return selected_actor


def load_movies_and_nationality_from_ttl(file_path, movies_dataset):
    """
    Carica il file RDF/Turtle e recupera i film, i loro attori e la loro nazionalità,
    filtrando solo quelli presenti nel dataset `movies`.

    Args:
        file_path (str): Percorso del file Turtle contenente i dati dei film.
        movies_dataset (pd.DataFrame): Dataset dei film da confrontare.

    Returns:
        dict: Dizionario {titolo_film: {"actors": [attori], "country": [nazione]}}
        con solo i film presenti nel dataset.
    """
    g = Graph()
    g.parse(file_path, format="turtle")

    movies_nationality = {}

    query = """
        SELECT DISTINCT ?filmName ?country WHERE {
            ?film rdfs:label ?filmName .
            ?film dbo:country ?country .
            FILTER (lang(?filmName) = "en")
        }
    """

    results = g.query(query)

    # Normalizza i titoli dei film per il confronto (rimuovendo l'anno tra parentesi)
    dataset_movie_titles = set(movies_dataset['title'].apply(lambda x: normalize_title(x)).str.lower().tolist())

    for row in results:
        if row[0]:  # Evita valori nulli
            # Normalizza il titolo del film (rimuovendo l'anno tra parentesi)
            film_name = normalize_title(str(row[0]))

            # Estrai la nazionalità (paese)
            country = str(row[1]) if row[1] else None

            # Rimuovi spazi extra e metti tutto in minuscolo per un confronto robusto
            film_name_cleaned = film_name.strip().lower()

            # Gestisci URL dei paesi e rimuovi duplicati
            if country:
                # Se il paese è un URL, rimuovilo o sostituiscilo con il nome corretto
                if country.startswith("http://dbpedia.org/resource/"):
                    # Estrarre il nome del paese dalla URL (rimuovendo il prefisso)
                    country = country.split("/")[-1].replace("_", " ").title()

                # Se il paese è "N/A", escludilo
                if country == "N/A":
                    country = None

            # Verifica che il film sia presente nel dataset
            if film_name_cleaned in dataset_movie_titles:
                if film_name not in movies_nationality:
                    movies_nationality[film_name] = {"country": set()}  # Usa un set per evitare duplicati

                # Aggiungi la nazionalità solo se non è "N/A" e non è già presente nel set
                if country:
                    movies_nationality[film_name]["country"].add(country)  # Aggiunge solo se non esiste già

    return movies_nationality


def display_nationality_selection(movies):
    """
    Interfaccia utente per selezionare una nazionalità e visualizzare i film associati.
    """
    st.markdown('<div class="subheader"> Which country do you prefer?</div>', unsafe_allow_html=True)

    ratings = pd.read_csv("../../dataset/archive/ratings.csv")

    # Carica i film e le nazionalità dal file RDF, filtrati per dataset
    movies_nationality = load_movies_and_nationality_from_ttl("../../../movies_ontology.ttl", movies)

    # Crea una lista unica di tutte le nazionalità per i film presenti nel dataset
    all_countries = set()
    for movie in movies_nationality.values():
        all_countries.update(movie["country"])

    # Aggiungi "Choose an option" come prima opzione
    all_countries = sorted(all_countries)  # Ordina i paesi
    all_countries.insert(0, "Choose an option")  # Aggiungi "Choose an option" come prima voce

    # Selezione della nazionalità tramite selectbox
    if all_countries:
        selected_country = st.selectbox("🌍 Choose a country:", all_countries)
    else:
        st.error("⚠️ No countries found in the dataset.")
        selected_country = "Choose an option"

    return selected_country


def load_movies_and_runtime_from_ttl(file_path, movies_dataset):
    """
    Carica il file RDF/Turtle e recupera i film e la loro durata,
    filtrando solo quelli presenti nel dataset `movies`.

    Args:
        file_path (str): Percorso del file Turtle contenente i dati dei film.
        movies_dataset (pd.DataFrame): Dataset dei film da confrontare.

    Returns:
        dict: Dizionario {titolo_film: {"runtime": durata}} con solo i film presenti nel dataset.
    """
    g = Graph()
    g.parse(file_path, format="turtle")

    movies_runtime = {}

    query = """
        SELECT DISTINCT ?filmName ?runtime WHERE {
            ?film rdfs:label ?filmName .
            ?film dbo:runtime ?runtime .
            FILTER (lang(?filmName) = "en")
        }
    """

    results = g.query(query)

    # Normalizza i titoli dei film per il confronto (rimuovendo l'anno tra parentesi)
    dataset_movie_titles = set(movies_dataset['title'].apply(lambda x: normalize_title(x)).str.lower().tolist())

    for row in results:
        if row[0] and row[1]:  # Verifica che ci siano valori validi
            # Normalizza il titolo del film (rimuovendo l'anno tra parentesi)
            film_name = normalize_title(str(row[0]))

            # Verifica che la durata sia un numero valido
            try:
                runtime = float(row[1]) if row[1] else None
            except ValueError:
                runtime = None  # Se non è un numero valido, imposta la durata a None

            # Rimuovi spazi extra e metti tutto in minuscolo per un confronto robusto
            film_name_cleaned = film_name.strip().lower()

            # Filtra solo i film presenti nel dataset
            if film_name_cleaned in dataset_movie_titles and runtime is not None:
                movies_runtime[film_name] = {"runtime": runtime}

    return movies_runtime

def display_runtime_selection(movies):
    """
    Interfaccia utente per selezionare la durata e visualizzare i film associati.
    """
    st.markdown('<div class="subheader"> Choose a movie runtime category:</div>', unsafe_allow_html=True)

    # Carica i film e le durate dal file RDF, filtrati per dataset
    movies_runtime = load_movies_and_runtime_from_ttl("../../../movies_ontology.ttl", movies)

    # Suddividi i film in base alla durata
    short_movies = []  # Film < 90 minuti
    medium_movies = []  # Film tra 90 e 150 minuti
    long_movies = []  # Film > 150 minuti

    for movie, data in movies_runtime.items():
        runtime = data["runtime"]
        if runtime:
            if runtime < 5400:  # < 90 minuti
                short_movies.append(movie)
            elif 5400 <= runtime <= 9000:  # 90-150 minuti
                medium_movies.append(movie)
            else:  # > 150 minuti
                long_movies.append(movie)

    # Lista delle categorie di durata
    runtime_film = ["Short", "Medium", "Long"]

    # Selezione della categoria di durata tramite radio button
    selected_runtime = st.radio("⏳ Choose a runtime category:", runtime_film)

    return selected_runtime


def load_movies_and_release_year_from_ttl(file_path, movies_dataset):
    """
    Carica il file RDF/Turtle e recupera i film e il loro anno di rilascio,
    filtrando solo quelli presenti nel dataset movies.

    Args:
        file_path (str): Percorso del file Turtle contenente i dati dei film.
        movies_dataset (pd.DataFrame): Dataset dei film da confrontare.

    Returns:
        dict: Dizionario {titolo_film: {"released": anno}} con solo i film presenti nel dataset.
    """
    g = Graph()
    g.parse(file_path, format="turtle")

    movies_release = {}

    query = """
        SELECT DISTINCT ?filmName ?released WHERE {
            ?film rdfs:label ?filmName .
            ?film dbp:released  ?released .
            FILTER (lang(?filmName) = "en")
        }
    """

    results = g.query(query)

    dataset_movie_titles = set(movies_dataset['title'].apply(lambda x: normalize_title(x)).tolist())

    for row in results:
        if row[0] and row[1]:  # Verifica che ci siano valori validi
            film_name = normalize_title(str(row[0]))  # Normalizza il titolo
            released = str(row[1])[:4]  # Prendi solo l'anno (i primi 4 caratteri)

            # Verifica che il film sia presente nel dataset
            if film_name in dataset_movie_titles and released:
                movies_release[film_name] = {"released": released}

    return movies_release


def group_movies_by_decade(movies_release):
    """
    Raggruppa i film per decennio (40s, 50s, 70s, 80s, 90s, etc.)

    Args:
        movies_release (dict): Dizionario con film e anni di rilascio.

    Returns:
        dict: Dizionario con i decenni come chiavi e i film associati come valori.
    """
    decades = {
        "70s": [],
        "80s": [],
        "90s": [],
    }

    for film, details in movies_release.items():
        year = int(details["released"])

        # Assegna il film al decennio corretto
        if 1970 <= year < 1980:
            decades["70s"].append(film)
        elif 1980 <= year < 1990:
            decades["80s"].append(film)
        elif 1990 <= year < 2000:
            decades["90s"].append(film)
        elif 2000 <= year < 2010:
            decades["2000s"].append(film)
        elif 2010 <= year < 2020:
            decades["2010s"].append(film)
        elif 2020 <= year < 2030:
            decades["2020s"].append(film)

    return decades

def display_movies_by_decade(movies_dataset):
    """
    Interfaccia utente per selezionare un decennio e visualizzare i film associati.
    """

    st.markdown('<div class="subheader"> Choose year of production : </div>', unsafe_allow_html=True)

    # Carica i film e gli anni di rilascio dal file RDF, filtrati per il dataset
    movies_release = load_movies_and_release_year_from_ttl("../../../movies_ontology.ttl", movies_dataset)

    if not movies_release:
        st.error("⚠️ No movies found in the RDF dataset or in the provided file.")
        return

    # Raggruppa i film per decennio
    grouped_movies = group_movies_by_decade(movies_release)

    # Crea una lista di decenni
    decades_list = list(grouped_movies.keys())

    # Aggiungi "Choose an option" come primo elemento
    decades_list.insert(0, "Choose an option")

    if decades_list:
        # Seleziona il decennio dal selectbox con etichetta
        selected_decade = st.selectbox("📅 Choose a decade:", decades_list)

    else:
        st.error("⚠️ No decade found in the dataset.")

    return selected_decade

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

def display_popularity_preference(ratings, movies):
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
        "",  # Testo della radio button
        ["Popular", "Niche", "Blockbuster"]  # Opzioni disponibili per la scelta
    )

    # Filtra i film in base alla preferenza selezionata (popolare, di nicchia, o blockbuster)
    filtered_movies = categorized_movies[categorized_movies['category'] == popularity_preference]

    # Visualizza la preferenza selezionata e i film corrispondenti
    st.write("Preferenza selezionata:", popularity_preference)
    st.write("Film nella categoria selezionata:", filtered_movies)

    # Restituisce i film filtrati in base alla selezione dell'utente
    return filtered_movies

def save_and_navigate_to_results(selected_genres, selected_director, selected_actors, selected_nationality, filtered_movies, selected_decade, duration):
    """
       Salva le scelte dell'utente nella sessione di Streamlit e naviga alla pagina dei risultati.

       :param selected_genres: Lista dei generi selezionati
       :param selected_director: Lista dei registi selezionati
       :param selected_actors: Lista degli attori selezionati
       :param selected_nationality: Nazionalità selezionata
       :param filtered_movies: Lista di film filtrati
       :param selected_decade: Decade selezionata
       :param duration: Durata selezionata
       :param budget: Budget selezionato (opzionale)
       :param language: Lingua del film selezionata (opzionale)
       """

    # Salva le scelte nei criteri di sessione
    st.session_state.selected_genres = selected_genres
    st.session_state.selected_director = selected_director
    st.session_state.selected_actors = selected_actors
    st.session_state.selected_nationality = selected_nationality
    st.session_state.filtered_movies = filtered_movies
    st.session_state.selected_decade = selected_decade
    st.session_state.duration = duration

    # Stampa i criteri salvati per il debug
    st.write("Selected Genres:", st.session_state.selected_genres)
    st.write("Selected Director:", st.session_state.selected_director)
    st.write("Selected Actors:", st.session_state.selected_actors)
    st.write("Selected Nationality:", st.session_state.selected_nationality)
    st.write("Filtered Movies:", st.session_state.filtered_movies)
    st.write("Selected Decade:", st.session_state.selected_decade)
    st.write("Duration:", st.session_state.duration)

    # Passa alla pagina dei risultati
    st.session_state.page = "results"
