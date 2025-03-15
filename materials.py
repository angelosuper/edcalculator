import pandas as pd

# Predefined materials with their properties
MATERIALS_DATA = {
    'PLA': {
        'density': 1.24,  # g/cm³
        'cost_per_kg': 20.0,  # EUR/kg
        'min_layer_height': 0.1,  # mm
        'max_layer_height': 0.3,  # mm
    },
    'PETG': {
        'density': 1.27,
        'cost_per_kg': 25.0,
        'min_layer_height': 0.1,
        'max_layer_height': 0.3,
    },
    'ABS': {
        'density': 1.04,
        'cost_per_kg': 22.0,
        'min_layer_height': 0.1,
        'max_layer_height': 0.3,
    },
    'TPU': {
        'density': 1.21,
        'cost_per_kg': 35.0,
        'min_layer_height': 0.15,
        'max_layer_height': 0.3,
    }
}

def get_materials_df():
    """Convert materials data to DataFrame for display"""
    df = pd.DataFrame.from_dict(MATERIALS_DATA, orient='index')
    df.index.name = 'Material'
    return df

def get_material_properties(material_name):
    """Get properties for a specific material"""
    return MATERIALS_DATA.get(material_name, None)
