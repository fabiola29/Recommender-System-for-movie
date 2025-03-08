import streamlit as st
import recommendation
import time

import pandas as pd
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

    progress_bar = st.progress(0)  # Inizializza la barra di caricamento
    with st.spinner("Searching for the best movies..."):


        recommended = recommendation.retrieve_results(
            10, selected_genres, selected_director, selected_actors,
            selected_nationality, selected_popularity, duration,
            selected_decade, progress_bar
        )

        progress_bar.empty()  # Rimuove la barra di avanzamento

    progress_bar.empty()  # Nasconde la barra di caricamento dopo la ricerca

    # Ordina i risultati in base al punteggio (dal più alto al più basso)
    if recommended is None:
        print("Errore: `recommended` è None. Assicurati che venga popolato correttamente.")
        recommended = {}  # Imposta un dizionario vuoto per evitare il crash

    sorted_recommendations = sorted(recommended.items(), key=lambda x: x[1].get("score", 0), reverse=True)

    # Mostra i risultati ordinati
    if sorted_recommendations:
        for idx, (title, details) in enumerate(sorted_recommendations):  # ✅ Ora è ordinato per punteggio
            score = details.get("score", 0)
            explanation = details.get("explanation", "No explanation available")
            abstract = details.get("abstract", "N/A")

            # Mostra il titolo del film
            st.subheader(title)

            # Mostra lo score e l'explanation

            #st.write(f"**Score:** {score}")
            st.write(f"**Explanation:** {explanation}")

            # Make the description read-only
            st.text_area("Description", abstract, height=150, key=f"{title}_{idx}", disabled=True)

            # Mostra il pulsante per scegliere il film
            if st.button(f"Choose", key=f"choose_{idx}"):
                # Salva il film selezionato e imposta la visualizzazione della schermata successiva
                st.session_state["selected_movie"] = title
                st.session_state.page = "confirmation screen"
                st.rerun()
    else:
        st.write("No movies found matching your criteria.")

    if st.button("Not satisfied? Go back to main"):
        st.session_state.page = "main"
        st.session_state.pop("recommended_movies", None)  # ✅ Cancella i risultati per forzare una nuova query
        st.rerun()
