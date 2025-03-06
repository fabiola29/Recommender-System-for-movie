import re
import random

def movie_matches_genre(movie_genre, user_genres):
    """
       Verifica se il genere del film corrisponde ai generi preferiti dall'utente.

       Parameters:
           movie_genre (str/tuple): Il genere del film, che può essere una stringa o una tupla di descrizioni.
           user_genres (list): Una lista dei generi preferiti dall'utente.

       Returns:
           bool: True se c'è un match, altrimenti False.
    """
    print(f"Raw Movie Genre: {movie_genre}, User Genres: {user_genres}")

    # Se movie_genre è una tupla, cerca una stringa con "genres like"
    if isinstance(movie_genre, tuple):
        for item in movie_genre:
            if isinstance(item, str) and "genres like" in item:
                match = re.search(r"genres like (\w+)", item)  # Cerca il genere
                if match:
                    movie_genre = match.group(1).strip().lower()
                    break

    print(f"Processed Movie Genre: {movie_genre}")

    # Confronto con i generi dell'utente
    if movie_genre in [g.lower() for g in user_genres]:
        print(f"✅ Match Found for Genre : {movie_genre}")

        return True

    print(f"❌ No Match for Genre")

    return False


def movie_matches_director(movie_director, user_directors):
    """
       Verifica se il regista del film corrisponde ai registi preferiti dall'utente.

       Parameters:
           movie_director (str/tuple): Il nome del regista del film, che può essere una stringa o una tupla di descrizioni.
           user_directors (list): Una lista dei registi preferiti dall'utente.

       Returns:
           bool: True se c'è un match, altrimenti False.
    """
    print(f"Raw Movie Director: {movie_director}, User Directors: {user_directors}")

    extracted_director = None

    # Se movie_director è una tupla, cerca una stringa con "films by"
    if isinstance(movie_director, tuple):
        for item in movie_director:
            if isinstance(item, str) and "films by" in item:
                match = re.search(r"films by (\w+)", item)  # Cerca il nome del regista
                if match:
                    extracted_director = match.group(1).strip()
                    break

    print(f"Extracted Director: {extracted_director}")

    # Standardizza i nomi rimuovendo eventuali underscore o confrontando senza differenze
    if extracted_director:
        extracted_director = extracted_director.replace("_", " ")  # Sostituisce gli underscore con spazi
        print(f"Standardized Extracted Director: {extracted_director}")

    # Confronto con i registi dell'utente
    if extracted_director and extracted_director in user_directors:
        print(f" ✅ Match Found for Director: {extracted_director}")

        return True

    print(f"❌ No Match for Director for {extracted_director}")

    return False

def movie_matches_actors(movie_actors, user_actors):
    """
       Verifica se uno degli attori del film corrisponde agli attori preferiti dall'utente.

       Parameters:
           movie_actors (list/tuple): Lista di attori del film, che può essere una lista o una tupla.
           user_actors (list): Lista degli attori preferiti dall'utente.

       Returns:
           int: Numero di attori corrispondenti tra quelli del film e quelli preferiti dall'utente.
    """
    print(f"Raw Movie Actors: {movie_actors}, User Actors: {user_actors}")

    extracted_actors = []

    # Se movie_actors è una tupla, cerchiamo gli attori nella descrizione
    if isinstance(movie_actors, tuple):
        for item in movie_actors:
            if isinstance(item, str):
                # Estrai i nomi degli attori dopo "features narration by" o "read by"
                matches = re.findall(r"(?:features narration by|read by) ([\w\s]+)", item)
                extracted_actors.extend(matches)

    print(f"Extracted Actors: {extracted_actors}")

    # Confronto tra attori estratti e quelli dell'utente
    matches = sum(1 for actor in extracted_actors if actor in user_actors)

    print(f"Matching Actors: {matches}")

    return matches


def movie_matches_country(movie_country, user_countries):
    """
       Verifica se il paese di origine del film corrisponde ai paesi preferiti dall'utente.

       Parameters:
           movie_country (str/tuple): Il paese di origine del film, che può essere una stringa o una tupla di descrizioni.
           user_countries (list): Una lista dei paesi preferiti dall'utente.

       Returns:
           int: 1 se c'è un match, altrimenti 0.
    """
    print(f"Raw Movie Country: {movie_country}, User Countries: {user_countries}")

    extracted_country = None

    # Se movie_country è una tupla, cerchiamo il paese nella descrizione
    if isinstance(movie_country, tuple):
        for item in movie_country:
            if isinstance(item, str) and "movies from" in item:
                match = re.search(r"movies from ([\w\s]+?)(?:\s+and|$)", item)  # Cerca il paese e fermati prima di 'and'
                if match:
                    extracted_country = match.group(1).strip()
                    break

    print(f"Extracted Country: {extracted_country}")

    # Confronto con i paesi dell'utente
    if extracted_country and extracted_country in user_countries:
        print(f"✅ Match Found for Country: {extracted_country}")

        return 1

    print(f"❌ No Match for Country for {extracted_country}")

    return 0


