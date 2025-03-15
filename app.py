import streamlit as st
import plotly.graph_objects as go
import numpy as np

from materials import get_materials_df, get_material_properties, MATERIALS_DATA
from stl_processor import process_stl, calculate_print_cost

def create_3d_visualization(vertices):
    """Create a 3D visualization of the STL model"""
    fig = go.Figure(data=[
        go.Scatter3d(
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
    ])
    
    fig.update_layout(
        scene=dict(
            aspectmode='data'
        ),
        margin=dict(l=0, r=0, t=0, b=0)
    )
    
    return fig

def main():
    st.title("3D Print Cost Calculator")
    
    # Material selection
    st.subheader("Material Selection")
    materials_df = get_materials_df()
    st.dataframe(materials_df)
    
    selected_material = st.selectbox(
        "Select material",
        options=list(MATERIALS_DATA.keys())
    )
    
    material_props = get_material_properties(selected_material)
    
    # Layer height selection
    layer_height = st.slider(
        "Layer height (mm)",
        min_value=material_props['min_layer_height'],
        max_value=material_props['max_layer_height'],
        value=0.2,
        step=0.05
    )
    
    # File upload
    st.subheader("Upload STL File")
    uploaded_file = st.file_uploader("Choose an STL file", type=['stl'])
    
    if uploaded_file is not None:
        try:
            # Process STL file
            file_content = uploaded_file.read()
            volume, vertices = process_stl(file_content)
            
            # Calculate costs
            calculations = calculate_print_cost(volume, material_props, layer_height)
            
            # Display results
            st.subheader("Results")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Volume", f"{calculations['volume_cm3']} cm³")
            with col2:
                st.metric("Weight", f"{calculations['weight_kg']} kg")
            with col3:
                st.metric("Total Cost", f"€{calculations['total_cost']}")
            
            # Detailed breakdown
            st.subheader("Cost Breakdown")
            st.write(f"Material Cost: €{calculations['material_cost']}")
            st.write(f"Machine Cost: €{calculations['machine_cost']}")
            
            # 3D Visualization
            st.subheader("Model Preview")
            fig = create_3d_visualization(vertices)
            st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")

if __name__ == "__main__":
    main()
