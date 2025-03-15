import streamlit as st
import plotly.graph_objects as go
import numpy as np
import requests
import pandas as pd
import json
import base64
import io

from stl_processor import process_stl, calculate_print_cost
from materials_manager import materials_manager_page, fetch_materials

def get_materials_from_api():
    """Recupera i materiali dal backend"""
    materials = fetch_materials()
    return {mat['name']: {
        'density': mat['density'],
        'cost_per_kg': mat['cost_per_kg'],
        'min_layer_height': mat['min_layer_height'],
        'max_layer_height': mat['max_layer_height']
    } for mat in materials}

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
                    # Processa file STL
                    file_content = uploaded_file.read()
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

                    # Visualizzazione 3D
                    st.subheader("Anteprima Modello")

                    try:
                        # Converti il file STL in base64
                        file_content = uploaded_file.getvalue()
                        file_base64 = base64.b64encode(file_content).decode()

                        # Visualizzatore STL ottimizzato
                        st.components.v1.html(
                            f"""
                            <div id="stl_viewer" style="width:100%; height:400px; border:1px solid #ddd; background:#f5f5f5;"></div>
                            <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
                            <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/loaders/STLLoader.js"></script>
                            <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
                            <script>
                                // Contenitore e dimensioni
                                const container = document.getElementById('stl_viewer');
                                const width = container.clientWidth;
                                const height = container.clientHeight;

                                // Scene setup
                                const scene = new THREE.Scene();
                                scene.background = new THREE.Color(0xf5f5f5);

                                // Camera setup
                                const camera = new THREE.PerspectiveCamera(75, width / height, 0.1, 1000);
                                camera.position.set(100, 100, 100);

                                // Renderer setup
                                const renderer = new THREE.WebGLRenderer({ antialias: true });
                                renderer.setSize(width, height);
                                container.appendChild(renderer.domElement);

                                // Illuminazione
                                const ambientLight = new THREE.AmbientLight(0x404040, 1.5);
                                scene.add(ambientLight);

                                const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
                                directionalLight.position.set(1, 1, 1);
                                scene.add(directionalLight);

                                // Controlli della camera
                                const controls = new THREE.OrbitControls(camera, renderer.domElement);
                                controls.enableDamping = true;
                                controls.dampingFactor = 0.05;
                                controls.screenSpacePanning = false;
                                controls.minDistance = 50;
                                controls.maxDistance = 300;

                                // Carica il modello STL
                                const loader = new THREE.STLLoader();
                                const modelData = atob('{file_base64}');
                                const buffer = new Uint8Array(modelData.length);
                                for (let i = 0; i < modelData.length; i++) {{
                                    buffer[i] = modelData.charCodeAt(i);
                                }}

                                try {{
                                    const geometry = loader.parse(buffer.buffer);
                                    const material = new THREE.MeshPhongMaterial({{
                                        color: 0x1E88E5,
                                        specular: 0x111111,
                                        shininess: 200
                                    }});
                                    const mesh = new THREE.Mesh(geometry, material);

                                    // Centra il modello
                                    geometry.computeBoundingBox();
                                    const center = new THREE.Vector3();
                                    geometry.boundingBox.getCenter(center);
                                    mesh.position.sub(center);

                                    // Calcola la dimensione per il posizionamento della camera
                                    const box = new THREE.Box3().setFromObject(mesh);
                                    const size = box.getSize(new THREE.Vector3());
                                    const maxDim = Math.max(size.x, size.y, size.z);

                                    // Scala il modello se necessario
                                    if (maxDim > 200) {{
                                        const scale = 200 / maxDim;
                                        mesh.scale.multiplyScalar(scale);
                                    }}

                                    scene.add(mesh);

                                    // Posiziona la camera
                                    camera.position.set(maxDim * 2, maxDim * 2, maxDim * 2);
                                    camera.lookAt(0, 0, 0);
                                    controls.target.set(0, 0, 0);

                                    // Animazione
                                    function animate() {{
                                        requestAnimationFrame(animate);
                                        controls.update();
                                        renderer.render(scene, camera);
                                    }}
                                    animate();

                                    // Gestione del ridimensionamento
                                    window.addEventListener('resize', () => {{
                                        const newWidth = container.clientWidth;
                                        const newHeight = container.clientHeight;
                                        camera.aspect = newWidth / newHeight;
                                        camera.updateProjectionMatrix();
                                        renderer.setSize(newWidth, newHeight);
                                    }});

                                    console.log('Modello STL caricato con successo');
                                }} catch (error) {{
                                    console.error('Errore nel caricamento del modello:', error);
                                    container.innerHTML = '<div style="color: red; padding: 20px;">Errore nel caricamento del modello 3D: ' + error.message + '</div>';
                                }}
                            </script>
                            """,
                            height=400
                        )

                    except Exception as e:
                        st.error(f"Errore nella visualizzazione del modello 3D: {str(e)}")

                except Exception as e:
                    st.error(f"Errore nel processare il file: {str(e)}")

    elif page == "⚙️ Gestione Materiali":
        materials_manager_page()

if __name__ == "__main__":
    main()