import streamlit as st


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
