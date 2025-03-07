import streamlit as st
import utils
from systemEvaluation import evaluate_recommendations
def reference_film_page():
    movies = st.session_state.movies['title']

    st.markdown('<div class="header"> 🎥 Add Reference Film </div>', unsafe_allow_html=True)

    # Usa una selectbox per visualizzare i film
    reference_film = st.selectbox("Choose a film you liked:", movies)

    if st.button("Search"):
        # Esegui la ricerca dei film simili
        utils.search_similar_movies(reference_film)
        st.write(f"Searching for movies similar to '{reference_film}'...")


    # Bottone per tornare alla pagina principale
    if st.button("Back to main"):
        st.session_state.selected_genres = None
        st.session_state.selected_director = None
        st.session_state.selected_actors = None
        st.session_state.selected_nationality = None
        st.session_state.selected_decade = None
        st.session_state.filtered_movies = None
        st.session_state.duration = None
        st.session_state.page = "main"
        st.rerun()
