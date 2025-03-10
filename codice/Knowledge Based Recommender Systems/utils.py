from __future__ import annotations
from typing import Any
import pandas as pd
import re
import streamlit as st
from rdflib import Graph
from urllib.parse import urlparse
import rdflib

# """
# Modulo di utilità per la gestione e il filtraggio dei film nell'applicazione di raccomandazione.
#
# Fornisce funzioni per il caricamento dei dati, la selezione delle preferenze dell'utente,
# la gestione delle query su RDF e l'estrazione delle informazioni dai dataset.
#
# Funzioni principali:
# - **Gestione della UI e delle preferenze utente:**
#   - `load_css()`: Carica un foglio di stile CSS personalizzato per Streamlit.
#   - `select_genres(genres, default)`: Permette all'utente di selezionare i generi preferiti.
#   - `display_director_selection(directors, default)`: Permette di selezionare un regista preferito.
#   - `display_actor_selection(actors, default)`: Permette di selezionare attori preferiti.
#   - `display_nationality_selection(all_countries, default)`: Permette di selezionare una nazionalità preferita.
#   - `display_runtime_selection(default)`: Permette di selezionare la durata del film.
#   - `display_movies_by_decade(years, default)`: Permette di selezionare la decade di uscita del film.
#   - `display_popularity_preference(default)`: Permette di selezionare il livello di popolarità dei film.
#   - `save_user_preferences(...)`: Salva le preferenze dell'utente nella sessione di Streamlit.
#
# - **Gestione dei dati RDF:**
#   - `load_data()`: Carica i dataset di MovieLens (movies, tags, ratings).
#   - `select_informations_from_ttl(movies_dataset)`: Estrae generi, registi, attori, nazionalità e anni disponibili dal file RDF.
#   - `get_movies_from_ttl()`: Recupera i titoli dei film presenti nel dataset RDF.
#   - `extract_reference_film_info(reference_title)`: Estrae le informazioni di un film di riferimento dal file RDF.
#   - `search_similar_movies(reference_film)`: Cerca film simili a un film di riferimento selezionato dall'utente.
#
# - **Gestione e normalizzazione dei dati:**
#   - `normalize_title(movie_title)`: Normalizza i titoli dei film rimuovendo l'anno e spostando gli articoli all'inizio.
#   - `is_valid_uri(uri)`: Verifica se una URI è valida.
#   - `group_movies_by_decade(movies_release)`: Raggruppa i film per decennio.
#
# - **Stampa e debugging:**
#   - `print_recommendations(recommendations)`: Stampa i film raccomandati in un formato leggibile.
#
# Caratteristiche:
# - **Compatibilità con RDF e DBpedia**: Il modulo interagisce con un file RDF contenente i dati dei film e permette di eseguire query SPARQL.
# - **Ottimizzazione per Streamlit**: Include funzioni per la gestione della UI e il salvataggio delle preferenze utente.
# - **Supporto alla ricerca di film simili**: Consente di utilizzare un film di riferimento per ottenere suggerimenti personalizzati.
#
# Questo modulo è essenziale per la gestione dei dati e l'interfaccia utente nel sistema di raccomandazione di film.
# """

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



def select_genres(genres, default=None):
    """
    Funzione che permette all'utente di selezionare uno o più generi cinematografici preferiti.

    Args:
        movies (DataFrame): DataFrame contenente i film e i relativi dettagli.

    Returns:
        list: Una lista di generi selezionati dall'utente.
    """

    # Mostra un'intestazione per la selezione dei generi preferiti
    st.markdown('<div class="subheader"> What genres of movies do you prefer? </div>', unsafe_allow_html=True)

    # Mostra la multiselectbox per la selezione dei generi preferiti
    selected_genres = st.multiselect(" 🎞️ Choose your preferred genres ( 1 or more)",
                                    genres,
                                    default=default)  # Usa il valore di default se disponibile

    return selected_genres  # Restituisce la lista di generi selezionati

