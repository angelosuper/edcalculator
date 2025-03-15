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
                    'max_layer_height': 'Altezza max. layer (mm)'
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
            
            submit_button = st.form_submit_button("Aggiungi Materiale")
            
            if submit_button:
                material_data = {
                    "name": name,
                    "density": density,
                    "cost_per_kg": cost_per_kg,
                    "min_layer_height": min_layer_height,
                    "max_layer_height": max_layer_height
                }
                add_material(material_data)
