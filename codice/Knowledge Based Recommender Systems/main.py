import streamlit as st
from Tools.scripts.generate_global_objects import Printer
import results
from utils import load_css, load_data, select_genres, display_director_selection, display_actor_selection, \
    display_nationality_selection, display_popularity_preference, display_movies_by_decade, display_runtime_selection, \
    save_user_preferences, select_informations_from_ttl
from confirmation_screen import confirmation_screen
from reference_film import reference_film_page

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