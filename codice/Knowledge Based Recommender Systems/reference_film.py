import streamlit as st
import utils

def reference_film_page():

    # ✅ Carica solo i film presenti nel file TTL
    movies_in_ttl = utils.get_movies_from_ttl()

    st.markdown('<div class="header"> 🎥 Add Reference Film </div>', unsafe_allow_html=True)

    if not movies_in_ttl:
        st.write("⚠️ No movies available in the dataset.")
        return

    reference_film = st.selectbox("Choose a film you liked:", movies_in_ttl)

    if st.button("Search"):
        print("DEBUG: Dopo il pulsante - Sto cercando film simili!")  # Dovrebbe apparire quando premi il pulsante

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
