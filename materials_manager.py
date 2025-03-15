import streamlit as st
import requests
import pandas as pd

def fetch_materials():
    """Recupera la lista dei materiali dal backend"""
    try:
        response = requests.get("http://localhost:8000/materials/")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Errore nel recupero dei materiali: {response.status_code}")
            return []
    except Exception as e:
        st.error(f"Errore di connessione al backend: {str(e)}")
        return []

def add_material(material_data):
    """Aggiunge un nuovo materiale"""
    try:
        response = requests.post("http://localhost:8000/materials/", json=material_data)
        if response.status_code == 200:
            st.success("Materiale aggiunto con successo!")
            return True
        else:
            st.error(f"Errore nell'aggiunta del materiale: {response.status_code}")
            return False
    except Exception as e:
        st.error(f"Errore di connessione al backend: {str(e)}")
        return False

def materials_manager_page():
    st.title("Gestione Materiali")

    # Tab per visualizzare/aggiungere materiali
    tab1, tab2 = st.tabs(["Lista Materiali", "Aggiungi Materiale"])

    with tab1:
        st.subheader("Materiali Disponibili")
        materials = fetch_materials()
        if materials:
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
                })
            )

    with tab2:
        st.subheader("Aggiungi Nuovo Materiale")
        with st.form("new_material_form"):
            name = st.text_input("Nome del materiale")
            density = st.number_input("Densità (g/cm³)", min_value=0.1, value=1.24, step=0.01)
            cost_per_kg = st.number_input("Costo per kg (€)", min_value=0.1, value=20.0, step=0.1)
            min_layer_height = st.number_input("Altezza minima layer (mm)", min_value=0.05, value=0.1, step=0.05)
            max_layer_height = st.number_input("Altezza massima layer (mm)", min_value=0.1, value=0.3, step=0.05)

            st.subheader("Parametri di Stampa")
            col1, col2 = st.columns(2)

            with col1:
                default_temperature = st.number_input("Temperatura predefinita (°C)", min_value=150.0, max_value=300.0, value=200.0, step=5.0)
                default_bed_temperature = st.number_input("Temperatura piano (°C)", min_value=0.0, max_value=120.0, value=60.0, step=5.0)
                retraction_enabled = st.checkbox("Retrazione attiva", value=True)
                retraction_distance = st.number_input("Distanza retrazione (mm)", min_value=0.0, max_value=10.0, value=6.0, step=0.5)

            with col2:
                retraction_speed = st.number_input("Velocità retrazione (mm/s)", min_value=10.0, max_value=100.0, value=25.0, step=5.0)
                print_speed = st.number_input("Velocità stampa (mm/s)", min_value=10.0, max_value=200.0, value=60.0, step=5.0)
                first_layer_speed = st.number_input("Velocità primo layer (mm/s)", min_value=5.0, max_value=100.0, value=30.0, step=5.0)
                fan_speed = st.number_input("Velocità ventola (%)", min_value=0, max_value=100, value=100, step=5)
                flow_rate = st.number_input("Flusso (%)", min_value=50, max_value=200, value=100, step=5)

            submit_button = st.form_submit_button("Aggiungi Materiale")

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
                add_material(material_data)