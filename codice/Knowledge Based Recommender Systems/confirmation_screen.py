import streamlit as st

# Modulo Streamlit per la schermata di conferma della scelta del film.
#
# Questa funzione `confirmation_screen` visualizza un messaggio di conferma dopo la selezione del film,
# indicando all'utente che il film sta per iniziare. Include inoltre un pulsante per tornare alla
# pagina principale, ripristinando lo stato della sessione relativo ai criteri di selezione e
# reimpostando la pagina principale dell'app.
#
# Funzioni:
# - `confirmation_screen()`: Mostra il messaggio di conferma e il pulsante per il ritorno alla pagina principale.


def confirmation_screen():
    # Cambia il contenuto della pagina dopo la scelta del film
    st.markdown(
        '<h2 style="text-align: center; color: @white;"> 🎥 Enjoy your movie! </h2>',
        unsafe_allow_html=True
    )
    st.write("The film is about to start. Sit back and enjoy the show!")

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
