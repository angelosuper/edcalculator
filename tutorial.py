import streamlit as st
from streamlit_extras.app_logo import add_logo
from streamlit_extras.switch_page_button import switch_page
from streamlit_extras.add_vertical_space import add_vertical_space

class TutorialState:
    def __init__(self):
        if 'tutorial_step' not in st.session_state:
            st.session_state.tutorial_step = 0
        if 'tutorial_enabled' not in st.session_state:
            st.session_state.tutorial_enabled = True

    def get_current_step(self):
        return st.session_state.tutorial_step

    def next_step(self):
        st.session_state.tutorial_step += 1

    def reset_tutorial(self):
        st.session_state.tutorial_step = 0

    def disable_tutorial(self):
        st.session_state.tutorial_enabled = False

    def is_enabled(self):
        return st.session_state.tutorial_enabled

def show_tooltip(key, message, placement="right"):
    """Mostra un tooltip se il tutorial è attivo e siamo al passo corretto"""
    if st.session_state.get('tutorial_enabled', True):
        with st.container():
            st.markdown(
                f"""
                <div class="tooltip-container" data-tooltip="{message}" data-placement="{placement}">
                    <style>
                    .tooltip-container {{
                        position: relative;
                        display: inline-block;
                        padding: 8px;
                        background: #0066cc;
                        color: white;
                        border-radius: 4px;
                        margin: 4px;
                        animation: pulse 2s infinite;
                    }}
                    @keyframes pulse {{
                        0% {{ transform: scale(1); }}
                        50% {{ transform: scale(1.05); }}
                        100% {{ transform: scale(1); }}
                    }}
                    </style>
                    {message}
                </div>
                """,
                unsafe_allow_html=True
            )

def show_welcome_message():
    """Mostra il messaggio di benvenuto al primo avvio"""
    if st.session_state.get('first_time', True):
        st.balloons()
        st.success("""
        👋 Benvenuto nel Calcolatore Costi Stampa 3D!
        
        Questo tutorial ti guiderà attraverso le funzionalità principali dell'applicazione.
        Puoi disattivarlo in qualsiasi momento usando il pulsante nelle impostazioni.
        """)
        if st.button("Inizia il Tutorial"):
            st.session_state.first_time = False
            st.rerun()

def get_tutorial_content(step):
    """Restituisce il contenuto del tutorial per ogni passo"""
    tutorial_steps = {
        0: {
            "title": "Selezione Materiale",
            "message": "Inizia selezionando il materiale che vuoi utilizzare per la stampa.",
            "hint": "Puoi vedere tutte le proprietà dei materiali nella tabella sopra."
        },
        1: {
            "title": "Configurazione Layer",
            "message": "Imposta l'altezza del layer. Un'altezza minore significa più dettaglio ma tempi di stampa più lunghi.",
            "hint": "Usa il slider per trovare il giusto compromesso tra qualità e velocità."
        },
        2: {
            "title": "Caricamento STL",
            "message": "Carica il tuo file STL per calcolare i costi di stampa.",
            "hint": "Assicurati che il file sia in formato STL e non superi i 200MB."
        },
        3: {
            "title": "Visualizzazione 3D",
            "message": "Esplora il tuo modello 3D con i controlli di visualizzazione.",
            "hint": "Puoi ruotare, zoomare e cambiare la modalità di visualizzazione."
        }
    }
    return tutorial_steps.get(step, None)
