import rdflib
import random
import time
from itertools import combinations
import streamlit as st
import utils

#TODO RENDI I RISULTATI UNICI
def execute_query(graph, query, description):
    """Esegue una query SPARQL e restituisce i risultati come una lista."""
    results = list(graph.query(query))

    if len(results) == 0:
        print("⚠️ Nessun risultato trovato nella query SPARQL!")

    return results


def collect_results_with_scores(results, genres, user_director, user_actors, user_country, views_list, duration_list, user_year):
    """
    Colleziona i risultati e assegna loro un punteggio in base ai vincoli soddisfatti.
    """
    print("Assegnando punteggi ai risultati...")

    # Controlli preventivi per garantire che le liste siano sempre iterabili
    genres = genres or []
    user_actors = user_actors or []
    views_list = views_list or []
    duration_list = duration_list or []

    results_with_scores = {}

    for row in results:
        score = 0
        reasons = []

        title = str(getattr(row, "title", "Unknown Title"))
        genre = str(getattr(row, "genre", "N/A"))
        director = str(getattr(row, "director", "N/A"))
        actors = str(getattr(row, "actor", "N/A"))
        country = str(getattr(row, "country", "N/A"))
        views = str(getattr(row, "views", "0"))  # Assicuriamoci che sia un numero valido
        runtime = str(getattr(row, "runtime", "0"))  # Assicuriamoci che sia un numero valido
        release_year = str(getattr(row, "released", "N/A"))
        abstract = str(getattr(row, "abstract", "N/A"))

        # ✅ Normalizziamo gli attori (rimuoviamo URI e trasformiamo in lista)
        actors = [a.split("/")[-1].replace("_", " ").strip() for a in actors.split(",") if a] if actors != "N/A" else []

        # ✅ Debug sugli attori
        print(f"DEBUG - Film: {title}, Attori film normalizzati: {actors}, Attori utente: {user_actors}")

        # ✅ Verifica e assegna punteggi ai vincoli rispettati
        if genres and genre != "N/A":
            matching_genres = [g for g in genres if g.lower() in genre.lower()]
            if matching_genres:
                score += len(matching_genres)
                reasons.append("you like genres like " + ", ".join(matching_genres))

        if user_director and director != "N/A" and user_director.lower() in director.lower():
            score += 1
            reasons.append(f"you appreciate films by {user_director}")

        # ✅ Confronto migliorato sugli attori
        if user_actors and actors:  # ✅ Controlliamo solo se entrambe le liste non sono vuote

            user_actors = [a.replace("_", " ").lower() for a in user_actors]

            matching_actors = [actor for actor in user_actors if any(actor.lower() in a.lower() for a in actors)]

            if matching_actors:
                score += len(matching_actors)
                reasons.append("you like actors like " + ", ".join(actors))

        if user_country and country != "N/A" and user_country.lower() in country.lower():
            score += 1
            reasons.append(f"you enjoy movies from {user_country}")

        # ✅ Confronto su popolarità (views)
        views = int(views) if views.isdigit() else 0
        views_result = None  # Inizializza con None

        if views_list:
            matching_views = []

            if views > 100:
                views_result = "Blockbuster"
                matching_views.append("Blockbuster")
            elif 30 <= views <= 100:
                views_result = "Popular"
                matching_views.append("Popular")
            elif views < 30:
                views_result = "Niche"
                matching_views.append("Niche")

            if matching_views:
                score += len(matching_views)
                reasons.append("it's a " + ", ".join(matching_views) + " film")

        # ✅ Confronto sulla durata
        runtime = int(runtime) if runtime.isdigit() else 0
        duration_result = None  # Inizializza con None

        if duration_list:
            matching_durations = []

            if runtime < 5400:
                duration_result = "Short"
                matching_durations.append("Short")
            elif 5400 <= runtime <= 9000:
                duration_result = "Medium"
                matching_durations.append("Medium")
            elif runtime > 9000:
                duration_result = "Long"
                matching_durations.append("Long")

            if matching_durations:
                score += len(matching_durations)
                reasons.append("it's a " + ", ".join(matching_durations) + "-length film")

        # ✅ Calcolo della decade
        decade = None
        if release_year.isdigit():
            release_year_int = int(release_year)
            decade = f"{(release_year_int // 10) * 10}s"
            if user_year == decade:
                score += 1
                reasons.append(f"it's from the {decade}")

        explanation = " and ".join(reasons) if reasons else "No specific reason found"

        # ✅ Salviamo i dati normalizzati nel dizionario
        results_with_scores[title] = {
            "title": title,
            "score": score,
            "explanation": explanation,
            "abstract": abstract,
            "genres": genre,
            "director": director,
            "actors": ", ".join(actors),  # Ora è una stringa leggibile
            "country": country,
            "views": views_result,
            "duration": duration_result,
            "year": decade
        }

    return results_with_scores