def movie_matches_duration(movie_duration, user_duration_range):
    """
       Verifica se la durata del film rientra nell'intervallo di tempo preferito dall'utente.

       Parameters:
           movie_duration (int/float/tuple): La durata del film, in ore o in una tupla di descrizioni.
           user_duration_range (list): Una lista che indica l'intervallo di durata preferito dall'utente.

       Returns:
           int: 1 se la durata del film corrisponde, altrimenti 0.
    """
    print(f"Raw Movie Duration: {movie_duration}, User Duration Range: {user_duration_range}")

    extracted_duration = None

    # Se movie_duration è una tupla, cerchiamo la durata nei suoi elementi
    if isinstance(movie_duration, tuple):
        for item in movie_duration:
            if isinstance(item, (int, float)):  # Se troviamo un numero, è la durata
                # Convertiamo ore → secondi
                extracted_duration = item * 60 * 60  # Convert hours to seconds
                break

    print(f"Extracted Duration (in seconds): {extracted_duration}")

    if extracted_duration is None:
        print("No valid duration extracted.")
        return 0

    # 🛠️ Gestione delle preferenze utente
    duration_mapping = {
        "short": (0, 5400),       # 0 to 5400 seconds (0 to 90 minutes)
        "medium": (5400, 9000),   # 5400 to 9000 seconds (90 to 150 minutes)
        "long": (9000, 18000)     # 9000 to 18000 seconds (150 to 300 minutes)
    }

    # Verifica se l'utente ha definito un range di durata
    if isinstance(user_duration_range, list) and user_duration_range:
        user_range_key = user_duration_range[0].lower()

        # Verifica se il range dell'utente è valido
        if user_range_key in duration_mapping:
            min_duration, max_duration = duration_mapping[user_range_key]
            print(f"Checking if {min_duration} <= {extracted_duration} <= {max_duration}")
        else:
            print("Invalid User Duration Range format.")
            return 0
    else:
        print("No valid user duration range provided.")
        return 0

    # Controllo finale
    if min_duration <= extracted_duration <= max_duration:
        print(f"✅ Duration Match Found for {extracted_duration} seconds")
        return 1

    print(f"❌ No Duration Match for {extracted_duration} seconds")
    return 0



import re

def movie_matches_year(movie_year, user_year_range):
    """
    Verifica se l'anno di uscita del film corrisponde all'intervallo di anni preferito dall'utente.

    Parameters:
        movie_year (int/tuple): L'anno di uscita del film, che può essere un numero o una tupla di descrizioni.
        user_year_range (str/tuple): L'intervallo di anni preferito dall'utente.

    Returns:
        int: 1 se l'anno corrisponde, altrimenti 0.
    """
    print(f"Raw Movie Year: {movie_year}, User Year Range: {user_year_range}")

    extracted_year = None

    # Se movie_year è una tupla, cerchiamo l'anno nella descrizione
    if isinstance(movie_year, tuple):
        for item in movie_year:
            if isinstance(item, str):
                # Cerca l'anno esatto come "1995"
                year_match = re.search(r"(\d{4})", item)  # Cerca un anno specifico come "1995"
                if year_match:
                    extracted_year = int(year_match.group(1))
                    print(f"Exact Year extracted: {extracted_year}")

                # Se troviamo una decade come "1990s", estrai l'inizio del decennio
                if "1990s" in item:
                    extracted_year = 1995  # Assegna un anno medio del decennio
                    print(f"Decade '1990s' extracted, setting year to {extracted_year}")

    print(f"Extracted Year: {extracted_year}")

    if extracted_year is None:
        print("No valid year extracted.")
        return 0

    # Se l'utente ha fornito un intervallo di anni come "1990s"
    if isinstance(user_year_range, str) and user_year_range.endswith('s'):
        start_year = int(user_year_range[:4])  # Estrai l'inizio del decennio (e.g., 1990)
        end_year = start_year + 9  # Imposta l'intervallo di anni fino al prossimo decennio
    elif isinstance(user_year_range, tuple) and len(user_year_range) == 2:
        # Se l'utente ha fornito un intervallo di anni specifico (ad esempio (1990, 2000))
        start_year, end_year = user_year_range
    else:
        print("Invalid user year range format. Expected a tuple with 2 values or a decade string.")
        return 0

    print(f"User Year Range: {start_year}-{end_year}")

    # Controlla se l'anno estratto è all'interno dell'intervallo specificato
    if start_year <= extracted_year <= end_year:
        print(f"✅ Year Match Found for {extracted_year}")
        return 1

    print(f"❌ No Year Match for {extracted_year}")
    return 0



