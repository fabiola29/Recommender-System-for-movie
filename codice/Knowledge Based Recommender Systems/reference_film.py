import streamlit as st
import utils

# """
# Modulo per la selezione di un film di riferimento nella ricerca di film simili.
#
# Gestisce la pagina in cui l'utente può selezionare un film che ha apprezzato,
# per ricevere raccomandazioni basate su film simili presenti nel dataset RDF.
#
# Funzioni principali:
# - `reference_film_page()`: Carica l'interfaccia della pagina per selezionare un film di riferimento e avviare la ricerca di film simili.
#   - Recupera l'elenco dei film disponibili nel dataset RDF.
#   - Permette all'utente di selezionare un film dal menu a tendina.
#   - Avvia la ricerca di film simili tramite `utils.search_similar_movies()`.
#   - Fornisce un pulsante per tornare alla pagina principale, resettando i criteri di ricerca precedenti.
#
# Caratteristiche:
# - Se il dataset RDF non contiene film, viene mostrato un messaggio di avviso.
# - Dopo la selezione di un film e la pressione del pulsante "Search", viene avviata la ricerca di film simili.
# - L'utente può tornare alla pagina principale azzerando le preferenze della sessione.
#
# Questo modulo aiuta a migliorare l’esperienza utente fornendo suggerimenti più mirati basati sui gusti personali.
# """

def reference_film_page():

    # Carica solo i film presenti nel file TTL
    movies_in_ttl = utils.get_movies_from_ttl()

    st.markdown('<div class="header"> 🎥 Add Reference Film </div>', unsafe_allow_html=True)

    if not movies_in_ttl:
        st.write("No movies available in the dataset.")
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
