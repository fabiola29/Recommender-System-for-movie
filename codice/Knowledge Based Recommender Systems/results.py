import streamlit as st
import recommendation
from systemEvaluation import evaluate_recommendations

# Funzione per mostrare i risultati in Streamlit
def results():

    """
       Funzione per visualizzare i risultati della ricerca dei film, sulla base dei criteri selezionati dall'utente.

       Questo metodo recupera i criteri di selezione dalla sessione di Streamlit, esegue una query per ottenere i film
       che soddisfano tali criteri, e visualizza i risultati con un'opzione per scegliere un film. Se non ci sono film
       che soddisfano i criteri, viene mostrato un messaggio di avviso.
       """

    # Titolo della pagina con il nome "results"
    st.markdown(
        '<h2 style="text-align: center; color: @white;"> 🎬 Films Recommended </h2>',
        unsafe_allow_html=True
    )


    # Recupero dei dati dalla sessione di Streamlit
    selected_genres = st.session_state.get('selected_genres', [])
    selected_director = st.session_state.get('selected_director', [])
    selected_actors = st.session_state.get('selected_actors', [])
    selected_nationality = st.session_state.get('selected_nationality', '')
    selected_decade = st.session_state.get('selected_decade', '')
    selected_popularity = st.session_state.get('filtered_movies', '')
    duration = st.session_state.get('duration', '')


    # Crea una stringa che riassume i criteri selezionati dall'utente
    criteria = "These are the results because you selected the following criteria:"

    # Aggiunge i generi selezionati
    if selected_genres:
        criteria += f"\n- **Genres**: {', '.join(selected_genres)}"
    else:
        criteria += "\n- **Genres**: Not selected"

    # Aggiunge i registi selezionati
    if selected_director:
        criteria += f"\n- **Director(s)**: {selected_director}"
    else:
        criteria += "\n- **Director(s)**: Not selected"

    # Aggiunge gli attori selezionati
    if selected_actors:
        criteria += f"\n- **Actor(s)**: {', '.join(selected_actors)}"
    else:
        criteria += "\n- **Actor(s)**: Not selected"

    # Aggiunge la nazionalità selezionata
    if selected_nationality:
        criteria += f"\n- **Nationality**: {selected_nationality}"
    else:
        criteria += "\n- **Nationality**: Not selected"

    # Aggiungie la decade selezionata
    if selected_decade:
        criteria += f"\n- **Decade**: {selected_decade}"
    else:
        criteria += "\n- **Decade**: Not selected"

    # Aggiunge la popolarità selezionata
    if selected_popularity:
        criteria += f"\n- **Popularity**: {', '.join(selected_popularity)}"
    else:
        criteria += "\n- **Popularity**: Not selected"

    # Aggiunge la durata selezionata
    if duration:
        criteria += f"\n- **Duration**: {', '.join(duration)}"
    else:
        criteria += "\n- **Duration**: Not selected"

    # Visualizza il riassunto dei criteri selezionati
    st.write(criteria)

    # Esegue la query per ottenere i risultati dei film


    recommended =  recommendation.retrieve_results(10, selected_genres, selected_director, selected_actors, selected_nationality, selected_popularity, duration, selected_decade)
    # Rimuovi i duplicati nel risultato in base al titolo del film

    user_preference = {
        "genres": selected_genres,
        "director": selected_director,
        "actors": selected_actors,
        "country": selected_nationality,
        "popularity": selected_popularity,
        "duration": duration,
        "year": selected_decade
    }

    print(f"User preferences: {user_preference}")

    # Chiamata alla funzione che valuta il sistema con una soglia di accettabilità del 50%
    evaluate_recommendations(recommended, user_preference, test_size=0.2)

    # Mostra i risultati
    if recommended:
        for idx, (movie, score, explanation, abstract) in enumerate(recommended):

            # Mostra il titolo del film
            st.subheader(movie)  # Qui movie è solo la stringa del titolo

            # Mostra lo score e l'explanation
            # st.write(f"**Score:** {score}")
            st.write(f"**Explanation:** {explanation}")

            # Make the description read-only
            st.text_area("Description", abstract, height=150, key=f"{movie}_{idx}", disabled=True)
            # Se desideri renderlo più stilizzato, puoi usare markdown
            # st.markdown(f"**Score:** {score}  \n**Explanation:** {explanation}")

            # # Mostra il pulsante per scegliere il film
            # if st.button(f"Choose", key=f"choose_{idx}"):
            #     # Mostra una notifica che l'utente ha scelto il film
            #     st.success(f"You have chosen **{movie}**!")

            if st.button(f"Choose", key=f"choose_{idx}"):
                # Salva il film selezionato e imposta la visualizzazione della schermata successiva
                st.session_state["selected_movie"] = movie
                st.session_state.page = "confirmation screen"   # Imposta la pagina a "other suggestions"
                st.rerun()

    else:
        st.write("No movies found matching your criteria.")

    # Mostra il bottone per tornare al main
    if st.button("Not satisfied? Go back to main"):
        st.session_state.page = "main"
        st.rerun()