@st.cache_data
def select_informations_from_ttl(movies_dataset):
    g = Graph()
    file_path = "movies_rdf.ttl"
    g.parse(file_path, format="turtle")

    movies_dict = {}

    query = """
        SELECT DISTINCT ?filmName ?genre ?director ?actor ?country ?released
        WHERE {
            ?movie rdfs:label ?filmName .
            OPTIONAL { ?movie dbo:genre ?genre. }
            OPTIONAL { ?movie dbo:director ?director. }
            OPTIONAL { ?movie dbo:starring ?actor. }
            OPTIONAL { ?movie dbo:country ?country. }
            OPTIONAL { ?movie dbp:released ?released. }
            FILTER (lang(?filmName) = "en")
        }
    """

    results = g.query(query)

    # Normalizza i titoli dei film per il confronto
    dataset_movie_titles = set(movies_dataset['title'].apply(lambda x: normalize_title(x)).str.lower().tolist())

    # Inizializza set per ogni informazione
    genres = set()
    directors = set()
    actors = set()
    nationalities = set()
    years = set()

    for row in results:
        if row[0]:  # Verifica che il nome del film esista
            film_name = normalize_title(str(row[0]))
            film_name_cleaned = film_name.strip().lower()

            # Se il film è nel dataset, aggiungi i relativi dati ai set
            if film_name_cleaned in dataset_movie_titles:
                if row[1]:  # ?genre
                    genre = str(row[1]).rsplit("/", 1)[-1].replace("_", " ")
                    subgenres = genre.split("|")
                    for subgenre in subgenres:
                        genres.add(subgenre.strip())
                if row[2]:  # ?director
                    director = str(row[2]).rsplit("/", 1)[-1].replace("_", " ")
                    directors.add(director)
                if row[3]:  # ?actor
                    actor = str(row[3]).rsplit("/", 1)[-1].replace("_", " ")
                    actors.add(actor)
                if row[4]:  # ?country
                    nationality = str(row[4]).rsplit("/", 1)[-1].replace("_", " ")
                    nationalities.add(nationality)
                if row[5]:  # ?released
                    year = str(row[5])[:4]  # Prendi solo l'anno
                    years.add(year)

    # Ordina ciascun set e converti in liste per le combobox
    genres_list = sorted(genres)
    directors_list = sorted(directors)
    actors_list = sorted(actors)
    nationalities_list = sorted(nationalities)
    years_list = sorted(years)

    directors_list = [d for d in directors_list if d != "A"]
    nationalities_list = [c for c in nationalities_list if c != "A"]

    return genres_list, directors_list, actors_list, nationalities_list, years_list


def get_movies_from_ttl():
    """
    Carica i titoli dei film dal file TTL.

    Ritorna:
    - lista dei titoli dei film presenti nel dataset TTL.
    """
    g = rdflib.Graph()
    g.parse("movies_rdf.ttl", format="turtle")

    query = """
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?title
        WHERE {
            ?movie rdfs:label ?title .
        }
    """

    results = g.query(query)
    movie_titles = [str(row[0]) for row in results]  # Converte i risultati in una lista di stringhe

    return movie_titles


def display_director_selection(directors, default=None):
    """
    Interfaccia utente per selezionare un regista e visualizzare i film che ha diretto.
    """
    st.markdown('<div class="subheader"> Which director do you prefer?</div>', unsafe_allow_html=True)

    # # **Carica i film e registi dal file RDF, filtrati per dataset**
    # movies_dict = load_movies_and_directors_from_ttl("movies_rdf.ttl", movies)
    #

    # **Aggiungi "Choose an option" come opzione predefinita**
    directors.insert(0, "Choose an option")

    if directors:
        # **Selezione del regista**
        selected_director = st.selectbox("🎬 Choose a director:", directors, index=directors.index(default) if default in directors else 0)

        # **Se l'utente non seleziona nulla (ovvero "Choose an option"), restituiamo None**
        if selected_director == "Choose an option":
            selected_director = None
    else:
        st.error("⚠️ No directors found in the dataset.")

    return selected_director


def display_actor_selection(actors, default=None):
    """
    Interfaccia utente per selezionare un regista e visualizzare i film che ha diretto.
    """
    st.markdown('<div class="subheader"> Which actor do you prefer?</div>', unsafe_allow_html=True)


    if actors:
        # **Selezione gli attori**
        selected_actor = st.multiselect(" 🎭 Choose a actor (1 or more):", actors, default=default)

    else:
        st.error("⚠️ No directors found in the dataset.")

    return selected_actor


