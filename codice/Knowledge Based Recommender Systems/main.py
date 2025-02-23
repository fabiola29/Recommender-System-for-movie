import streamlit as st
from utils import load_css, save_and_navigate_to_results, load_data, select_genres, select_director, select_actors, select_nationality, select_popularity_preference, select_decade, select_duration, select_tags
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
    selected_director = select_director(movies)

    # Step 3: Seleziona attori preferiti
    selected_actors = select_actors(movies)

    # Step 4: Seleziona nazionalità
    selected_nationality = select_nationality(movies)

    # Step 5: Seleziona preferenza di popolarità
    filtered_movies = select_popularity_preference(ratings, movies)

    # Step 6: Seleziona anno di uscita
    selected_decade = select_decade(movies)

    # Step 7: Seleziona durata del film
    duration = select_duration(movies)

    # Step 8: Seleziona tag del film
    selected_tags = select_tags(tags)

    # Step 9: Salva i criteri e vai alla pagina dei risultati
    if st.button("Research"):
        save_and_navigate_to_results(selected_genres, selected_director, selected_actors, selected_nationality,
                                     filtered_movies, selected_decade, duration, selected_tags)


if __name__ == "__main__":
    navigate_pages()
