import streamlit as st
from Tools.scripts.generate_global_objects import Printer
import results
from utils import load_css, load_data, select_genres, display_director_selection, display_actor_selection, display_nationality_selection, display_popularity_preference, display_movies_by_decade, display_runtime_selection, save_and_navigate_to_results
from confirmation_screen import confirmation_screen

# Funzione per gestire la navigazione tra pagine
def navigate_pages():

    # Inizializza la pagina all'avvio
    if "page" not in st.session_state:
        st.session_state.page = "main"  # Imposta la pagina iniziale

    # Naviga alla pagina corretta
    if st.session_state.page == "main":
        main()  # Mostra la pagina principale
    elif st.session_state.page == "results":
        print("ANDIAMO ENI RISULTATI")
        results.results()  # Mostra la pagina dei risultati
    elif st.session_state.page == "confirmation screen":
        confirmation_screen()  # Mostra la pagina dei risultati


def main():

    # Carica il file CSS esterno
    load_css()

    # Titolo pagina
    st.markdown('<div class="header" style="color: red;"> 🔎 Search Film </div>', unsafe_allow_html=True)

    # Carica i dati
    movies, tags, ratings = load_data()

    # st.session_state.selected_genres = None

    # Step 1: Seleziona generi
    selected_genres = select_genres(movies, default=st.session_state.get("selected_genres"))
    print("GENRE SELEZIONATO è ")
    print(selected_genres)

    # Step 2: Seleziona regista preferito
    selected_director = display_director_selection(movies, default=st.session_state.get("selected_director"))
    print("DIRECTOR ")
    print(selected_director)


    # Step 3: Seleziona attori preferiti
    selected_actors = display_actor_selection(movies, default=st.session_state.get("selected_actors"))
    print("ATTORI ")
    print(selected_actors)

    # Step 4: Seleziona nazionalità
    selected_nationality = display_nationality_selection(movies, default=st.session_state.get("selected_nationality"))
    print("NAZIONALITA")
    print(selected_nationality)

    # Step 5: Seleziona preferenza di popolarità
    selected_popularity = display_popularity_preference(default=st.session_state.get("filtered_movies"))
    print("PREFERENZA ")
    print(selected_popularity)

    # Step 6: Seleziona anno di uscita
    selected_decade = display_movies_by_decade(movies, default=st.session_state.get("selected_decade"))
    print("ANNO")
    print(selected_decade)

    # Step 7: Seleziona durata del film
    duration = display_runtime_selection(default=st.session_state.get("duration"))
    print("DURATA")
    print(duration)

    # Step 8: Salva i criteri e vai alla pagina dei risultati
    if st.button("Research"):
        save_and_navigate_to_results(selected_genres, selected_director, selected_actors, selected_nationality,
                                     selected_popularity, selected_decade, duration)
        st.session_state.page = "results"
        st.rerun()


if __name__ == "__main__":
    navigate_pages()