def epsilon_greedy_recommendation(results_with_scores, top_k, epsilon=0.2):
    """
    Seleziona top_k film usando epsilon-greedy. Con probabilità epsilon, sceglie a caso;
    altrimenti, preferisce quelli con punteggi più alti ma introduce un elemento casuale.
    """
    print(f"Applicando epsilon-greedy con epsilon={epsilon}...")

    if not results_with_scores:
        print("Nessun risultato disponibile per epsilon-greedy.")
        return {}

    # 🔹 Estrai la lista di film corretta
    films_list = [list(film.values())[0] for film in results_with_scores]  # ✅ Estrai il dizionario corretto

    # Creare una lista di tuple con il punteggio randomizzato
    randomized_scores = [
        (
            film.get("title", "Unknown"),  # ✅ Garantiamo che ogni film abbia un titolo
            film,
            film.get("score", 0) + random.uniform(-0.5, 0.5)  # Se "score" non esiste, usa 0
        )
        for film in films_list  # ✅ Iteriamo sulla lista corretta
    ]

    # Ordina per il punteggio randomizzato in ordine decrescente
    randomized_scores.sort(key=lambda x: x[2], reverse=True)

    print("Risultati disponibili per epsilon-greedy (con randomizzazione):")
    for title, film, score in randomized_scores:
        print(f"- Titolo: {title}, Punteggio randomizzato: {score}, Motivo: {film.get('explanation', 'N/A')}")

    selected = {}  # Ora è un DIZIONARIO con la stessa struttura di results_with_scores
    selected_titles = set()  # Per evitare duplicati
    available = randomized_scores[:]  # Copia della lista dei film disponibili

    random.seed(time.time())

    while len(selected) < top_k and available:
        # Genera un numero casuale per decidere tra esplorazione ed esploitazione
        random_value = random.random()
        print(f"Valore casuale generato: {random_value}")

        if random_value < epsilon and len(available) > 1:
            chosen = random.choice(available)  # Esplorazione: scegli un film a caso
        else:
            chosen = available[0]  # Sfruttamento: scegli il film con punteggio massimo

        title, film, score = chosen

        if title not in selected_titles:
            # Aggiunge il film scelto al dizionario mantenendo tutti i dati
            film_copy = film.copy()
            film_copy["score"] = score  # Aggiorna il punteggio con quello randomizzato
            selected[title] = film_copy  # Mantiene la struttura originale

            selected_titles.add(title)

            print(f"Film scelto: {title} con punteggio {score}, Motivo: {film.get('explanation', 'N/A')}")

        # Rimuove il film scelto dalla lista disponibile
        available = [movie for movie in available if movie[0] != title]

    return selected




