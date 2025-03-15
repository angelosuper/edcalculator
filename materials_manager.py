import streamlit as st
import requests
import pandas as pd
import os
import time

# Ottieni l'URL del backend dall'ambiente o usa un default
BACKEND_URL = os.getenv('BACKEND_URL', 'http://localhost:8000')

def fetch_materials():
    """Recupera la lista dei materiali dal backend"""
    with st.spinner('🔄 Caricamento materiali in corso...'):
        try:
            response = requests.get(f"{BACKEND_URL}/materials/")
            if response.status_code == 200:
                # Simula un breve ritardo per mostrare l'animazione
                time.sleep(0.5)
                return response.json()
            else:
                st.error(f"Errore nel recupero dei materiali: {response.status_code}")
                return []
        except Exception as e:
            st.error(f"Errore di connessione al backend: {str(e)}")
            return []

def add_material(material_data):
    """Aggiunge un nuovo materiale"""
    with st.spinner('⏳ Aggiunta del nuovo materiale in corso...'):
        try:
            response = requests.post(f"{BACKEND_URL}/materials/", json=material_data)
            if response.status_code == 200:
                # Mostra una animazione di successo
                with st.balloons():
                    st.success("✅ Materiale aggiunto con successo!")
                return True
            else:
                st.error(f"❌ Errore nell'aggiunta del materiale: {response.status_code}")
                return False
        except Exception as e:
            st.error(f"❌ Errore di connessione al backend: {str(e)}")
            return False

def materials_manager_page():
    st.title("⚙️ Gestione Materiali")
    st.markdown("""
    Qui puoi visualizzare, aggiungere e modificare i materiali disponibili per la stampa 3D.
    Usa le schede sottostanti per gestire i tuoi materiali.
    """)

    # Contenitore per animazioni di transizione
    main_container = st.container()

    # Tab per visualizzare/aggiungere materiali
    tab1, tab2 = st.tabs(["📋 Lista Materiali", "➕ Aggiungi Materiale"])

    with tab1:
        st.subheader("📋 Materiali Disponibili")

        # Animazione di caricamento e transizione
        with st.empty():
            materials = fetch_materials()
            if materials:
                # Contenitore per la tabella con effetto fade-in
                with main_container:
                    df = pd.DataFrame(materials)
                    st.dataframe(
                        df.rename(columns={
                            'name': 'Nome',
                            'density': 'Densità (g/cm³)',
                            'cost_per_kg': 'Costo per kg (€)',
                            'min_layer_height': 'Altezza min. layer (mm)',
                            'max_layer_height': 'Altezza max. layer (mm)',
                            'default_temperature': 'Temperatura predefinita (°C)',
                            'default_bed_temperature': 'Temperatura piano (°C)',
                            'retraction_enabled': 'Retrazione attiva',
                            'retraction_distance': 'Distanza retrazione (mm)',
                            'retraction_speed': 'Velocità retrazione (mm/s)',
                            'print_speed': 'Velocità stampa (mm/s)',
                            'first_layer_speed': 'Velocità primo layer (mm/s)',
                            'fan_speed': 'Velocità ventola (%)',
                            'flow_rate': 'Flusso (%)'
                        }),
                        use_container_width=True
                    )
                    st.info("ℹ️ Scorri orizzontalmente per vedere tutti i parametri")

    with tab2:
        st.subheader("➕ Aggiungi Nuovo Materiale")
        with st.form("new_material_form"):
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("##### Parametri Base")
                name = st.text_input("Nome del materiale")
                density = st.number_input("Densità (g/cm³)", min_value=0.1, value=1.24, step=0.01)
                cost_per_kg = st.number_input("Costo per kg (€)", min_value=0.1, value=20.0, step=0.1)
                min_layer_height = st.number_input("Altezza minima layer (mm)", min_value=0.05, value=0.1, step=0.05)
                max_layer_height = st.number_input("Altezza massima layer (mm)", min_value=0.1, value=0.3, step=0.05)

            with col2:
                st.markdown("##### Temperature")
                default_temperature = st.number_input("Temperatura predefinita (°C)", min_value=150.0, max_value=300.0, value=200.0, step=5.0)
                default_bed_temperature = st.number_input("Temperatura piano (°C)", min_value=0.0, max_value=120.0, value=60.0, step=5.0)

            st.markdown("##### Parametri di Stampa")
            col3, col4 = st.columns(2)

            with col3:
                retraction_enabled = st.checkbox("Retrazione attiva", value=True)
                retraction_distance = st.number_input("Distanza retrazione (mm)", min_value=0.0, max_value=10.0, value=6.0, step=0.5)
                retraction_speed = st.number_input("Velocità retrazione (mm/s)", min_value=10.0, max_value=100.0, value=25.0, step=5.0)

            with col4:
                print_speed = st.number_input("Velocità stampa (mm/s)", min_value=10.0, max_value=200.0, value=60.0, step=5.0)
                first_layer_speed = st.number_input("Velocità primo layer (mm/s)", min_value=5.0, max_value=100.0, value=30.0, step=5.0)
                fan_speed = st.number_input("Velocità ventola (%)", min_value=0, max_value=100, value=100, step=5)
                flow_rate = st.number_input("Flusso (%)", min_value=50, max_value=200, value=100, step=5)

            submit_button = st.form_submit_button("➕ Aggiungi Materiale")

            if submit_button:
                material_data = {
                    "name": name,
                    "density": density,
                    "cost_per_kg": cost_per_kg,
                    "min_layer_height": min_layer_height,
                    "max_layer_height": max_layer_height,
                    "default_temperature": default_temperature,
                    "default_bed_temperature": default_bed_temperature,
                    "retraction_enabled": retraction_enabled,
                    "retraction_distance": retraction_distance,
                    "retraction_speed": retraction_speed,
                    "print_speed": print_speed,
                    "first_layer_speed": first_layer_speed,
                    "fan_speed": fan_speed,
                    "flow_rate": flow_rate
                }
                if add_material(material_data):
                    st.rerun()