def display_nationality_selection(all_countries, default=None):
    """
    Interfaccia utente per selezionare una nazionalità e visualizzare i film associati.
    """
    st.markdown('<div class="subheader"> Which country do you prefer?</div>', unsafe_allow_html=True)

    # Aggiungi l’etichetta predefinita come primo elemento
    label = "Choose a country"  # Etichetta per indicare che l’utente deve scegliere
    all_countries = sorted(all_countries)
    all_countries.insert(0, label)

    # Configura il selectbox per la selezione della nazionalità
    selected_country = st.selectbox(
        "🌍 Choose a country:",
        all_countries,
        index=all_countries.index(default) if default in all_countries else 0
    )

    # Se l’utente non cambia la selezione predefinita, restituisci una stringa vuota
    if selected_country == label:
        return ""

    return selected_country


def display_runtime_selection(default=None):
    """
    Interfaccia utente per selezionare una o più durate dei film.
    """
    st.markdown('<div class="subheader"> Choose one or more movie runtime categories:</div>', unsafe_allow_html=True)

    # Se default non è passato, inizializzalo come lista vuota
    default = default or []

    # Lista delle categorie di durata
    runtime_film = ["Short", "Medium", "Long"]

    # Descrizioni ausiliarie per ogni opzione
    runtime_descriptions = {
        "Short": " (less than 1.5 hours)",
        "Medium": " (between 1.5 and 2.5 hours)",
        "Long": " (more than 2.5 hours)"
    }

    # Creazione delle checkbox per ogni opzione
    selected_runtimes = [
        runtime
        for runtime in runtime_film
        if st.checkbox(f"{runtime}{runtime_descriptions.get(runtime, '')}", value=runtime in default)
    ]

    return selected_runtimes


def group_movies_by_decade(movies_release):
    decades = {
        "1900s": [],
        "1910s": [],
        "1920s": [],
        "1930s": [],
        "1940s": [],
        "1950s": [],
        "1960s": [],
        "1970s": [],
        "1980s": [],
        "1990s": [],
        "2000s": [],
        "2010s": [],
        "2020s": [],
    }

    for year_str in movies_release:
        try:
            year = int(year_str)  # Converte la stringa in intero
        except ValueError:
            continue  # Se il valore non è un numero, lo salta

        # Assegna l'anno al decennio corretto
        if 1900 <= year < 1910:
            decades["1900s"].append(year)
        elif 1910 <= year < 1920:
            decades["1910s"].append(year)
        elif 1920 <= year < 1930:
            decades["1920s"].append(year)
        elif 1930 <= year < 1940:
            decades["1930s"].append(year)
        elif 1940 <= year < 1950:
            decades["1940s"].append(year)
        elif 1950 <= year < 1960:
            decades["1950s"].append(year)
        elif 1960 <= year < 1970:
            decades["1960s"].append(year)
        elif 1970 <= year < 1980:
            decades["1970s"].append(year)
        elif 1980 <= year < 1990:
            decades["1980s"].append(year)
        elif 1990 <= year < 2000:
            decades["1990s"].append(year)
        elif 2000 <= year < 2010:
            decades["2000s"].append(year)
        elif 2010 <= year < 2020:
            decades["2010s"].append(year)
        elif 2020 <= year < 2030:
            decades["2020s"].append(year)

    return decades


def display_movies_by_decade(years: object, default: object = None) -> str | Any:
    """
    Interfaccia utente per selezionare un decennio e visualizzare i film associati.
    """

    st.markdown('<div class="subheader"> Choose year of production : </div>', unsafe_allow_html=True)

    # Raggruppa i film per decennio
    grouped_movies = group_movies_by_decade(years)

    # Crea una lista di decenni
    decades_list = list(grouped_movies.keys())

    # Aggiungi l’opzione predefinita “Choose a decade” come primo elemento
    label = "Choose a decade"  # Etichetta per indicare che l’utente deve scegliere
    decades_list.insert(0, label)

    # Configura il selectbox per la selezione del decennio
    selected_decade = st.selectbox(
        "📅 Choose a decade:",
        decades_list,
        index=decades_list.index(default) if default in decades_list else 0
    )

    # Se l’utente non cambia la selezione predefinita, restituisci una stringa vuota
    if selected_decade == label:
        return ""

    return selected_decade


