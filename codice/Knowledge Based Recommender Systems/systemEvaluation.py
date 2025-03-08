
from itertools import combinations

def compute_accuracy(recommendations, user_constraints):
    """
    Calcola l'Accuracy delle raccomandazioni rispetto ai vincoli dell'utente.

    Accuracy misura la precisione delle raccomandazioni rispetto alle richieste originali,
    calcolando la proporzione di film che soddisfano **tutti** i vincoli forniti.

    Parametri:
    - recommendations (dict): Dizionario in cui le chiavi sono i titoli dei film e i valori sono dizionari con i dettagli.
    - user_constraints (dict): Dizionario contenente i vincoli dell'utente.

    Ritorna:
    - float: Accuracy, valore tra 0 e 1.
    """
    total_recommendations = len(recommendations)
    correct_recommendations = 0

    if isinstance(recommendations, list):
        recommendations = {str(i): rec for i, rec in enumerate(recommendations)}

    for title, details in recommendations.items():
        matches = 0
        total_constraints = len(user_constraints)  # Conta solo i vincoli effettivamente impostati

        # Controllo generi
        if 'genres' in user_constraints:
            genres = details.get('genres', [])
            if isinstance(genres, str):
                genres = genres.split(', ')
            if any(genre in user_constraints['genres'] for genre in genres):
                matches += 1

        # Controllo regista
        if 'directors' in user_constraints:
            if details.get('director', '').split('/')[-1] == user_constraints.get('directors', '').split('/')[-1]:
                matches += 1

        # Controllo attori
        if 'actors' in user_constraints:
            actors = details.get('actors', [])
            if isinstance(actors, str):
                actors = actors.split(', ')
            if any(actor in user_constraints['actors'] for actor in actors):
                matches += 1

        # Controllo anno di uscita
        if 'year' in user_constraints:
            if details.get('year', '') == user_constraints['year']:
                matches += 1

        # Controllo paese di produzione
        if 'country' in user_constraints:
            if details.get('country', '') == user_constraints['country']:
                matches += 1

        # Se il film soddisfa tutti i vincoli forniti, conta come corretto
        if matches == total_constraints:
            correct_recommendations += 1

    accuracy = correct_recommendations / total_recommendations if total_recommendations else 0
    return accuracy


def compute_partial_accuracy(recommendations, user_constraints):
    """
    Calcola la Partial Accuracy delle raccomandazioni rispetto ai vincoli dell'utente.

    La Partial Accuracy misura il numero medio di vincoli soddisfatti per film,
    rispetto al numero totale di vincoli definiti dall'utente.

    Parametri:
    - recommendations (dict): Dizionario in cui le chiavi sono i titoli dei film e i valori sono dizionari con i dettagli.
    - user_constraints (dict): Dizionario contenente i vincoli dell'utente.

    Ritorna:
    - float: Partial Accuracy, valore tra 0 e 1.
    """
    total_recommendations = len(recommendations)
    total_constraints = sum(1 for key in user_constraints if user_constraints[key])  # Conta solo i vincoli effettivi
    total_satisfied_constraints = 0

    if total_constraints == 0:
        return 0  # Se non ci sono vincoli impostati, la Partial Accuracy non è definita.

    for title, details in recommendations.items():
        satisfied_constraints = 0

        # Controllo generi
        genres = details.get('genres', [])
        if isinstance(genres, str):
            genres = genres.split(', ')
        if 'genres' in user_constraints and isinstance(user_constraints.get('genres'), list):
            if any(genre in user_constraints['genres'] for genre in genres):
                satisfied_constraints += 1

        # Controllo regista
        director = details.get('director', "")
        if 'directors' in user_constraints and isinstance(user_constraints.get('directors'), str):
            if director.split('/')[-1] == user_constraints['directors'].split('/')[-1]:
                satisfied_constraints += 1

        # Controllo attori (ora evita il problema del NoneType)
        actors = details.get('actors', [])
        if isinstance(actors, str):
            actors = actors.split(', ')
        user_actors = user_constraints.get('actors', []) or []  # Garantisce che sia sempre una lista
        if 'actors' in user_constraints and isinstance(user_actors, list):
            if any(actor in user_actors for actor in actors):
                satisfied_constraints += 1

        # Controllo anno di uscita
        if 'year' in user_constraints and isinstance(user_constraints.get('year'), str):
            if details.get('year', "") == user_constraints['year']:
                satisfied_constraints += 1

        # Controllo paese di produzione
        if 'country' in user_constraints and isinstance(user_constraints.get('country'), str):
            if details.get('country', "") == user_constraints['country']:
                satisfied_constraints += 1

        total_satisfied_constraints += satisfied_constraints

    partial_accuracy = total_satisfied_constraints / (total_recommendations * total_constraints) if total_recommendations else 0
    return partial_accuracy


