
import rdflib
import random
import time
from itertools import combinations
import streamlit as st

#TODO RENDI I RISULTATI UNICI
def execute_query(graph, query, description):
    """Esegue una query SPARQL e restituisce i risultati come una lista."""
    print(f"Eseguendo query: {description}")
    results = list(graph.query(query))
    print(f"Risultati trovati: {len(results)}")

    for row in results:
        print(
            f"- Titolo: {row.title}, Genere: {getattr(row, 'genre', 'N/A')}, Regista: {getattr(row, 'director', 'N/A')}, Attore: {getattr(row, 'actors', 'N/A')}, Country: {getattr(row, 'country', 'N/A')}, Popularity: {getattr(row, 'views', 'N/A')}, Runtime: {getattr(row, 'runtime', 'N/A')}, Year: {getattr(row, 'released', 'N/A')} ")

    print("CIAO SONO AI RISULTTI")


    print(results)
    return results


def collect_results_with_scores(results, genres, director, actors, country, views_list, duration_list, year):
    """
    Colleziona i risultati e assegna loro un punteggio in base ai vincoli soddisfatti.
    """
    print("Assegnando punteggi ai risultati...")
    results_with_scores = []
    for row in results:
        score = 0
        reasons = []
        if genres and hasattr(row, "genre") and row.genre:
            matching_genres = [genre for genre in genres if genre.lower() in row.genre.lower()]
            if matching_genres:
                score += len(matching_genres)
                reasons.append("you like genres like " + ", ".join(matching_genres))
        if director and hasattr(row, "director") and row.director and director.lower() in row.director.lower():
            score += 1
            reasons.append(f"you appreciate films by {director}")
        if actors and hasattr(row, "actors") and row.actors:
            matching_actors = [actor for actor in actors if actor.lower() in row.actor.lower()]
            if matching_actors:
                score += len(matching_actors)
                reasons.append("you like actors like " + ", ".join(matching_actors))
        if country and hasattr(row, "country") and row.country and country.lower() in row.country.lower():
            score += 1
            reasons.append(f"you enjoy movies from {country}")
        if views_list and hasattr(row, "views") and row.views:
            try:
                views_count = int(row.views)
                matching_views = [
                    v for v in views_list if
                    (v == "Blockbuster" and views_count > 100) or
                    (v == "Popular" and 30 <= views_count <= 100) or
                    (v == "Niche" and views_count < 30)
                ]
                if matching_views:
                    score += len(matching_views)
                    reasons.append("it's a " + ", ".join(matching_views) + " film")
            except ValueError:
                print(f"Valore di views non valido: {row.views}")

        if duration_list and hasattr(row, "runtime") and row.runtime:
            try:
                runtime = int(row.runtime)
                matching_durations = [
                    d for d in duration_list if
                    (d == "Short" and runtime < 5400) or
                    (d == "Medium" and 5400 <= runtime <= 9000) or
                    (d == "Long" and runtime > 9000)
                ]
                if matching_durations:
                    score += len(matching_durations)
                    reasons.append("it's a " + ", ".join(matching_durations) + "-lenght film")
            except ValueError:
                print(f"Valore di runtime non valido: {row.runtime}")

        if year and hasattr(row, "released") and row.released:
            try:
                release_year = int(row.released)
                if year == "1900s" and 1900 <= release_year <= 1909:
                    score += 1
                    reasons.append("it's from the 1900s")
                elif year == "1910s" and 1910 <= release_year <= 1919:
                    score += 1
                    reasons.append("it's from the 1910s")
                elif year == "1920s" and 1920 <= release_year <= 1929:
                    score += 1
                    reasons.append("it's from the 1920s")
                elif year == "1930s" and 1930 <= release_year <= 1939:
                    score += 1
                    reasons.append("it's from the 1930s")
                elif year == "1940s" and 1940 <= release_year <= 1949:
                    score += 1
                    reasons.append("it's from the 1940s")
                elif year == "1950s" and 1950 <= release_year <= 1959:
                    score += 1
                    reasons.append("it's from the 1950s")
                elif year == "1960s" and 1960 <= release_year <= 1969:
                    score += 1
                    reasons.append("it's from the 1960s")
                elif year == "1970s" and 1970 <= release_year <= 1979:
                    score += 1
                    reasons.append("it's from the 1970s")
                elif year == "1980s" and 1980 <= release_year <= 1989:
                    score += 1
                    reasons.append("it's from the 1980s")
                elif year == "1990s" and 1990 <= release_year <= 1999:
                    score += 1
                    reasons.append("it's from the 1990s")
                elif year == "2000s" and 2000 <= release_year <= 2009:
                    score += 1
                    reasons.append("it's from the 2000s")
                elif year == "2010s" and 2010 <= release_year <= 2019:
                    score += 1
                    reasons.append("it's from the 2010s")
                elif year == "2020s" and 2020 <= release_year <= 2029:
                    score += 1
                    reasons.append("it's from the 2020s")
                elif year == "2030s" and 2030 <= release_year <= 2039:
                    score += 1
                    reasons.append("it's from the 2030s")
            except ValueError:
                print(f"Valore di year non valido: {row.released}")

        explanation = " and ".join(reasons)
        for row in results:
            # Esempio: estrai l'abstract dal risultato corrente
            abstract = getattr(row, 'abstract', 'N/A')
            # Aggiungi il titolo, lo score e l'abstract ai risultati
            results_with_scores.append((row.title, score, explanation, abstract))

    return results_with_scores



