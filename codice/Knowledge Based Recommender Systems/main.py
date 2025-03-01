import streamlit as st
from utils import load_css, load_data, select_genres, display_director_selection, display_actor_selection, display_nationality_selection, display_popularity_preference, display_movies_by_decade, display_runtime_selection, save_and_navigate_to_results
from results import results
from other_suggestions import other_suggestions

# Funzione per gestire la navigazione tra pagine
def navigate_pages():

    # Inizializza la pagina all'avvio
    if "page" not in st.session_state:
        st.session_state.page = "main"  # Imposta la pagina iniziale

    # Naviga alla pagina corretta
    if st.session_state.page == "main":
        main()  # Mostra la pagina principale
    elif st.session_state.page == "results":
        results()  # Mostra la pagina dei risultati
    elif st.session_state.page == "other suggestions":
        other_suggestions()  # Mostra la pagina dei risultati

def main():

    # Carica il file CSS esterno
    load_css()

    # Titolo pagina
    st.markdown('<div class="header"> 🔎 Search Film </div>', unsafe_allow_html=True)

    # Carica i dati
    movies, tags, ratings = load_data()

    # Step 1: Seleziona generi
    selected_genres = select_genres(movies)

    # Step 2: Seleziona regista preferito
    selected_director = display_director_selection(movies)

    # Step 3: Seleziona attori preferiti
    selected_actors = display_actor_selection(movies)

    # Step 4: Seleziona nazionalità
    selected_nationality = display_nationality_selection(movies)

    # Step 5: Seleziona preferenza di popolarità
    filtered_movies = display_popularity_preference(ratings, movies)

    # Step 6: Seleziona anno di uscita
    selected_decade = display_movies_by_decade(movies)

    # Step 7: Seleziona durata del film
    duration = display_runtime_selection(movies)

    # Step 8: Salva i criteri e vai alla pagina dei risultati
    if st.button("Research"):
        save_and_navigate_to_results(selected_genres, selected_director, selected_actors, selected_nationality,
                                     filtered_movies, selected_decade, duration)


if __name__ == "__main__":
    navigate_pages()
