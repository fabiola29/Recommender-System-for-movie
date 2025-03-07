import json
import recommendation
import systemEvaluation
import utils
# Funzione per caricare gli utenti simulati da file JSON
def load_simulated_users(filename):
    with open(filename, "r") as file:
        return json.load(file)

# Funzione che avvia raccomandazioni e valutazione per ogni utente simulato
def run_recommendations_for_users(users, results_per_user=5):
    user_count = 1
    total_users = len(users)

    for user_id, prefs in users.items():
        genres = prefs.get('genres', [])
        director = prefs.get('director', [])
        actors = prefs.get('actors', [])
        country = prefs.get('country', None)
        duration = prefs.get('duration', None)
        popularity = prefs.get('popularity', None)
        year = prefs.get('year', None)

        print(f"\nRunning recommendations for user {user_id} ({user_count}/{total_users})")
        recommended = recommendation.retrieve_results(5, genres, director, actors, country, popularity, duration, year)
        print("ITEM RACCOMANDATI")
        utils.print_recommendations(recommended)
        systemEvaluation.evaluate_recommendations(recommended, prefs)

        print("Genero ITEM RANDOM")
        random_recommendations = recommendation.random_recommendation(5)
        utils.print_recommendations(random_recommendations)
        systemEvaluation.evaluate_recommendations(random_recommendations, prefs)

        # TODO MOST POPULAR

        user_count += 1


# Esecuzione principale
if __name__ == "__main__":
    users = load_simulated_users("../../dataset/simulated_users.json")
    run_recommendations_for_users(users, results_per_user=5)
