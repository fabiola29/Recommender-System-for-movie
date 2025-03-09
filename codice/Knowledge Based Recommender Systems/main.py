import streamlit as st
import results
from utils import load_css, load_data, select_genres, display_director_selection, display_actor_selection, \
    display_nationality_selection, display_popularity_preference, display_movies_by_decade, display_runtime_selection, \
    save_user_preferences, select_informations_from_ttl
from confirmation_screen import confirmation_screen
from reference_film import reference_film_page

# Modulo principale dell'applicazione Streamlit per la ricerca e la raccomandazione di film.
#
# Gestisce la navigazione tra le diverse pagine dell'app e permette all'utente di
# selezionare preferenze sui film per ricevere suggerimenti personalizzati.
#
# Funzioni principali:
# - `navigate_pages()`: Controlla la navigazione tra le pagine dell'applicazione:
#   - "main": Pagina principale per l'inserimento dei criteri di ricerca.
#   - "results": Pagina dei risultati con i film consigliati.
#   - "confirmation screen": Schermata di conferma dopo la selezione del film.
#   - "reference film": Pagina per selezionare un film di riferimento simile a quelli desiderati.
#
# - `main()`: Carica l'interfaccia della pagina principale, consentendo all'utente di specificare le
#   preferenze di ricerca per trovare film rilevanti. Gli utenti possono:
#   - Selezionare generi preferiti.
#   - Scegliere registi e attori preferiti.
#   - Indicare una nazionalità preferita.
#   - Esprimere preferenze di popolarità (blockbuster o film di nicchia).
#   - Specificare una decade di uscita del film.
#   - Definire una durata preferita.
#   - Utilizzare un film di riferimento per affinare la ricerca.
#
# Avvio:
# - Il modulo viene eseguito direttamente avviando `navigate_pages()`, che determina la pagina da visualizzare.


# Funzione per gestire la navigazione tra pagine
def navigate_pages():

    # Inizializza la pagina all'avvio
    if "page" not in st.session_state:
        st.session_state.page = "main"  # Imposta la pagina iniziale

    # Naviga alla pagina corretta
    if st.session_state.page == "main":
        main()  # Mostra la pagina principale
    elif st.session_state.page == "results":
        results.results()  # Mostra la pagina dei risultati
    elif st.session_state.page == "confirmation screen":
        confirmation_screen()  # Mostra la pagina dei risultati
    elif st.session_state.page == "reference film":
        reference_film_page()


def main():

    # Carica il file CSS esterno
    load_css()

    # Titolo pagina
    st.markdown('<div class="header" style="color: red;"> 🔎 Search Film </div>', unsafe_allow_html=True)
    # Bottone per aggiungere un film di riferimento
    st.markdown(
        "If you have a movie in mind that you really enjoyed, click here, and we’ll help you find similar films.")
    if st.button("Add a film you liked"):
        st.session_state.page = "reference film"
        reference_film_page()
        st.rerun()

    st.markdown("Otherwise, tell us what you’re looking for and we’ll help you find it.")
    # Carica i dati
    movies, tags, ratings = load_data()

    # Salva 'movies' nello st.session_state
    st.session_state.movies = movies
    # st.session_state.selected_genres = None

    genres, directors, actors, nationality, years = select_informations_from_ttl(movies)
    # Step 1: Seleziona generi
    selected_genres = select_genres(genres, default=st.session_state.get("selected_genres"))

    # # Step 2: Seleziona regista preferito
    selected_director = display_director_selection(directors, default=st.session_state.get("selected_director"))

    # # Step 3: Seleziona attori preferiti
    selected_actors = display_actor_selection(actors, default=st.session_state.get("selected_actors"))

    # # Step 4: Seleziona nazionalità
    selected_nationality = display_nationality_selection(nationality, default=st.session_state.get("selected_nationality"))

    # Step 5: Seleziona preferenza di popolarità
    selected_popularity = display_popularity_preference(default=st.session_state.get("filtered_movies"))

    # # Step 6: Seleziona anno di uscita
    selected_decade = display_movies_by_decade(years, default=st.session_state.get("selected_decade"))

    # Step 7: Seleziona durata del film
    duration = display_runtime_selection(default=st.session_state.get("duration"))

    # Step 8: Salva i criteri e vai alla pagina dei risultati
    if st.button("Research"):
        st.session_state.pop("current_search_results", None)
        save_user_preferences(selected_genres, selected_director, selected_actors, selected_nationality,
                              selected_popularity, selected_decade, duration)
        st.session_state.page = "results"
        st.rerun()


if __name__ == "__main__":
    navigate_pages()