def movie_matches_popularity(movie_popularity, user_popularity_threshold):
    """
    Verifica se la popolarità del film corrisponde alla soglia di popolarità dell'utente.

    Parameters:
        movie_popularity (str/tuple): Descrizione della popolarità del film, che può essere una stringa o una tupla.
        user_popularity_threshold (str): La soglia di popolarità dell'utente.

    Returns:
        int: 1 se la popolarità corrisponde, altrimenti 0.
    """
    print(f"Raw Movie Popularity: {movie_popularity}, User Popularity Threshold: {user_popularity_threshold}")

    extracted_popularity = None

    # Se movie_popularity è una tupla, cerchiamo la popolarità nella descrizione
    if isinstance(movie_popularity, tuple):
        for item in movie_popularity:
            if isinstance(item, str):
                # Estrai la parola chiave popolarità come "Blockbuster"
                match = re.search(r"it's a (\w+)", item)

                if match:
                    extracted_popularity = match.group(1)
                    break

    print(f"Extracted Popularity: {extracted_popularity}")

    if extracted_popularity is None:
        print("No valid popularity extracted.")
        return 0

    # 🛠️ Assicuriamoci che user_popularity_threshold sia un numero singolo
    if isinstance(user_popularity_threshold, (list, tuple)) and len(user_popularity_threshold) > 0:
        user_popularity_threshold = user_popularity_threshold[0]  # Prendi il primo valore se è una lista/tupla
        print(f"Extracted User Popularity Threshold: {user_popularity_threshold}")

    if not isinstance(user_popularity_threshold, (str)):
        print("Invalid User Popularity Threshold format.")
        return 0

    # Controlla se la popolarità soddisfa la soglia dell'utente
    if extracted_popularity.lower() == user_popularity_threshold[0].lower():
        print(f"Popularity Match Found")
        print(f"✅ Popularity Match Found for {movie_popularity} seconds")

        return 1

    print(f"❌ No Popularity Match for {movie_popularity} seconds")

    return 0

def hold_out_split(data, test_size=0.2):
    """
           Divide il dataset in set di addestramento e di test.

           Parameters:
               data (list): Il dataset da suddividere.
               test_size (float): La frazione di dati da usare per il test (default 0.2).

           Returns:
               tuple: Set di addestramento e set di test.
    """
    test_set_size = int(len(data) * test_size)
    random.shuffle(data)  # Shuffle to ensure randomness
    test_set = data[:test_set_size]
    training_set = data[test_set_size:]
    return training_set, test_set