def display_popularity_preference(default=None):
    """
    Funzione che permette all'utente di selezionare una o più preferenze in base alla popolarità del film
    (film popolari, di nicchia o blockbuster).
    """
    st.markdown('<div class="subheader">Do you prefer popular movies or niche films?</div>', unsafe_allow_html=True)

    # Se default non è passato, inizializzalo come lista vuota
    default = default or []

    # Imposta lo stato iniziale di ogni checkbox in base a default
    is_popular = st.checkbox("Popular", value="Popular" in default)
    is_niche = st.checkbox("Niche", value="Niche" in default)
    is_blockbuster = st.checkbox("Blockbuster", value="Blockbuster" in default)

    # Costruisce un elenco di preferenze basate sulle selezioni effettuate dall'utente
    preferences = []
    if is_popular:
        preferences.append("Popular")
    if is_niche:
        preferences.append("Niche")
    if is_blockbuster:
        preferences.append("Blockbuster")

    return preferences


def save_user_preferences(selected_genres, selected_director, selected_actors, selected_nationality, selected_popularity, selected_decade, duration,
                          ):
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
    st.session_state.filtered_movies = selected_popularity
    st.session_state.selected_decade = selected_decade
    st.session_state.duration = duration


def extract_reference_film_info(reference_title):
    g = Graph()
    file_path = "movies_rdf.ttl"
    g.parse(file_path, format="turtle")

    # Normalizza il titolo di riferimento per il confronto
    normalized_reference_title = normalize_title(reference_title).strip().lower()

    # Inizializza i contenitori per le informazioni
    reference_info = {
        "genres": set(),
        "director": "",
        "actors": set(),
        "countries": "",
        "year": None,
        "runtime": None,
        "views": None
    }

    query = """
        SELECT DISTINCT ?filmName ?genre ?director ?actor ?country ?released ?runtime ?views
        WHERE {
            ?movie rdfs:label ?filmName .
            OPTIONAL { ?movie dbo:genre ?genre. }
            OPTIONAL { ?movie dbo:director ?director. }
            OPTIONAL { ?movie dbo:starring ?actor. }
            OPTIONAL { ?movie dbo:country ?country. }
            OPTIONAL { ?movie dbp:released ?released. }
            OPTIONAL { ?movie dbo:runtime ?runtime. }
            OPTIONAL { ?movie dbp:views ?views. }
            FILTER (lang(?filmName) = "en")
        }
    """

    results = g.query(query)

    for row in results:
        if row[0]:  # Verifica che il nome del film esista
            # Normalizza il titolo del film corrente
            film_name = normalize_title(str(row[0])).strip().lower()

            # Se il titolo corrente corrisponde al titolo di riferimento, raccogli le informazioni
            if film_name == normalized_reference_title:
                if row[1]:  # ?genre
                    genre = str(row[1]).rsplit("/", 1)[-1].replace("_", " ")
                    subgenres = genre.split("|")
                    for subgenre in subgenres:
                        reference_info["genres"].add(subgenre.strip())
                if row[2]:  # ?director
                    director = str(row[2]).rsplit("/", 1)[-1].replace("_", " ")
                    reference_info["director"] = director
                if row[3]:  # ?actor
                    actor = str(row[3]).rsplit("/", 1)[-1].replace("_", " ")
                    reference_info["actors"].add(actor)
                if row[4]:  # ?country
                    country = str(row[4]).rsplit("/", 1)[-1].replace("_", " ")
                    reference_info["countries"] = country
                if row[5]:  # ?released
                    year = str(row[5])[:4]  # Prendi solo l'anno
                    try:
                        reference_info["year"] = int(year)
                    except ValueError:
                        reference_info["year"] = None
                if row[6]:  # ?runtime
                    runtime = str(row[6]).strip()
                    try:
                        reference_info["runtime"] = int(float(runtime))
                    except ValueError:
                        reference_info["runtime"] = None
                if row[7]:  # ?views
                    views = str(row[7]).strip()
                    try:
                        reference_info["views"] = int(float(views))
                    except ValueError:
                        reference_info["views"] = None

                # Abbiamo trovato il film di riferimento, non serve continuare
                break

    # Trasforma l'anno in un decennio, se disponibile
    if reference_info["year"]:
        reference_info["year"] = f"{reference_info['year'] // 10 * 10}s"

    # Converte le views in una categoria
    if reference_info["views"] is not None:
        if reference_info["views"] < 30:
            reference_info["views"] = ["Short"]
        elif 30 <= reference_info["views"] <= 100:
            reference_info["views"] = ["Popular"]
        else:
            reference_info["views"] = ["Blockbuster"]

    # Converte il runtime in una categoria
    if reference_info["runtime"] is not None:
        if reference_info["runtime"] < 5400:
            reference_info["runtime"] = ["Short"]
        elif 5400 <= reference_info["runtime"] <= 9000:
            reference_info["runtime"] = ["Medium"]
        else:
            reference_info["runtime"] = ["Long"]

    # Converte i generi in una lista ordinata per la coerenza
    reference_info["genres"] = sorted(reference_info["genres"])

    # Gli altri campi sono già nel formato desiderato
    return reference_info



