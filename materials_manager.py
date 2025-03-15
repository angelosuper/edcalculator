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

def validate_material_data(data):
    """Valida i dati del materiale"""
    required_fields = ['name', 'density', 'cost_per_kg', 'min_layer_height', 'max_layer_height']

    for field in required_fields:
        if not data.get(field):
            st.error(f"Campo obbligatorio mancante: {field}")
            return False

    numeric_fields = [
        'density', 'cost_per_kg', 'min_layer_height', 'max_layer_height',
        'default_temperature', 'default_bed_temperature', 'retraction_distance',
        'retraction_speed', 'print_speed', 'first_layer_speed'
    ]

    for field in numeric_fields:
        if field in data and data[field] <= 0:
            st.error(f"Il valore di {field} deve essere maggiore di zero")
            return False

    return True

def add_material(material_data):
    """Aggiunge un nuovo materiale"""
    if not validate_material_data(material_data):
        return False

    try:
        response = requests.post(
            f"{BACKEND_URL}/materials/",
            json=material_data,
            headers={"Content-Type": "application/json"}
        )

        if response.status_code == 200:
            st.success("✅ Materiale aggiunto con successo!")
            return True
        else:
            error_detail = response.json().get('detail', 'Errore sconosciuto')
            st.error(f"Errore nell'aggiunta del materiale: {error_detail}")
            return False
    except Exception as e:
        st.error(f"Errore durante l'aggiunta del materiale: {str(e)}")
        return False

def update_material(material_id, material_data):
    """Aggiorna un materiale esistente"""
    if not validate_material_data(material_data):
        return False

    try:
        response = requests.patch(
            f"{BACKEND_URL}/materials/{material_id}",
            json=material_data,
            headers={"Content-Type": "application/json"}
        )

        if response.status_code == 200:
            st.success("✅ Materiale aggiornato con successo!")
            return True
        else:
            error_detail = response.json().get('detail', 'Errore sconosciuto')
            st.error(f"Errore nell'aggiornamento del materiale: {error_detail}")
            return False
    except Exception as e:
        st.error(f"Errore durante l'aggiornamento del materiale: {str(e)}")
        return False

def delete_material(material_id):
    """Elimina un materiale"""
    try:
        response = requests.delete(f"{BACKEND_URL}/materials/{material_id}")
        if response.status_code == 200:
            st.success("✅ Materiale eliminato con successo!")
            return True
        else:
            error_detail = response.json().get('detail', 'Errore sconosciuto')
            st.error(f"Errore nell'eliminazione del materiale: {error_detail}")
            return False
    except Exception as e:
        st.error(f"Errore durante l'eliminazione del materiale: {str(e)}")
        return False

def materials_manager_page():
    st.title("⚙️ Gestione Materiali")
    st.markdown("""
    Qui puoi visualizzare, aggiungere, modificare ed eliminare i materiali disponibili per la stampa 3D.
    """)

    # Sezione per aggiungere un nuovo materiale
    with st.expander("➕ Aggiungi Nuovo Materiale", expanded=False):
        col1, col2 = st.columns(2)

        with col1:
            name = st.text_input("Nome del materiale")
            density = st.number_input("Densità (g/cm³)", min_value=0.1, value=1.24, step=0.01)
            cost_per_kg = st.number_input("Costo per kg (€)", min_value=0.1, value=20.0, step=0.1)
            min_layer_height = st.number_input("Altezza minima layer (mm)", min_value=0.05, value=0.1, step=0.05)
            max_layer_height = st.number_input("Altezza massima layer (mm)", min_value=0.1, value=0.3, step=0.05)

        with col2:
            default_temperature = st.number_input("Temperatura predefinita (°C)", min_value=150.0, value=200.0, step=5.0)
            default_bed_temperature = st.number_input("Temperatura piano (°C)", min_value=0.0, value=60.0, step=5.0)
            retraction_enabled = st.checkbox("Retrazione attiva", value=True)
            retraction_distance = st.number_input("Distanza retrazione (mm)", min_value=0.0, value=6.0, step=0.5)
            retraction_speed = st.number_input("Velocità retrazione (mm/s)", min_value=10.0, value=25.0, step=5.0)

        if st.button("➕ Aggiungi Materiale"):
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
                "print_speed": 60.0,
                "first_layer_speed": 30.0,
                "fan_speed": 100,
                "flow_rate": 100
            }
            if add_material(material_data):
                st.rerun()

    # Lista dei materiali esistenti
    st.markdown("### 📋 Materiali Esistenti")
    materials = fetch_materials()

    if not materials:
        st.info("Nessun materiale presente. Aggiungi il tuo primo materiale!")
        return

    # Visualizza i materiali come cards
    for material in materials:
        with st.container():
            col1, col2, col3 = st.columns([3, 1, 1])

            with col1:
                st.markdown(f"#### {material['name']}")
                st.markdown(f"""
                - Densità: {material['density']} g/cm³
                - Costo: €{material['cost_per_kg']}/kg
                - Layer: {material['min_layer_height']}-{material['max_layer_height']} mm
                """)

            with col2:
                if st.button("✏️ Modifica", key=f"edit_{material['id']}"):
                    st.session_state.editing_material_id = material['id']
                    st.rerun()

            with col3:
                if st.button("🗑️ Elimina", key=f"delete_{material['id']}"):
                    if delete_material(material['id']):
                        st.rerun()

            # Se questo materiale è in modalità modifica
            if st.session_state.get('editing_material_id') == material['id']:
                with st.container():
                    st.markdown("#### Modifica Materiale")
                    col1, col2 = st.columns(2)

                    with col1:
                        new_name = st.text_input("Nome", value=material['name'], key=f"edit_name_{material['id']}")
                        new_density = st.number_input("Densità", value=material['density'], key=f"edit_density_{material['id']}")
                        new_cost = st.number_input("Costo per kg", value=material['cost_per_kg'], key=f"edit_cost_{material['id']}")

                    with col2:
                        new_min_layer = st.number_input("Min Layer", value=material['min_layer_height'], key=f"edit_min_{material['id']}")
                        new_max_layer = st.number_input("Max Layer", value=material['max_layer_height'], key=f"edit_max_{material['id']}")

                    col3, col4 = st.columns(2)
                    with col3:
                        if st.button("💾 Salva", key=f"save_{material['id']}"):
                            updated_data = {
                                "name": new_name,
                                "density": new_density,
                                "cost_per_kg": new_cost,
                                "min_layer_height": new_min_layer,
                                "max_layer_height": new_max_layer
                            }
                            if update_material(material['id'], updated_data):
                                st.session_state.editing_material_id = None
                                st.rerun()

                    with col4:
                        if st.button("❌ Annulla", key=f"cancel_{material['id']}"):
                            st.session_state.editing_material_id = None
                            st.rerun()

            st.markdown("---")