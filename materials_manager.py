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

def update_material(material_id, material_data):
    """Aggiorna un materiale esistente"""
    with st.spinner('🔄 Aggiornamento del materiale in corso...'):
        try:
            response = requests.patch(f"{BACKEND_URL}/materials/{material_id}", json=material_data)
            if response.status_code == 200:
                st.success("✅ Materiale aggiornato con successo!")
                return True
            else:
                st.error(f"❌ Errore nell'aggiornamento del materiale: {response.status_code}")
                return False
        except Exception as e:
            st.error(f"❌ Errore di connessione al backend: {str(e)}")
            return False

def delete_material(material_id):
    """Elimina un materiale"""
    with st.spinner('🗑️ Eliminazione del materiale in corso...'):
        try:
            response = requests.delete(f"{BACKEND_URL}/materials/{material_id}")
            if response.status_code == 200:
                st.success("✅ Materiale eliminato con successo!")
                return True
            else:
                st.error(f"❌ Errore nell'eliminazione del materiale: {response.status_code}")
                return False
        except Exception as e:
            st.error(f"❌ Errore di connessione al backend: {str(e)}")
            return False

def material_form(default_values=None):
    """Form per l'aggiunta/modifica di un materiale"""
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("##### Parametri Base")
        name = st.text_input("Nome del materiale", value=default_values.get('name', '') if default_values else '')
        density = st.number_input("Densità (g/cm³)", min_value=0.1, value=float(default_values.get('density', 1.24)) if default_values else 1.24, step=0.01)
        cost_per_kg = st.number_input("Costo per kg (€)", min_value=0.1, value=float(default_values.get('cost_per_kg', 20.0)) if default_values else 20.0, step=0.1)
        min_layer_height = st.number_input("Altezza minima layer (mm)", min_value=0.05, value=float(default_values.get('min_layer_height', 0.1)) if default_values else 0.1, step=0.05)
        max_layer_height = st.number_input("Altezza massima layer (mm)", min_value=0.1, value=float(default_values.get('max_layer_height', 0.3)) if default_values else 0.3, step=0.05)

    with col2:
        st.markdown("##### Temperature")
        default_temperature = st.number_input("Temperatura predefinita (°C)", min_value=150.0, max_value=300.0, value=float(default_values.get('default_temperature', 200.0)) if default_values else 200.0, step=5.0)
        default_bed_temperature = st.number_input("Temperatura piano (°C)", min_value=0.0, max_value=120.0, value=float(default_values.get('default_bed_temperature', 60.0)) if default_values else 60.0, step=5.0)

    st.markdown("##### Parametri di Stampa")
    col3, col4 = st.columns(2)

    with col3:
        retraction_enabled = st.checkbox("Retrazione attiva", value=bool(default_values.get('retraction_enabled', True)) if default_values else True)
        retraction_distance = st.number_input("Distanza retrazione (mm)", min_value=0.0, max_value=10.0, value=float(default_values.get('retraction_distance', 6.0)) if default_values else 6.0, step=0.5)
        retraction_speed = st.number_input("Velocità retrazione (mm/s)", min_value=10.0, max_value=100.0, value=float(default_values.get('retraction_speed', 25.0)) if default_values else 25.0, step=5.0)

    with col4:
        print_speed = st.number_input("Velocità stampa (mm/s)", min_value=10.0, max_value=200.0, value=float(default_values.get('print_speed', 60.0)) if default_values else 60.0, step=5.0)
        first_layer_speed = st.number_input("Velocità primo layer (mm/s)", min_value=5.0, max_value=100.0, value=float(default_values.get('first_layer_speed', 30.0)) if default_values else 30.0, step=5.0)
        fan_speed = st.number_input("Velocità ventola (%)", min_value=0, max_value=100, value=int(default_values.get('fan_speed', 100)) if default_values else 100, step=5)
        flow_rate = st.number_input("Flusso (%)", min_value=50, max_value=200, value=int(default_values.get('flow_rate', 100)) if default_values else 100, step=5)

    return {
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

def materials_manager_page():
    st.title("⚙️ Gestione Materiali")
    st.markdown("""
    Qui puoi visualizzare, aggiungere, modificare ed eliminare i materiali disponibili per la stampa 3D.
    Usa le schede sottostanti per gestire i tuoi materiali.
    """)

    # Stato per tenere traccia del materiale in modifica
    if 'editing_material' not in st.session_state:
        st.session_state.editing_material = None

    # Tab per visualizzare/aggiungere materiali
    tab1, tab2 = st.tabs(["📋 Lista Materiali", "➕ Aggiungi Materiale"])

    with tab1:
        st.subheader("📋 Lista dei Materiali")

        # Animazione di caricamento e transizione
        with st.empty():
            materials = fetch_materials()
            if materials:
                for material in materials:
                    with st.container():
                        col1, col2, col3 = st.columns([3, 1, 1])
                        with col1:
                            st.markdown(f"#### {material['name']}")
                            st.write(f"Densità: {material['density']} g/cm³ | Costo: €{material['cost_per_kg']}/kg")
                        with col2:
                            if st.button("✏️ Modifica", key=f"edit_{material['id']}"):
                                st.session_state.editing_material = material
                                st.experimental_rerun()
                        with col3:
                            if st.button("🗑️ Elimina", key=f"delete_{material['id']}"):
                                if delete_material(material['id']):
                                    st.experimental_rerun()
                        st.markdown("---")

                # Form di modifica se un materiale è selezionato
                if st.session_state.editing_material:
                    st.subheader(f"✏️ Modifica {st.session_state.editing_material['name']}")
                    with st.form("edit_material_form"):
                        material_data = material_form(st.session_state.editing_material)
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.form_submit_button("💾 Salva Modifiche"):
                                if update_material(st.session_state.editing_material['id'], material_data):
                                    st.session_state.editing_material = None
                                    st.experimental_rerun()
                        with col2:
                            if st.form_submit_button("❌ Annulla"):
                                st.session_state.editing_material = None
                                st.experimental_rerun()

    with tab2:
        st.subheader("➕ Aggiungi Nuovo Materiale")
        with st.form("new_material_form"):
            material_data = material_form()
            if st.form_submit_button("➕ Aggiungi Materiale"):
                if add_material(material_data):
                    st.experimental_rerun()