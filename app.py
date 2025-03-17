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
        'max_layer_height': mat['max_layer_height'],
        'hourly_cost': mat.get('hourly_cost', 30)  # Aggiungi il costo orario
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

    # Stile CSS per ridurre la larghezza della sidebar
    st.markdown("""
        <style>
        [data-testid="stSidebar"][aria-expanded="true"] {
            width: 200px;
        }
        [data-testid="stSidebar"][aria-expanded="false"] {
            width: 200px;
            margin-left: -200px;
        }
        </style>
    """, unsafe_allow_html=True)

    # Barra laterale
    with st.sidebar:
        st.title("Navigazione")
        st.markdown("---")
        page = st.radio(
            "Seleziona una sezione:",
            ["🧮 Calcolo Costi", "⚙️ Gestione Materiali"],
            format_func=lambda x: x.split(" ", 1)[1]
        )

        # Sezione Download Documentazione
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 📥 Download Documentazione")

        def get_file_content_as_string(file_path):
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()

        docs = {
            "Struttura Applicazione": "documentation/app_structure.txt",
            "Istruzioni Deployment": "documentation/deployment_instructions.txt",
            "Documentazione Codice": "documentation/code_documentation.txt",
            "README": "documentation/README.txt"
        }

        selected_doc = st.sidebar.selectbox(
            "Seleziona documento da scaricare:",
            list(docs.keys())
        )

        if selected_doc:
            file_path = docs[selected_doc]
            try:
                file_content = get_file_content_as_string(file_path)
                st.sidebar.download_button(
                    label=f"📥 Download {selected_doc}",
                    data=file_content,
                    file_name=file_path.split('/')[-1],
                    mime="text/plain"
                )
            except Exception as e:
                st.sidebar.error(f"Errore nel caricamento del file: {str(e)}")

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
                'max_layer_height': 'Altezza max. layer (mm)',
                'hourly_cost': 'Costo orario (€)'
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
            # Layout per layer height e numero copie
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
                num_copies = st.number_input(
                    "Numero di copie",
                    min_value=1,
                    value=1,
                    step=1,
                    help="Inserisci il numero di copie da stampare"
                )

            # Caricamento file
            st.subheader("Anteprima Modello")
            uploaded_file = st.file_uploader("Scegli un file STL", type=['stl'])

            # Visualizzatore 3D
            viewer_html = f"""
            <div style="position: relative; width:100%; max-width:500px; margin:0 auto;">
                <div id="stl_viewer" style="width:100%; height:500px; border:1px solid #ddd; background:#f5f5f5;">
                    {"<div style='display: flex; height: 100%; align-items: center; justify-content: center; color: #666;'>Carica un file STL per visualizzare il modello 3D</div>" if not uploaded_file else ""}
                </div>
                <div style="position: absolute; bottom: 10px; right: 10px; display: flex; gap: 5px;">
                    <button onclick="resetCamera()" style="padding: 5px 10px; background: white; border: 1px solid #ddd; border-radius: 4px;">
                        🔄 Reset
                    </button>
                    <button onclick="zoomIn()" style="padding: 5px 10px; background: white; border: 1px solid #ddd; border-radius: 4px;">
                        🔍+ Zoom In
                    </button>
                    <button onclick="zoomOut()" style="padding: 5px 10px; background: white; border: 1px solid #ddd; border-radius: 4px;">
                        🔍- Zoom Out
                    </button>
                </div>
            </div>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r113/three.min.js"></script>
            <script src="https://cdn.rawgit.com/mrdoob/three.js/r113/examples/js/loaders/STLLoader.js"></script>
            <script src="https://cdn.rawgit.com/mrdoob/three.js/r113/examples/js/controls/OrbitControls.js"></script>
            <script>
                let camera, controls;

                // Verifica che Three.js sia caricato
                if (typeof THREE === 'undefined') {{
                    document.getElementById('stl_viewer').innerHTML = 
                        '<div style="color: red; padding: 20px;">Three.js non è stato caricato</div>';
                    throw new Error('Three.js non è stato caricato');
                }}

                // Setup base
                const container = document.getElementById('stl_viewer');
                const scene = new THREE.Scene();
                scene.background = new THREE.Color(0xf5f5f5);

                camera = new THREE.PerspectiveCamera(
                    75, 1, 0.1, 1000  // aspect ratio 1:1 per vista quadrata
                );
                camera.position.set(100, 100, 100);
                camera.lookAt(0, 0, 0);

                const renderer = new THREE.WebGLRenderer({{antialias: true}});
                renderer.setSize(500, 500);  // Dimensioni fisse quadrate
                renderer.shadowMap.enabled = true;  // Abilita le ombre
                renderer.shadowMap.type = THREE.PCFSoftShadowMap;  // Ombre morbide
                container.appendChild(renderer.domElement);

                // Aggiungi controlli orbitali
                controls = new THREE.OrbitControls(camera, renderer.domElement);
                controls.enableDamping = true;
                controls.dampingFactor = 0.05;
                controls.screenSpacePanning = true;
                controls.minDistance = 50;
                controls.maxDistance = 300;
                controls.maxPolarAngle = Math.PI;

                // Sistema di illuminazione migliorato
                const ambientLight = new THREE.AmbientLight(0x404040, 0.8);  // Aumentata intensità
                scene.add(ambientLight);

                // Luce principale dall'alto-destra
                const mainLight = new THREE.DirectionalLight(0xffffff, 1.0);  // Aumentata intensità
                mainLight.position.set(2, 2, 1).normalize();
                mainLight.castShadow = true;
                scene.add(mainLight);

                // Luce di riempimento frontale
                const fillLight = new THREE.DirectionalLight(0xffffff, 0.4);
                fillLight.position.set(-1, 0, 2).normalize();
                scene.add(fillLight);

                // Luce dal basso per dettagli
                const bottomLight = new THREE.DirectionalLight(0xffffff, 0.3);
                bottomLight.position.set(0, -1, 0).normalize();
                scene.add(bottomLight);

                // Luce posteriore per evidenziare i bordi
                const backLight = new THREE.DirectionalLight(0xffffff, 0.3);
                backLight.position.set(-1, 1, -2).normalize();
                scene.add(backLight);

                // Funzioni di controllo camera
                window.resetCamera = function() {{
                    camera.position.set(100, 100, 100);
                    camera.lookAt(0, 0, 0);
                    controls.reset();
                }}

                window.zoomIn = function() {{
                    camera.position.multiplyScalar(0.8);
                }}

                window.zoomOut = function() {{
                    camera.position.multiplyScalar(1.2);
                }}

                {'''
                // Carica il modello STL
                const loader = new THREE.STLLoader();
                const modelData = atob("''' + (base64.b64encode(uploaded_file.getvalue()).decode() if uploaded_file else '') + '''");
                const buffer = new Uint8Array(modelData.length);
                for (let i = 0; i < modelData.length; i++) {
                    buffer[i] = modelData.charCodeAt(i);
                }

                try {
                    const geometry = loader.parse(buffer.buffer);
                    const material = new THREE.MeshPhongMaterial({
                        color: 0x1E88E5,
                        shininess: 50,  // Aumentato per più riflessi
                        specular: 0x444444,  // Colore dei riflessi più intenso
                        flatShading: false  // Shading più smooth
                    });
                    const mesh = new THREE.Mesh(geometry, material);
                    mesh.castShadow = true;
                    mesh.receiveShadow = true;

                    // Auto-centraggio e scala
                    geometry.computeBoundingBox();
                    const center = new THREE.Vector3();
                    geometry.boundingBox.getCenter(center);
                    mesh.position.sub(center);

                    // Calcola scala appropriata
                    const size = new THREE.Vector3();
                    geometry.boundingBox.getSize(size);
                    const maxDim = Math.max(size.x, size.y, size.z);
                    const scale = 100 / maxDim;
                    mesh.scale.multiplyScalar(scale);

                    scene.add(mesh);
                } catch (error) {
                    console.error('Errore nel parsing STL:', error);
                    container.innerHTML = '<div style="color: red; padding: 20px;">Errore nel caricamento del modello</div>';
                }
                ''' if uploaded_file else ""}

                // Loop di rendering
                function animate() {{
                    requestAnimationFrame(animate);
                    controls.update();
                    renderer.render(scene, camera);
                }}
                animate();

                // Gestione ridimensionamento
                window.addEventListener('resize', function() {{
                    camera.updateProjectionMatrix();
                }});
            </script>
            """

            st.components.v1.html(viewer_html, height=520)  # Aumentata altezza per contenere il visualizzatore quadrato

            if uploaded_file is not None:
                try:
                    # Processa file STL
                    volume, vertices, dimensions = process_stl(uploaded_file.getvalue())

                    # Calcola costi per un singolo pezzo
                    calculations = calculate_print_cost(volume, material_props, layer_height)

                    # Mostra risultati per pezzo singolo
                    st.subheader("Risultati per Singolo Pezzo")

                    # Metriche con dimensioni ridotte
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.markdown('<div class="metric-container">', unsafe_allow_html=True)
                        st.metric("Volume", f"{calculations['volume_cm3']:.2f} cm³")
                        st.markdown('</div>', unsafe_allow_html=True)
                    with col2:
                        st.markdown('<div class="metric-container">', unsafe_allow_html=True)
                        st.metric("Peso", f"{calculations['weight_kg']:.3f} kg")
                        st.markdown('</div>', unsafe_allow_html=True)
                    with col3:
                        st.markdown('<div class="metric-container">', unsafe_allow_html=True)
                        st.metric("Costo", f"€{calculations['total_cost']:.2f}")
                        st.markdown('</div>', unsafe_allow_html=True)

                    # Applica stile CSS per ridurre la dimensione dei caratteri
                    st.markdown("""
                    <style>
                    .metric-container {
                        font-size: 0.9em;
                    }
                    .metric-label {
                        font-size: 0.8em;
                        color: #555;
                    }
                    .metric-value {
                        font-size: 1em;
                        font-weight: bold;
                    }
                    </style>
                    """, unsafe_allow_html=True)

                    # Mostra dimensioni con dimensioni ridotte
                    st.markdown("##### Dimensioni Oggetto")
                    dim_col1, dim_col2, dim_col3 = st.columns(3)
                    with dim_col1:
                        st.markdown('<div class="metric-container">', unsafe_allow_html=True)
                        st.metric("Larghezza", f"{dimensions['width']:.1f} mm")
                        st.markdown('</div>', unsafe_allow_html=True)
                    with dim_col2:
                        st.markdown('<div class="metric-container">', unsafe_allow_html=True)
                        st.metric("Profondità", f"{dimensions['depth']:.1f} mm")
                        st.markdown('</div>', unsafe_allow_html=True)
                    with dim_col3:
                        st.markdown('<div class="metric-container">', unsafe_allow_html=True)
                        st.metric("Altezza", f"{dimensions['height']:.1f} mm")
                        st.markdown('</div>', unsafe_allow_html=True)

                    # Dettaglio costi per pezzo con dimensioni ridotte
                    st.markdown("##### Dettaglio Costi per Pezzo")
                    st.markdown('<div class="metric-container">', unsafe_allow_html=True)
                    st.write(f"Tempo di stampa stimato: {calculations['tempo_stampa']:.1f} ore")
                    st.write(f"Costo Materiale: €{calculations['material_cost']:.2f}")
                    st.write(f"Costo Macchina: €{calculations['machine_cost']:.2f}")
                    st.markdown('</div>', unsafe_allow_html=True)

                    # Mostra totale per tutte le copie se num_copies > 1
                    if num_copies > 1:
                        st.markdown("##### Totale per più pezzi")
                        total_cost = calculations['total_cost'] * num_copies
                        total_volume = calculations['volume_cm3'] * num_copies
                        total_weight = calculations['weight_kg'] * num_copies
                        total_time = calculations['tempo_stampa'] * num_copies

                        tcol1, tcol2, tcol3 = st.columns(3)
                        with tcol1:
                            st.markdown('<div class="metric-container">', unsafe_allow_html=True)
                            st.metric("Volume Totale", f"{total_volume:.2f} cm³")
                            st.markdown('</div>', unsafe_allow_html=True)
                        with tcol2:
                            st.markdown('<div class="metric-container">', unsafe_allow_html=True)
                            st.metric("Peso Totale", f"{total_weight:.3f} kg")
                            st.markdown('</div>', unsafe_allow_html=True)
                        with tcol3:
                            st.markdown('<div class="metric-container">', unsafe_allow_html=True)
                            st.metric("Costo Totale", f"€{total_cost:.2f}")
                            st.markdown('</div>', unsafe_allow_html=True)

                except Exception as e:
                    logger.error(f"Errore nel processare il file: {str(e)}")
                    st.error(f"Errore nel processare il file: {str(e)}")

    elif page == "⚙️ Gestione Materiali":
        materials_manager_page()

if __name__ == "__main__":
    main()