def epsilon_greedy_recommendation(results_with_scores, top_k, epsilon=0.2):
    """
    Seleziona top_k film usando epsilon-greedy. Con probabilità epsilon, sceglie a caso;
    altrimenti, preferisce quelli con punteggi più alti ma introduce un elemento casuale.
    """
    print(f"Applicando epsilon-greedy con epsilon={epsilon}...")
    if not results_with_scores:
        print("Nessun risultato disponibile per epsilon-greedy.")
        return []

    # Aggiungi un elemento casuale ai punteggi per introdurre maggiore casualità.
    randomized_scores = [
        (title, score + random.uniform(-0.5, 0.5), explanation, abstract)
        for title, score, explanation, abstract in results_with_scores
    ]

    # Ordina per il nuovo punteggio "casuale"
    randomized_scores = sorted(randomized_scores, key=lambda x: x[1], reverse=True)

    # Stampa i risultati con i loro nuovi punteggi casuali e spiegazioni
    print("Risultati disponibili per epsilon-greedy (con randomizzazione):")
    for title, score, explanation, abstract in randomized_scores:
        print(f"- Titolo: {title}, Punteggio randomizzato: {score}, Motivo: {explanation}")

    selected = []
    selected_titles = set()  # Un set per tenere traccia dei titoli già scelti
    available = randomized_scores[:]

    random.seed(time.time())

    while len(selected) < top_k and available:
        # Genera un numero casuale float
        random_value = random.random()
        print(f"Valore casuale generato: {random_value}")

        if random_value < epsilon and len(available) > 1:
            # Esplorazione: scegli un film a caso tra quelli non ancora selezionati
            chosen = random.choice(available)
        else:
            # Sfruttamento (ma con punteggi già randomizzati): scegli il primo (migliore) film disponibile
            chosen = available[0]

        title, score, explanation, abstract = chosen
        if title not in selected_titles:
            # Aggiungi il film scelto ai selezionati, incluso l’abstract
            selected.append((title, score, explanation, abstract))
            selected_titles.add(title)
            print(f"Film scelto: {title} con punteggio {score}, Motivo: {explanation}")

        # Rimuovi il film scelto dai disponibili
        available = [movie for movie in available if movie[0] != title]

    return selected


@st.cache_data
def retrieve_results(number_of_results, genres, director, actors, country, popularity_list, duration_list, year):
    g = rdflib.Graph()
    g.parse("movies_ontology.ttl", format="turtle")

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

    print("FILTROO")
    print(popularity_list)

    if year and year.endswith("s"):
        decade_start = int(year[:-1])
        decade_end = decade_start + 9
        year_filter = f"?released >= {decade_start} && ?released <= {decade_end}"
    else:
        year_filter = ""

