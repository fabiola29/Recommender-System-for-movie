import json
import recommendation
import systemEvaluation
import pandas as pd

# """
# Modulo per la valutazione e il confronto di diverse strategie di raccomandazione.
#
# Esegue raccomandazioni per utenti simulati e raccoglie metriche di valutazione
# per confrontare tre approcci diversi:
# - Knowledge-Based Recommender System (KBRS)
# - Raccomandazioni casuali (Random)
# - Raccomandazioni basate sulla popolarità (Most Popular)
#
# Funzioni principali:
# - `load_simulated_users(filename)`: Carica gli utenti simulati da un file JSON.
# - `run_recommendations_for_users(users, results_per_user=5)`:
#   - Esegue le raccomandazioni per ogni utente simulato.
#   - Confronta le strategie KBRS, Random e Most Popular misurando le seguenti metriche:
#     - **Accuracy**: Percentuale di film raccomandati che soddisfano tutti i vincoli dell'utente.
#     - **Partial Accuracy**: Percentuale di film che soddisfano almeno alcuni vincoli.
#     - **Diversity**: Variazione tra i film raccomandati per evitare ripetizioni simili.
#     - **Serendipity**: Misura quanto le raccomandazioni siano sorprendenti per l'utente.
#   - Genera una tabella strutturata con i risultati per ogni utente e ogni strategia.
#
# Esecuzione:
# - Il modulo viene eseguito automaticamente se avviato come script principale.
# - Carica gli utenti simulati dal file `simulated_users.json`.
# - Calcola e stampa una tabella comparativa delle performance delle diverse strategie di raccomandazione.
#
# Output:
# - Un DataFrame Pandas con le metriche di valutazione, utile per l'analisi delle performance del sistema.
#
# Questo modulo consente di confrontare l'efficacia dei diversi metodi di raccomandazione e
# supporta il miglioramento continuo dell'algoritmo utilizzato.
# """


# Funzione per caricare gli utenti simulati da file JSON
def load_simulated_users(filename):
    with open(filename, "r") as file:
        return json.load(file)

def run_recommendations_for_users(users, results_per_user=5):
    """
    Esegue le raccomandazioni per ogni utente simulato e raccoglie le metriche
    in una tabella strutturata per confrontare Knowledge-Based, Random e Most Popular.
    """

    # Lista per raccogliere i risultati
    results_list = []

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

        # Raccomandazioni basate sui vincoli dell'utente
        recommended = recommendation.retrieve_results(results_per_user, genres, director, actors, country, popularity, duration, year, None, use_cache=False)
        acc_rec = systemEvaluation.compute_accuracy(recommended, prefs)
        part_acc_rec = systemEvaluation.compute_partial_accuracy(recommended, prefs)
        div_rec = systemEvaluation.compute_diversity(recommended)
        ser_rec = systemEvaluation.compute_serendipity(recommended, prefs)

        # Raccomandazioni casuali
        random_recommendations = recommendation.random_recommendation(results_per_user)
        acc_rand = systemEvaluation.compute_accuracy(random_recommendations, prefs)
        part_acc_rand = systemEvaluation.compute_partial_accuracy(random_recommendations, prefs)
        div_rand = systemEvaluation.compute_diversity(random_recommendations)
        ser_rand = systemEvaluation.compute_serendipity(random_recommendations, prefs)

        # Raccomandazioni basate sulla popolarità
        most_popular_recommendations = recommendation.most_popular_recommendation(results_per_user)
        acc_pop = systemEvaluation.compute_accuracy(most_popular_recommendations, prefs)
        part_acc_pop = systemEvaluation.compute_partial_accuracy(most_popular_recommendations, prefs)
        div_pop = systemEvaluation.compute_diversity(most_popular_recommendations)
        ser_pop = systemEvaluation.compute_serendipity(most_popular_recommendations, prefs)

        # Aggiungiamo i risultati alla lista per la tabella
        results_list.append([user_id, "Knowledge-Based", acc_rec, part_acc_rec, div_rec, ser_rec])
        results_list.append([user_id, "Random", acc_rand, part_acc_rand, div_rand, ser_rand])
        results_list.append([user_id, "Most Popular", acc_pop, part_acc_pop, div_pop, ser_pop])

        user_count += 1

    # Creiamo il DataFrame
    results = pd.DataFrame(results_list, columns=["User ID", "Recommendation Type", "Accuracy", "Partial Accuracy", "Diversity", "Serendipity"])
    pd.set_option('display.max_columns', None)  # Mostra tutte le colonne

    # Mostriamo la tabella
    print(results)
    return results

# Esecuzione principale
if __name__ == "__main__":
    users = load_simulated_users("../../dataset/simulated_users.json")
    df_results = run_recommendations_for_users(users, results_per_user=5)