def retrieve_results(number_of_results, genres, director, actors, country, popularity_list, duration_list, year, _progress_bar):
    if "recommended_movies" in st.session_state:
        return st.session_state.recommended_movies  # ✅ Se i risultati esistono, restituiscili subito

    g = rdflib.Graph()
    g.parse("movies_ontology.ttl", format="turtle")

    if director:
        director = director.replace(" ", "_")

    if actors:
        actors = [actor.replace(" ", "_").lower() for actor in actors]
    else:
        actors = []

    genre_filters = " || ".join(f'CONTAINS(LCASE(?genre), "{genre.lower()}")' for genre in genres)

    actor_filters = " || ".join(f'CONTAINS(LCASE(?actor), "{actor}")' for actor in actors)

    # Filtri per popularity (lista)
    if popularity_list:
        popularity_conditions = []
        for p in popularity_list:
            if p == "Blockbuster":
                popularity_conditions.append("?views > 100")
            elif p == "Popular":
                popularity_conditions.append("?views >= 30 && ?views <= 100")
            elif p == "Niche":
                popularity_conditions.append("?views < 30")
        # Aggiungi il filtro solo se ci sono condizioni valide
        if popularity_conditions:
            popularity_filter = " || ".join(popularity_conditions)
        else:
            popularity_filter = ""
    else:
        popularity_filter = ""

    # Filtri per duration (lista)
    if duration_list:
        duration_filter = " || ".join(
            "?runtime < 5400" if d == "Short" else
            "?runtime >= 5400 && ?runtime <= 9000" if d == "Medium" else
            "?runtime > 9000" for d in duration_list
        )
        duration_filter = f"({duration_filter})"
    else:
        duration_filter = ""


    if year and year.endswith("s"):
        decade_start = int(year[:-1])
        decade_end = decade_start + 9
        year_filter = f"?released >= {decade_start} && ?released <= {decade_end}"
    else:
        year_filter = ""


    constraints = [
        genre_filters,
        f"CONTAINS(LCASE(?director), '{director.lower()}')" if director else "",
        actor_filters,
        f"CONTAINS(LCASE(?country), '{country.lower()}')" if country else "",
        popularity_filter,
        duration_filter,
        year_filter
    ]


    constraints = [constraint for constraint in constraints if constraint]


    subnum = 0
    list_results_with_scores = []
    current_results_count = 0
    max_constraints_found = None  # Tiene traccia del numero di vincoli della prima query che ha restituito risultati
    unique_titles = set()
    query_completed = False

    #SPINNER

    total_queries = sum(range(len(constraints) + 1))  # Numero totale di combinazioni da provare
    completed_queries = 0  # Contatore per l'avanzamento della barra

    for num_constraints in range(len(constraints), 0, -1):

        for subset in combinations(constraints, num_constraints):

            print(f"Testing subset: {subset}")
            completed_queries += 1  # Incrementa il numero di query eseguite
            progress_percentage = min(int((completed_queries / total_queries) * 100), 100)  # Calcola la percentuale
            _progress_bar.progress(progress_percentage)  # **Aggiorna la barra di caricamento**

            subnum = subnum + 1

            # Genera la stringa dei filtri SPARQL
            filters = " ".join([f"FILTER({constraint})" for constraint in subset if constraint])

            query_template = """
                PREFIX dbo: <http://dbpedia.org/ontology/>
                PREFIX dbp: <http://dbpedia.org/property/>
                SELECT ?title ?genre ?director ?actor ?country ?views ?runtime ?released ?abstract
                WHERE {{
                    ?movie rdfs:label ?title .
                    OPTIONAL {{ ?movie dbo:genre ?genre. }}
                    OPTIONAL {{ ?movie dbo:director ?director. }}
                    OPTIONAL {{ ?movie dbo:starring ?actor. }}
                    OPTIONAL {{ ?movie dbo:country ?country. }}
                    OPTIONAL {{ ?movie dbp:views ?views. }}
                    OPTIONAL {{ ?movie dbo:runtime ?runtime. }}
                    OPTIONAL {{ ?movie dbp:released ?released. }}
                    OPTIONAL {{ ?movie dbo:abstract ?abstract. }}
                    {filters}
                }}
                ORDER BY RAND()
                LIMIT 10
            """
            query = query_template.format(filters=filters)


            # Esegui la query
            results = execute_query(g, query, f"Combination of {num_constraints} constraints")

            if "excluded_film" in st.session_state and st.session_state.excluded_film:
                excluded_title = st.session_state.excluded_film
                excluded_title = excluded_title.split("(")[0].strip().lower()
            else:
                excluded_title = None  # Se non c'è, lasciamo il valore None

            if results:
                for row in results:
                    row_title = row.title.strip().lower()
                    print("-------")
                    print("PARAGONIAMO")
                    print(excluded_title)
                    print(row_title.title)
                    print("--------")
                    # ✅ Escludiamo il film di riferimento SOLO se `excluded_title` esiste
                    if excluded_title and row_title == excluded_title:
                        print(f"❌ Film escluso: {row.title}")  # Debug per verificare
                        continue  # Saltiamo questo film

                    # ✅ Aggiungiamo solo titoli unici
                    if row.title not in unique_titles:
                        unique_titles.add(row.title)

                        # Se è la prima query con risultati, memorizza il numero di vincoli
                        if max_constraints_found is None:
                            max_constraints_found = num_constraints

                        # Estrai le informazioni del film e aggiungile al risultato
                        subset_scores = collect_results_with_scores(
                            [row], genres, director, actors, country, popularity_list, duration_list, year
                        )
                        list_results_with_scores.append(subset_scores)
                        current_results_count += 1  # Aumenta il conteggio solo per i film nuovi

                        # Controlla se hai accumulato abbastanza risultati
                        if current_results_count >= number_of_results:
                            query_completed = True

            # Se il ciclo corrente ha raggiunto il numero desiderato e non ci sono più combinazioni, termina il ciclo interno
            if query_completed:
                break

        # Se il ciclo corrente ha raggiunto il numero desiderato e tutte le combinazioni sono state elaborate, termina il ciclo esterno
        if query_completed and num_constraints < max_constraints_found:
            break


    recommended = epsilon_greedy_recommendation(list_results_with_scores, number_of_results)

    # Dopo aver calcolato recommended con epsilon_greedy_recommendation

    if len(recommended) < number_of_results:
        print("Non abbastanza risultati, aggiungendo film random...")

        # Numero di film mancanti per raggiungere desired_results
        films_needed = number_of_results - len(recommended)
        random_results = random_recommendation(films_needed)


        # ✅ Iteriamo correttamente su `random_results.items()` per accedere ai dettagli
        for title, details in random_results.items():  # ✅ CORRETTO SE random_results È UN DIZIONARIO
            if not isinstance(details, dict):  # Se details non è un dizionario, ignora il film
                print(f"⚠️ Errore: Dettagli mancanti per '{title}', skipping... Contenuto: {details}")
                continue

            recommended[title] = {
                "score": 0,
                "explanation": "chosen randomly",
                "abstract": details.get("abstract", "N/A"),
                "genres": details.get("genres", "N/A"),
                "director": details.get("director", "N/A"),
                "actors": details.get("actors", "N/A"),
                "country": details.get("country", "N/A"),
                "year": details.get("year", "N/A")
            }

    _progress_bar.empty()  # **Rimuove la barra di avanzamento dopo la ricerca**

    return recommended


