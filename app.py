import streamlit as st
import plotly.graph_objects as go
import numpy as np

from materials import get_materials_df, get_material_properties, MATERIALS_DATA
from stl_processor import process_stl, calculate_print_cost

def create_3d_visualization(vertices, visualization_mode='points'):
    """Crea una visualizzazione 3D del modello STL con diverse modalità"""

    if visualization_mode == 'points':
        trace = go.Scatter3d(
            x=vertices[:, 0],
            y=vertices[:, 1],
            z=vertices[:, 2],
            mode='markers',
            marker=dict(
                size=1,
                color='blue',
                opacity=0.8
            )
        )
    elif visualization_mode == 'surface':
        # Creare una mesh di superficie
        trace = go.Mesh3d(
            x=vertices[:, 0],
            y=vertices[:, 1],
            z=vertices[:, 2],
            color='blue',
            opacity=0.8
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
            color='blue',
            opacity=0.5
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
            aspectmode='data'
        ),
        margin=dict(l=0, r=0, t=0, b=0)
    )
    return fig

def main():
    st.title("Calcolatore Costi Stampa 3D")

    # Selezione materiale
    st.subheader("Selezione Materiale")
    materials_df = get_materials_df()
    st.dataframe(materials_df.rename(columns={
        'density': 'Densità (g/cm³)',
        'cost_per_kg': 'Costo per kg (€)',
        'min_layer_height': 'Altezza min. layer (mm)',
        'max_layer_height': 'Altezza max. layer (mm)'
    }))

    selected_material = st.selectbox(
        "Seleziona materiale",
        options=list(MATERIALS_DATA.keys())
    )

    material_props = get_material_properties(selected_material)
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
                volume, vertices = process_stl(file_content)

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

if __name__ == "__main__":
    main()