def search_similar_movies(reference_film):
    print(f"DEBUG: Funzione chiamata con film '{reference_film}'")  # ✅ Verifica che la funzione venga chiamata

    informations = extract_reference_film_info(reference_film)
    print(f"DEBUG: Informazioni estratte: {informations}")  # ✅ Verifica che `extract_reference_film_info()` funzioni

    # Aggiorna lo stato della sessione Streamlit con i nuovi formati
    st.session_state.selected_genres = informations["genres"]
    st.session_state.selected_director = informations["director"]
    st.session_state.selected_actors = informations["actors"]
    st.session_state.selected_nationality = informations["countries"]
    st.session_state.filtered_movies = informations["views"]
    st.session_state.selected_decade = informations["year"]
    st.session_state.duration = informations["runtime"]

    st.session_state.excluded_film = reference_film

    # Passa alla pagina dei risultati
    st.session_state.page = "results"
    print("DEBUG: Stato aggiornato per passare alla pagina dei risultati")  # ✅ Verifica che la pagina venga aggiornata

    st.rerun()


def print_recommendations(recommendations):
    """
    Stampa le raccomandazioni in un formato leggibile.

    Parametri:
    - recommendations (dict): Dizionario contenente le raccomandazioni con i dettagli dei film.
    """

    if not isinstance(recommendations, dict):
        print(f"❌ Errore: recommendations NON è un dizionario, ma {type(recommendations)}")
        return

    if len(recommendations) == 0:
        print("⚠️ Nessun film trovato.")
        return

    for title, details in recommendations.items():
        if not isinstance(details, dict):
            print(f"⚠️ Attenzione: '{title}' non ha dettagli validi: {details}")
            continue

        # Recuperiamo i dettagli e assicuriamoci che non siano `None`
        genres = str(details.get('genres', 'N/A')).strip()
        director = str(details.get('director', 'N/A')).strip()
        actors = str(details.get('actors', 'N/A')).strip()
        country = str(details.get('country', 'N/A')).strip()
        year = str(details.get('year', 'N/A')).strip()
        abstract = str(details.get('abstract', 'N/A')).strip()

        # Se alcuni dettagli contengono URL di DBpedia, estraiamo solo il nome alla fine
        if director.startswith("http"):
            director = director.split("/")[-1].replace("_", " ")
        if actors.startswith("http"):
            actors = actors.split("/")[-1].replace("_", " ")
        if country.startswith("http"):
            country = country.split("/")[-1].replace("_", " ")

        print("\n🎬 Title:", details.get('title', title))  # Usa la chiave se manca il titolo
        print("⭐ Score:", details.get('score', 'N/A'))
        print("📖 Explanation:", details.get('explanation', 'N/A'))
        print("🎭 Genres:", genres)
        print("🎬 Director:", director)
        print("👥 Actors:", actors)
        print("🌍 Country:", country)
        print("📆 Year:", year)
        print("📜 Abstract:", abstract)
        print("-" * 60)