def random_recommendation(number_of_results):
    """
    Genera raccomandazioni casuali di film nel formato corretto.

    Parametri:
    - number_of_results (int): Numero di risultati da generare.
    - genres (list): Lista dei generi preferiti.
    - director (str): Regista preferito.
    - actors (list): Lista di attori preferiti.
    - country (str): Paese preferito.
    - popularity_list (list): Lista di parametri di popolarità.
    - duration_list (list): Lista delle durate preferite.
    - year (str): Decennio preferito.

    Ritorna:
    - dict: Raccomandazioni di film nel formato corretto.
    """
    g = rdflib.Graph()
    g.parse("movies_ontology.ttl", format="turtle")

    random_query = f"""
           PREFIX dbo: <http://dbpedia.org/ontology/>
           PREFIX dbp: <http://dbpedia.org/property/>
           SELECT ?title ?genre ?director ?actors ?country ?views ?runtime ?released ?abstract
           WHERE {{
               ?movie rdfs:label ?title .
               OPTIONAL {{ ?movie dbo:genre ?genre. }}
               OPTIONAL {{ ?movie dbo:director ?director. }}
               OPTIONAL {{ ?movie dbo:starring ?actors. }}
               OPTIONAL {{ ?movie dbo:country ?country. }}
               OPTIONAL {{ ?movie dbp:views ?views. }}
               OPTIONAL {{ ?movie dbo:runtime ?runtime. }}
               OPTIONAL {{ ?movie dbp:released ?released. }}
               OPTIONAL {{ ?movie dbo:abstract ?abstract. }}
           }}
           ORDER BY RAND()
           LIMIT {number_of_results}
           """

    list_results_with_scores = {}
    random_results = execute_query(g, random_query, "Film casuali per completare")


    for row in random_results:
        film_title = str(row[0])
        film_details = {
            'title': film_title,
            'score': 0,  # Score predefinito per film casuali
            'explanation': 'Randomly selected movie',
            'abstract': str(row[8]) if row[8] else None,
            'genres': str(row[1]) if row[1] else None,
            'director': str(row[2]) if row[2] else None,
            'actors': str(row[3]) if row[3] else None,
            'country': str(row[4]) if row[4] else None,
            'views': str(row[5]) if row[5] else None,
            'duration': str(row[6]) if row[6] else None,
            'year': str(row[7]) if row[7] else None,
        }
        list_results_with_scores[film_title] = film_details

    return list_results_with_scores
