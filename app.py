import streamlit as st
import plotly.graph_objects as go
import numpy as np
import requests
import pandas as pd
import json
import base64
import io
import trimesh
import tempfile
import os
import logging

from stl_processor import process_stl, calculate_print_cost
from materials_manager import materials_manager_page, fetch_materials

# Configura logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_materials_from_api():
    """Recupera i materiali dal backend"""
    materials = fetch_materials()
    return {mat['name']: {
        'density': mat['density'],
        'cost_per_kg': mat['cost_per_kg'],
        'min_layer_height': mat['min_layer_height'],
        'max_layer_height': mat['max_layer_height']
    } for mat in materials}

def convert_stl_to_glb(stl_content):
    """Converte il contenuto STL in GLB"""
    temp_stl_path = None
    temp_glb_path = None

    try:
        logger.info("Iniziando la conversione STL -> GLB")

        # Crea un file temporaneo per il contenuto STL
        with tempfile.NamedTemporaryFile(suffix='.stl', delete=False) as temp_stl:
            temp_stl.write(stl_content)
            temp_stl_path = temp_stl.name
            logger.info(f"File STL temporaneo creato: {temp_stl_path}")

        # Carica la mesh STL
        mesh = trimesh.load(temp_stl_path)
        if not mesh.is_valid:
            raise ValueError("Mesh STL non valida")
        logger.info("Mesh STL caricata correttamente")

        # Crea un file temporaneo per il GLB
        with tempfile.NamedTemporaryFile(suffix='.glb', delete=False) as temp_glb:
            temp_glb_path = temp_glb.name

        # Esporta come GLB
        mesh.export(temp_glb_path, file_type='glb')
        logger.info("Mesh esportata come GLB")

        # Leggi il contenuto GLB
        with open(temp_glb_path, 'rb') as f:
            glb_content = f.read()

        logger.info("Conversione completata con successo")
        return base64.b64encode(glb_content).decode()

    except Exception as e:
        logger.error(f"Errore durante la conversione: {str(e)}")
        raise Exception(f"Errore nella conversione STL->GLB: {str(e)}")

    finally:
        # Pulisci i file temporanei
        try:
            if temp_stl_path and os.path.exists(temp_stl_path):
                os.unlink(temp_stl_path)
            if temp_glb_path and os.path.exists(temp_glb_path):
                os.unlink(temp_glb_path)
            logger.info("File temporanei rimossi")
        except Exception as e:
            logger.warning(f"Errore nella pulizia dei file temporanei: {str(e)}")

