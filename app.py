import streamlit as st
import plotly.graph_objects as go
import numpy as np
import requests
import pandas as pd
import json

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

def create_3d_visualization(vertices, visualization_mode='points'):
    """Crea una visualizzazione 3D del modello STL con diverse modalità"""

    if visualization_mode == 'points':
        trace = go.Scatter3d(
            x=vertices[:, 0],
            y=vertices[:, 1],
            z=vertices[:, 2],
            mode='markers',
            marker=dict(
                size=2,                
                color='blue',          
                opacity=0.8,           
                line=dict(
                    width=0.5,         
                    color='darkblue'   
                )
            )
        )
    elif visualization_mode == 'surface':
        trace = go.Mesh3d(
            x=vertices[:, 0],
            y=vertices[:, 1],
            z=vertices[:, 2],
            color='rgb(0, 100, 255)',
            opacity=1.0,
            lighting=dict(
                ambient=0.3,
                diffuse=1.0,
                fresnel=0.8,
                specular=1.0,
                roughness=0.4
            ),
            flatshading=True
        )
    elif visualization_mode == 'wireframe':
        trace = go.Scatter3d(
            x=vertices[:, 0],
            y=vertices[:, 1],
            z=vertices[:, 2],
            mode='lines',
            line=dict(
                color='blue',
                width=1
            )
        )
    else:  # combination
        trace1 = go.Mesh3d(
            x=vertices[:, 0],
            y=vertices[:, 1],
            z=vertices[:, 2],
            color='rgb(0, 100, 255)',
            opacity=0.7,
            lighting=dict(
                ambient=0.3,
                diffuse=1.0,
                fresnel=0.8,
                specular=1.0,
                roughness=0.4
            ),
            flatshading=True
        )
        trace2 = go.Scatter3d(
            x=vertices[:, 0],
            y=vertices[:, 1],
            z=vertices[:, 2],
            mode='lines',
            line=dict(
                color='white',
                width=1
            )
        )
        return go.Figure(data=[trace1, trace2])

    fig = go.Figure(data=[trace])
    fig.update_layout(
        scene=dict(
            aspectmode='manual',  
            aspectratio=dict(
                x=195.84/122.4,  
                y=1,             
                z=200/122.4      
            ),
            camera=dict(
                up=dict(x=0, y=1, z=0),
                center=dict(x=0, y=0, z=0),
                eye=dict(x=1.5, y=1.5, z=1.5)
            ),
            xaxis=dict(
                showgrid=True,
                gridwidth=1,
                gridcolor='lightgray',
                zeroline=True,
                zerolinewidth=2,
                zerolinecolor='gray',
                range=[-97.92, 97.92]  
            ),
            yaxis=dict(
                showgrid=True,
                gridwidth=1,
                gridcolor='lightgray',
                zeroline=True,
                zerolinewidth=2,
                zerolinecolor='gray',
                range=[-61.2, 61.2]    
            ),
            zaxis=dict(
                showgrid=True,
                gridwidth=1,
                gridcolor='lightgray',
                zeroline=True,
                zerolinewidth=2,
                zerolinecolor='gray',
                range=[0, 200]         
            ),
            dragmode='orbit'  
        ),
        margin=dict(l=0, r=0, t=0, b=0),
        showlegend=False,
        updatemenus=[
            dict(
                type='buttons',
                showactive=False,
                buttons=[
                    dict(
                        label='Vista Frontale',
                        method='relayout',
                        args=[{'scene.camera': dict(
                            eye=dict(x=0, y=100, z=0),
                            up=dict(x=0, y=0, z=1),
                            center=dict(x=0, y=0, z=0)
                        )}]
                    ),
                    dict(
                        label='Vista Laterale',
                        method='relayout',
                        args=[{'scene.camera': dict(
                            eye=dict(x=100, y=0, z=0),
                            up=dict(x=0, y=0, z=1),
                            center=dict(x=0, y=0, z=0)
                        )}]
                    ),
                    dict(
                        label='Vista Dall\'alto',
                        method='relayout',
                        args=[{'scene.camera': dict(
                            eye=dict(x=0, y=0, z=100),
                            up=dict(x=0, y=1, z=0),
                            center=dict(x=0, y=0, z=0)
                        )}]
                    ),
                    dict(
                        label='Vista Isometrica',
                        method='relayout',
                        args=[{'scene.camera': dict(
                            eye=dict(x=150, y=150, z=150),
                            up=dict(x=0, y=0, z=1),
                            center=dict(x=0, y=0, z=0)
                        )}]
                    )
                ],
                direction='down',
                pad={'r': 10, 't': 10},
                x=0.1,
                y=1.1,
                xanchor='left',
                yanchor='top'
            )
        ]
    )
    return fig

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
        st.markdown("---")
        st.info("Usa il menu sopra per navigare tra le sezioni dell'applicazione")

    # Contenuto principale
    if page == "🧮 Calcolo Costi":
        st.title("Calcolatore Costi Stampa 3D")
        # Recupera materiali dal backend
        materials_data = get_materials_from_api()

        if not materials_data:
            st.warning("Nessun materiale disponibile. Aggiungi materiali nella sezione 'Gestione Materiali'.")
            return

        # Selezione materiale
        st.subheader("Selezione Materiale")
        materials_df = pd.DataFrame.from_dict(materials_data, orient='index')
        materials_df.index.name = 'Materiale'

        st.dataframe(materials_df.rename(columns={
            'density': 'Densità (g/cm³)',
            'cost_per_kg': 'Costo per kg (€)',
            'min_layer_height': 'Altezza min. layer (mm)',
            'max_layer_height': 'Altezza max. layer (mm)'
        }))

        selected_material = st.selectbox(
            "Seleziona materiale",
            options=list(materials_data.keys())
        )

        material_props = materials_data.get(selected_material)

        if material_props:
            # Selezione altezza layer
            layer_height = st.slider(
                "Altezza layer (mm)",
                min_value=material_props['min_layer_height'],
                max_value=material_props['max_layer_height'],
                value=0.2,
                step=0.05
            )

            # Velocità di stampa
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

                    # Selezione modalità visualizzazione
                    st.subheader("Anteprima Modello")
                    visualization_mode = st.selectbox(
                        "Modalità di visualizzazione",
                        options=['points', 'surface', 'wireframe', 'combination'],
                        format_func=lambda x: {
                            'points': 'Punti',
                            'surface': 'Superficie',
                            'wireframe': 'Reticolo',
                            'combination': 'Combinato'
                        }[x]
                    )

                    # Visualizzazione 3D
                    fig = create_3d_visualization(vertices, visualization_mode)
                    st.plotly_chart(fig, use_container_width=True)

                except Exception as e:
                    st.error(f"Errore nel processare il file: {str(e)}")

    elif page == "⚙️ Gestione Materiali":
        materials_manager_page()

if __name__ == "__main__":
    main()