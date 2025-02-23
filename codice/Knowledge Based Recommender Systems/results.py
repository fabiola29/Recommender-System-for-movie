import streamlit as st
from SPARQLWrapper import SPARQLWrapper, JSON

# Funzione per eseguire la query su DBpedia
def query_movies(selected_genres, selected_director, selected_actors, selected_nationality, selected_decade, duration, selected_tags):

    """
        Funzione per eseguire una query SPARQL su DBpedia per recuperare film che soddisfano i criteri selezionati.

        Args:
            selected_genres (list): Lista di generi di film da filtrare (ad esempio, ['Action', 'Comedy']).
            selected_director (list): Lista di registi da filtrare (ad esempio, ['Steven Spielberg']).
            selected_actors (list): Lista di attori da filtrare (ad esempio, ['Tom Hanks', 'Meryl Streep']).
            selected_nationality (str): Nazionalità del film (ad esempio, 'United States').
            selected_decade (str): Decade in cui il film è stato rilasciato (ad esempio, '1990s').
            duration (str): Durata del film, che può essere 'Short (< 90 min)', 'Medium (90-150 min)', o 'Long (> 150 min)'.
            selected_tags (list): Lista di tag/temi del film da filtrare (ad esempio, ['Adventure', 'Drama']).

        Returns:
            list: Una lista di dizionari, dove ogni dizionario rappresenta un film e contiene i seguenti campi:
                - "title": Titolo del film
                - "abstract": Descrizione breve del film (se disponibile)
                - "director": Nome del regista del film
                - "actors": Nome degli attori principali
                - "year": Anno di rilascio del film
                - "nationality": Nazionalità del film
                - "duration": Durata del film in minuti
        """

    endpoint = "https://dbpedia.org/sparql"
    sparql = SPARQLWrapper(endpoint)

    filters = []

    # Filtro per i generi
    if selected_genres:
        genre_filters = " || ".join(f"?movie dbo:genre <http://dbpedia.org/resource/{genre.replace(' ', '_')}>" for genre in selected_genres)
        filters.append(f"({genre_filters})")

    # Filtro per il regista
    if selected_director:
        director_filters = " || ".join(f"?movie dbo:director <http://dbpedia.org/resource/{director.replace(' ', '_')}>" for director in selected_director)
        filters.append(f"({director_filters})")

    # Filtro per gli attori
    if selected_actors:
        actors_filters = " || ".join(f"?movie dbo:starring <http://dbpedia.org/resource/{actor.replace(' ', '_')}>" for actor in selected_actors)
        filters.append(f"({actors_filters})")

    # Filtro per la nazionalità
    if selected_nationality:
        filters.append(f"?movie dbo:country <http://dbpedia.org/resource/{selected_nationality.replace(' ', '_')}>")

    # Filtro per la decade
    if selected_decade:
        decade_start = int(selected_decade[:4])
        filters.append(f"FILTER(YEAR(?releaseDate) >= {decade_start} && YEAR(?releaseDate) < {decade_start + 10})")

    # Filtro per la durata
    if duration:
        if duration == "Short (< 90 min)":
            filters.append("FILTER(?duration < 5400)")
        elif duration == "Medium (90-150 min)":
            filters.append("FILTER(?duration >= 5400 && ?duration <= 9000)")
        elif duration == "Long (> 150 min)":
            filters.append("FILTER(?duration > 9000)")

    # Filtro per i tag (senza EXISTS)
    if selected_tags:
        tags_filter = " || ".join(f"?movie dcterms:subject <http://dbpedia.org/resource/Category:{tag.replace(' ', '_')}>" for tag in selected_tags)
        filters.append(f"({tags_filter})")

    query = f"""
          SELECT ?title ?directorResource ?actorResource ?countryResource ?runtime ?abstract
          WHERE {{
            ?movie rdfs:label ?title .
            ?movie dbo:director ?directorResource .
            ?movie dbo:starring ?actorResource .
            ?movie dbo:country ?countryResource .
            ?movie dbo:runtime ?runtime .
            ?movie dbo:abstract ?abstract .
            FILTER(LANG(?abstract) = "en")
            FILTER(LANG(?title) = "en")
          }}
          LIMIT 20
    """

    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)

    try:
        results = sparql.query().convert()
    except Exception as e:
        st.error(f"Error querying DBpedia: {e}")
        return []

    movies = []
    for result in results["results"]["bindings"]:
        movie = {
            "title": result["title"]["value"],
            "abstract": result.get("abstract", {}).get("value", "No description available."),
            "director": result.get("director", {}).get("value", "Unknown"),
            "actors": result.get("actors", {}).get("value", "Unknown"),
            "year": result.get("releaseDate", {}).get("value", "Unknown")[:4],
            "nationality": result.get("country", {}).get("value", "Unknown"),
            "duration": str(int(result.get("duration", {}).get("value", "0")) // 60)  # Converti in minuti
        }
        movies.append(movie)

    return movies

# Funzione per mostrare i risultati in Streamlit
def results():

    """
       Funzione per visualizzare i risultati della ricerca dei film, sulla base dei criteri selezionati dall'utente.

       Questo metodo recupera i criteri di selezione dalla sessione di Streamlit, esegue una query per ottenere i film
       che soddisfano tali criteri, e visualizza i risultati con un'opzione per scegliere un film. Se non ci sono film
       che soddisfano i criteri, viene mostrato un messaggio di avviso.
       """

    # Titolo della pagina con il nome "results"
    st.markdown(
        '<h2 style="text-align: center; color: @white;"> 🎬 Films Recommended </h2>',
        unsafe_allow_html=True
    )

    # Recupero dei dati dalla sessione di Streamlit
    selected_genres = st.session_state.get('selected_genres', [])
    selected_director = st.session_state.get('selected_director', [])
    selected_actors = st.session_state.get('selected_actors', [])
    selected_nationality = st.session_state.get('selected_nationality', '')
    selected_decade = st.session_state.get('selected_decade', '')
    duration = st.session_state.get('duration', '')
    selected_tags = st.session_state.get('selected_tags', [])

    # Crea una stringa che riassume i criteri selezionati dall'utente
    criteria = "These are the results because you selected the following criteria:"

    # Aggiunge i generi selezionati
    if selected_genres:
        criteria += f"\n- **Genres**: {', '.join(selected_genres)}"
    else:
        criteria += "\n- **Genres**: Not selected"

    # Aggiunge i registi selezionati
    if selected_director:
        criteria += f"\n- **Director(s)**: {', '.join(selected_director)}"
    else:
        criteria += "\n- **Director(s)**: Not selected"

    # Aggiunge gli attori selezionati
    if selected_actors:
        criteria += f"\n- **Actor(s)**: {', '.join(selected_actors)}"
    else:
        criteria += "\n- **Actor(s)**: Not selected"

    # Aggiunge la nazionalità selezionata
    if selected_nationality:
        criteria += f"\n- **Nationality**: {selected_nationality}"
    else:
        criteria += "\n- **Nationality**: Not selected"

    # Aggiungie la decade selezionata
    if selected_decade:
        criteria += f"\n- **Decade**: {selected_decade}"
    else:
        criteria += "\n- **Decade**: Not selected"

    # Aggiungie la durata selezionata
    if duration:
        criteria += f"\n- **Duration**: {duration}"
    else:
        criteria += "\n- **Duration**: Not selected"

    # Aggiungie i tag selezionati (formattazione dei tag)
    if selected_tags:
        criteria += f"\n- **Tags**: {selected_tags}"
    else:
        criteria += "\n- **Tags**: Not selected"

    # Visualizza il riassunto dei criteri selezionati
    st.write(criteria)

    # Esegue la query per ottenere i risultati dei film
    query_results = query_movies(selected_genres, selected_director, selected_actors, selected_nationality,
                                 selected_decade, duration, selected_tags)

    # Rimuovi i duplicati nel risultato in base al titolo del film
    unique_movies = []
    seen_titles = set()

    for movie in query_results:
        if movie['title'] not in seen_titles:
            unique_movies.append(movie)
            seen_titles.add(movie['title'])

    # Mostra i risultati
    if unique_movies:
        for idx, movie in enumerate(unique_movies):
            st.subheader(movie['title'])

            # Make the description read-only
            st.text_area("Description", movie['abstract'], height=150, key=f"{movie['title']}_{idx}", disabled=True)

            # Mostra la descrizione
            if st.button(f"Choose", key=f"choose_{idx}"):
                # Aggiungi un pulsante per scegliere il film
                st.success("You have chosen **{movie['title']}**! BUONA VISIONE")
                st.session_state.page = "main"  # Imposta la pagina a "main" quando viene scelto un film
                st.rerun()  # Ricarica la pagina per mostrare il cambiamento
    else:
        st.write("No movies found matching your criteria.")

# Pulsante per andare alla schermata con altri suggerimenti (con vincoli rilassati)
    if st.button("other suggestions"):
        st.session_state.page = "other suggestions"   # Imposta la pagina a "other suggestions"