def compute_diversity(recommendations):
    """
    Calcola la diversità delle raccomandazioni considerando generi, registi, attori e paesi.

    La diversità è definita come 1 - media della similarità tra i film raccomandati.
    Un valore più alto indica una maggiore diversità.

    Parametri:
    - recommendations (dict): Dizionario delle raccomandazioni con i dettagli dei film.

    Ritorna:
    - float: Valore della diversità (0 a 1).
    """
    feature_sets = {}

    for title, details in recommendations.items():
        genres = set((details.get('genres') or "").split(', '))
        director = {details.get('director') or ""}
        actors = set((details.get('actors') or "").split(', '))
        country = {details.get('country') or ""}

        # Ogni film è rappresentato da un insieme di caratteristiche (generi, regista, attori, paese)
        feature_sets[title] = genres | director | actors | country

    if len(feature_sets) < 2:
        return 1.0  # Se c'è un solo film, consideriamo massima diversità

    similarity_scores = []

    for (movie1, features1), (movie2, features2) in combinations(feature_sets.items(), 2):
        intersection = len(features1 & features2)
        union = len(features1 | features2)
        similarity = intersection / union if union > 0 else 0
        similarity_scores.append(similarity)

    avg_similarity = sum(similarity_scores) / len(similarity_scores) if similarity_scores else 0
    diversity = 1 - avg_similarity

    return diversity


def compute_serendipity(recommendations, user_constraints):
    """
    Calcola la serendipità delle raccomandazioni rispetto ai vincoli dell'utente.

    La serendipità misura quanto le raccomandazioni siano inaspettate ma potenzialmente utili.
    Un valore più alto indica che il sistema suggerisce film che **deviano dai vincoli**,
    offrendo nuove scoperte all'utente senza essere completamente irrilevanti.

    Parametri:
    - recommendations (dict): Dizionario delle raccomandazioni con i dettagli dei film.
    - user_constraints (dict): Dizionario contenente i vincoli dell'utente.

    Ritorna:
    - float: Valore della serendipità (0 a 1).
    """
    total_recommendations = len(recommendations)
    serendipitous_scores = []

    for title, details in recommendations.items():
        matches = 0
        total_constraints = sum(1 for key in user_constraints if user_constraints[key])  # Conta i vincoli effettivi

        # Controllo generi
        genres = set(details.get('genres', "").split(', '))
        genre_match = genres.intersection(set(user_constraints.get('genres', [])))
        if genre_match:
            matches += 1

        # Controllo regista
        director = details.get('director', "")
        if director == user_constraints.get('directors', ""):
            matches += 1

        # Controllo attori
        actors = set((details.get('actors') or "").split(', '))
        actor_match = actors.intersection(set(user_constraints.get('actors', [])))
        if actor_match:
            matches += 1

        # Controllo anno di uscita
        if details.get('year', "") == user_constraints.get('year', ""):
            matches += 1

        # Controllo paese di produzione
        if details.get('country', "") == user_constraints.get('country', ""):
            matches += 1

        # Percentuale di vincoli soddisfatti
        if total_constraints > 0:
            match_ratio = matches / total_constraints  # Quanto il film rispetta i vincoli
        else:
            match_ratio = 0  # Se non ci sono vincoli definiti dall'utente

        # La serendipità è alta se il film è leggermente fuori dai vincoli ma non completamente diverso
        serendipity_score = 1 - match_ratio if 0 < match_ratio < 0.7 else 0  # Consideriamo serendipitosi i film con 30%-70% di match
        serendipitous_scores.append(serendipity_score)

    serendipity = sum(serendipitous_scores) / total_recommendations if total_recommendations else 0
    return serendipity



# def evaluate_recommendations(recommended, user_preferences):
#     accuracy = compute_accuracy(recommended, user_preferences)
#     partial_accuracy = compute_partial_accuracy(recommended, user_preferences)
#     diversity = compute_diversity(recommended)
#     serendipity = compute_serendipity(recommended, user_preferences)
#     # Mostra i punteggi medi per il sistema di raccomandazione
#     print("\n📊 Average Scores for the Recommendation System:")
#     print(f"🔹 Accuracy: {accuracy * 100:.2f}%")
#     print(f"🔹 Partial Accuracy: {partial_accuracy * 100:.2f}%")
#     print(f"🔹 Diversity: {diversity * 100:.2f}%")
#     print(f"🔹 Serendipity: {serendipity * 100:.2f}%")