def evaluate_recommendations(recommended, user_preferences, test_size=0.2):
    """
    Questa funzione valuta un sistema di raccomandazione in base a vari criteri, inclusi rilevanza, serendipità,
    novità, diversità e accettabilità. Utilizza un set di test per verificare quanto bene i film consigliati
    soddisfano le preferenze dell'utente.

    Parametri:
    - recommended (list): Una lista di film consigliati dal sistema.
    - user_preferences (dict): Un dizionario contenente le preferenze dell'utente, ad esempio 'genres',
      'director', 'actors', 'country', ecc.
    - test_size (float, opzionale): La percentuale del set di dati che verrà utilizzata per il test (default è 0.2).

    Ritorna:
    - relevance_scores (list): Una lista di punteggi di rilevanza per ciascun film nel test set.
    - serendipity_scores (list): Una lista di punteggi di serendipità per ciascun film nel test set.
    - novelty_scores (list): Una lista di punteggi di novità per ciascun film nel test set.
    - diversity_scores (list): Una lista di punteggi di diversità per ciascun film nel test set.
    """

    # Inizializzazione delle liste per salvare i punteggi di valutazione
    relevance_scores = []  # Punteggio di rilevanza: quanto le raccomandazioni sono pertinenti rispetto alle preferenze
    serendipity_scores = []  # Punteggio di serendipità: quanto le raccomandazioni sono sorprendenti (ma comunque utili)
    novelty_scores = []  # Punteggio di novità: quanto le raccomandazioni sono nuove per l'utente
    diversity_scores = []  # Punteggio di diversità: quanto le raccomandazioni coprono vari aspetti delle preferenze

    # Suddividiamo la lista di film consigliati in set di addestramento e test usando il metodo hold-out
    training_set, test_set = hold_out_split(recommended, test_size)
    print(f"\n🔄 Data Split - Training set size: {len(training_set)}, Test set size: {len(test_set)}")

    # Verifica se l'utente ha selezionato solo il genere come preferenza
    if 'genres' in user_preferences and len(user_preferences) == 1:
        print("\n🎬 Only genre preference selected, evaluating recommendations based on genre only.")

    # Ora eseguiamo la valutazione delle raccomandazioni usando il test set
    for movie in test_set:
        print(f"\n🔍 Debug - Movie: {movie}")

        matched_constraints = 0  # Contatore per i vincoli esatti che il film soddisfa
        total_constraints = len(user_preferences)  # Numero totale di preferenze dell'utente
        partial_matches = 0  # Contatore per i vincoli parzialmente soddisfatti
        novelty = 0  # Contatore per la novità: film che non soddisfano completamente le preferenze
        movie_features = []  # Lista per tracciare le caratteristiche del film che soddisfano le preferenze dell'utente

        # Se è stato selezionato solo il genere, valutiamo solo questo criterio
        if 'genres' in user_preferences and len(user_preferences) == 1:
            if movie_matches_genre(movie, user_preferences['genres']):
                matched_constraints += 1
                movie_features.append('genres')
            else:
                novelty += 1  # Il film non corrisponde al genere, quindi è considerato nuovo

        # Se sono selezionate altre preferenze, valutiamo anche altri criteri
        else:
            # Controllo per il genere
            if 'genres' in user_preferences and movie_matches_genre(movie, user_preferences['genres']):
                matched_constraints += 1
                movie_features.append('genres')
            else:
                partial_matches += 1
                novelty += 1

            # Controllo per il regista
            if 'director' in user_preferences and movie_matches_director(movie, user_preferences['director']):
                matched_constraints += 1
                movie_features.append('director')
            else:
                partial_matches += 1
                novelty += 1

            # Controllo per gli attori
            if 'actors' in user_preferences and movie_matches_actors(movie, user_preferences['actors']):
                matched_constraints += 1
                movie_features.append('actors')
            else:
                partial_matches += 1
                novelty += 1

            # Controllo per il paese di origine
            if 'country' in user_preferences and movie_matches_country(movie, user_preferences['country']):
                matched_constraints += 1
                movie_features.append('country')
            else:
                partial_matches += 1
                novelty += 1

            # Controllo per la popolarità
            if 'popularity' in user_preferences and movie_matches_popularity(movie, user_preferences['popularity']):
                matched_constraints += 1
                movie_features.append('popularity')
            else:
                partial_matches += 1
                novelty += 1

            # Controllo per la durata
            if 'duration' in user_preferences and movie_matches_duration(movie, user_preferences['duration']):
                matched_constraints += 1
                movie_features.append('duration')
            else:
                partial_matches += 1
                novelty += 1

            # Controllo per l'anno
            if 'year' in user_preferences and movie_matches_year(movie, user_preferences['year']):
                matched_constraints += 1
                movie_features.append('year')
            else:
                partial_matches += 1
                novelty += 1

        # Debug: Mostra i match per questo film
        print(
            f"✅ Exact Matches: {matched_constraints}, ❌ Partial Matches: {partial_matches}, 🎭 Total Constraints: {total_constraints}")

        # Calcolo dei punteggi
        relevance_score = matched_constraints / total_constraints  # Punteggio di rilevanza basato sui match esatti
        serendipity_score = (partial_matches + 1) / (total_constraints + 1)  # Punteggio di serendipità
        novelty_score = (novelty + 1) / (total_constraints + 1)  # Punteggio di novità (evita 0 assoluto)
        diversity_score = len(set(movie_features)) / (
                    len(movie_features) + 1) if movie_features else 0  # Punteggio di diversità

        # Salviamo i punteggi aggiornati
        relevance_scores.append(relevance_score)
        serendipity_scores.append(serendipity_score)
        novelty_scores.append(novelty_score)
        diversity_scores.append(diversity_score)


    # Calcolo dei punteggi medi
    avg_relevance = sum(relevance_scores) / len(relevance_scores) if relevance_scores else 0
    avg_serendipity = sum(serendipity_scores) / len(serendipity_scores) if serendipity_scores else 0
    avg_novelty = sum(novelty_scores) / len(novelty_scores) if novelty_scores else 0
    avg_diversity = sum(diversity_scores) / len(diversity_scores) if diversity_scores else 0

    # Mostra i punteggi medi
    print("\n📊 Average Scores for the Recommendation System:")
    print(f"🔹 Relevance: {avg_relevance * 100:.2f}%")
    print(f"🔹 Serendipity: {avg_serendipity * 100:.2f}%")
    print(f"🔹 Novelty: {avg_novelty * 100:.2f}%")
    print(f"🔹 Diversity: {avg_diversity * 100:.2f}%")


    return relevance_scores, serendipity_scores, novelty_scores, diversity_scores