def main():
    # Configura la pagina
    st.set_page_config(
        page_title="3D Print Cost Calculator",
        layout="wide"
    )

    # Barra laterale
    with st.sidebar:
        st.title("Navigazione")
        st.markdown("---")
        page = st.radio(
            "Seleziona una sezione:",
            ["🧮 Calcolo Costi", "⚙️ Gestione Materiali"],
            format_func=lambda x: x.split(" ", 1)[1]
        )

    # Contenuto principale
    if page == "🧮 Calcolo Costi":
        st.title("Calcolatore Costi Stampa 3D")

        # Recupera materiali dal backend
        materials_data = get_materials_from_api()

        if not materials_data:
            st.warning("Nessun materiale disponibile. Aggiungi materiali nella sezione 'Gestione Materiali'.")
            return

        st.subheader("Selezione Materiale")

        # Sposta la tabella dei materiali in un expander
        with st.expander("📋 Mostra dettagli materiali"):
            materials_df = pd.DataFrame.from_dict(materials_data, orient='index')
            materials_df.index.name = 'Materiale'

            st.dataframe(materials_df.rename(columns={
                'density': 'Densità (g/cm³)',
                'cost_per_kg': 'Costo per kg (€)',
                'min_layer_height': 'Altezza min. layer (mm)',
                'max_layer_height': 'Altezza max. layer (mm)'
            }))

        # Modifica il selectbox per includere il costo
        material_options = {
            f"{name} (€{props['cost_per_kg']}/kg)": name 
            for name, props in materials_data.items()
        }

        selected_material_display = st.selectbox(
            "Seleziona materiale",
            options=list(material_options.keys())
        )

        # Ottieni il nome del materiale effettivo
        selected_material = material_options[selected_material_display]
        material_props = materials_data.get(selected_material)

        if material_props:
            # Layout a due colonne per i controlli
            col1, col2 = st.columns(2)

            with col1:
                layer_height = st.slider(
                    "Altezza layer (mm)",
                    min_value=material_props['min_layer_height'],
                    max_value=material_props['max_layer_height'],
                    value=0.2,
                    step=0.05
                )

            with col2:
                velocita_stampa = st.slider(
                    "Velocità di stampa (mm/s)",
                    min_value=30,
                    max_value=100,
                    value=60,
                    step=5
                )

            # Caricamento file
            st.subheader("Carica File STL")
            uploaded_file = st.file_uploader("Scegli un file STL", type=['stl'])

            if uploaded_file is not None:
                try:
                    logger.info("File STL caricato, inizio elaborazione")
                    # Processa file STL
                    file_content = uploaded_file.getvalue()
                    volume, vertices, dimensions = process_stl(file_content)

                    # Calcola costi
                    calculations = calculate_print_cost(volume, material_props, layer_height, velocita_stampa)

                    # Mostra risultati
                    st.subheader("Risultati")
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.metric("Volume", f"{calculations['volume_cm3']} cm³")
                    with col2:
                        st.metric("Peso", f"{calculations['weight_kg']} kg")
                    with col3:
                        st.metric("Costo Totale", f"€{calculations['total_cost']}")

                    # Mostra dimensioni
                    st.subheader("Dimensioni Oggetto")
                    dim_col1, dim_col2, dim_col3 = st.columns(3)
                    with dim_col1:
                        st.metric("Larghezza", f"{dimensions['width']} mm")
                    with dim_col2:
                        st.metric("Profondità", f"{dimensions['depth']} mm")
                    with dim_col3:
                        st.metric("Altezza", f"{dimensions['height']} mm")

                    # Dettaglio costi
                    st.subheader("Dettaglio Costi")
                    st.write(f"Tempo di stampa stimato: {calculations['tempo_stampa']} ore")
                    st.write(f"Costo Materiale: €{calculations['material_cost']}")
                    st.write(f"Costo Macchina: €{calculations['machine_cost']} (€30/ora)")

                    # Visualizzazione 3D semplice
                    st.subheader("Anteprima Modello")
                    try:
                        # Converti il file STL in base64
                        file_content = uploaded_file.getvalue()
                        file_base64 = base64.b64encode(file_content).decode()

                        # Crea il visualizzatore semplice
                        st.components.v1.html(
                            f"""
                            <div id="stl_viewer" style="width:100%; height:400px; border:1px solid #ddd; background:#f5f5f5;"></div>
                            <script src="https://cdn.jsdelivr.net/npm/stl-viewer@0.12.0/lib/stl-viewer.min.js"></script>
                            <script>
                                const viewer = new StlViewer(
                                    document.getElementById('stl_viewer'),
                                    { models: [
                                        {{
                                            filename: 'model.stl',
                                            content: atob('{file_base64}'),
                                            color: '#1E88E5'
                                        }}
                                    ],
                                    camera: {{
                                        target: [0, 0, 0],
                                        distance: 100
                                    }},
                                    controls: {{
                                        autoRotate: false
                                    }}
                                });
                            </script>
                            """,
                            height=400
                        )

                    except Exception as e:
                        st.error(f"Errore nel processare il file: {str(e)}")

                except Exception as e:
                    logger.error(f"Errore nel processare il file: {str(e)}")
                    st.error(f"Errore nel processare il file: {str(e)}")

    elif page == "⚙️ Gestione Materiali":
        materials_manager_page()

if __name__ == "__main__":
    main()