# TODO CHOOSE AN OPTION RISOLVI
    constraints = [
        genre_filters,
        f"CONTAINS(LCASE(?director), '{director.lower()}')" if director else "",
        actor_filters,
        f"CONTAINS(LCASE(?country), '{country.lower()}')" if country else "",
        popularity_filter,
        duration_filter,
        year_filter
    ]

    print("POPOLARITT")
    print(popularity_filter)

    constraints = [constraint for constraint in constraints if constraint]

    results_with_scores = []
    subnum = 0
    # Ciclo attraverso tutte le combinazioni dei vincoli
    # for num_constraints in range(len(constraints), 0, -1):  # Inizia con tutti i vincoli, riduci gradualmente
    #
    #     for subset in combinations(constraints, num_constraints):
    #         print(f"Testing subset: {subset}")
    #         subnum = subnum + 1
    #
    #         #Genera la stringa dei filtri SPARQL, ma includi solo quelli che non sono vuoti
    #         filters = " ".join([f"FILTER({constraint})" for constraint in subset if constraint])
    #
    #         # Inserisci questi filtri in una query template
    #         query_template = """
    #             PREFIX dbo: <http://dbpedia.org/ontology/>
    #             PREFIX dbp: <http://dbpedia.org/property/>
    #             SELECT ?title ?genre ?director ?actor ?country ?views ?runtime ?released ?abstract
    #             WHERE {{
    #                 ?movie rdfs:label ?title .
    #                 OPTIONAL {{ ?movie dbo:genre ?genre. }}
    #                 OPTIONAL {{ ?movie dbo:director ?director. }}
    #                 OPTIONAL {{ ?movie dbo:starring ?actor. }}
    #                 OPTIONAL {{ ?movie dbo:country ?country. }}
    #                 OPTIONAL {{ ?movie dbp:views ?views. }}
    #                 OPTIONAL {{ ?movie dbo:runtime ?runtime. }}
    #                 OPTIONAL {{ ?movie dbp:released ?released. }}
    #                 OPTIONAL {{ ?movie dbo:abstract ?abstract. }}
    #                 {filters}
    #             }}
    #             ORDER BY RAND()
    #             LIMIT 100
    #         """
    #         query = query_template.format(filters=filters)
    #         print("\n\n\n\nQUESTA LA QUERY")
    #         print(query)
    #
    #         # Esegui la query
    #         print(f"Testing combination of {num_constraints} constraints: {subset}")
    #         results = execute_query(g, query, f"Combination of {num_constraints} constraints")
    #
    #         # Se ci sono risultati, accumulali
    #         if results:
    #             subset_scores = collect_results_with_scores(
    #                 results, genres, director, actors, country, popularity_list, duration_list, year
    #             )
    #             results_with_scores.extend(subset_scores)



    results_with_scores = []
    current_results_count = 0
    max_constraints_found = None  # Tiene traccia del numero di vincoli della prima query che ha restituito risultati

    for num_constraints in range(len(constraints), 0, -1):
        for subset in combinations(constraints, num_constraints):
            print(f"Testing subset: {subset}")
            subnum = subnum + 1

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
            print("\n\n\n\nQUESTA LA QUERY")
            print(query)

            results = execute_query(g, query, f"Combination of {num_constraints} constraints")

            # if results:
            #     # Se è la prima query con risultati, memorizza il numero di vincoli
            #     if max_constraints_found is None:
            #         max_constraints_found = num_constraints
            #
            #     # Se il numero di vincoli della query è minore rispetto a quello memorizzato, conta i risultati
            #     if num_constraints < max_constraints_found:
            #         subset_scores = collect_results_with_scores(
            #             results, genres, director, actors, country, popularity_list, duration_list, year
            #         )
            #         results_with_scores.extend(subset_scores)
            #         current_results_count += len(subset_scores)
            #
            #         # Se hai abbastanza risultati, esci
            #         if current_results_count >= number_of_results:
            #             break
            # else:
            #     continue
            # break
            # Esegui la query
            print(f"Testing combination of {num_constraints} constraints: {subset}")
            results = execute_query(g, query, f"Combination of {num_constraints} constraints")

            # Se ci sono risultati, accumulali
            if results:
                subset_scores = collect_results_with_scores(
                    results, genres, director, actors, country, popularity_list, duration_list, year
                )
                results_with_scores.extend(subset_scores)



    # Una volta raccolti tutti i risultati, applica epsilon-greedy
    recommended = epsilon_greedy_recommendation(results_with_scores, number_of_results)

    # Dopo aver calcolato recommended con epsilon_greedy_recommendation
    print(len(recommended))
    if len(recommended) < number_of_results:
        print("Non abbastanza risultati, aggiungendo film random...")

        # Numero di film mancanti per raggiungere desired_results
        films_needed = number_of_results - len(recommended)
        print("MI SERVONO")
        print(films_needed)
        # Query per film casuali senza filtri
        random_query = f"""
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
        }}
        ORDER BY RAND()
        LIMIT {films_needed}
        """

        print("RANDOM QUERYYYY")
        print(random_query)

        # Esegui la query per ottenere film casuali
        random_results = execute_query(g, random_query, "Film casuali per completare")
        print("\n\nCI ARRIVO QUI")
        # Aggiungi questi film ai risultati consigliati
        for row in random_results:
            # Aggiungi un motivo specifico per i film random
            recommended.append((row.title, 0, "chosen randomly", getattr(row, 'abstract', 'N/A')))

        # Ora 'recommended' contiene almeno 'desired_results' film

    return recommended




if __name__ == "__main__":
    genres = ["comedy"]
    director = "Paul Aster".replace(" ", "_")
    actors = ["Lou Reed"]
    actors = [actor.replace(" ", "_").lower() for actor in actors]
    country = "United States"
    duration = "Short"
    popularity = "Niche"
    year = "1990s"
    # actors = []
    # director = None
    # country = None
    retrieve_results(genres, director, actors, country, popularity, duration, year)
