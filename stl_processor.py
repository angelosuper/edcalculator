import numpy as np
from numpy.typing import NDArray
import numpy_stl.utils
from numpy_stl.stl import mesh
import io

def process_stl(file_content: bytes) -> tuple[float, NDArray]:
    """
    Process STL file and return volume and vertices for visualization
    
    Args:
        file_content: Binary content of the STL file
    
    Returns:
        tuple: (volume in cm³, vertices array for plotting)
    """
    try:
        # Load STL file
        stl_mesh = mesh.Mesh.from_file(io.BytesIO(file_content))
        
        # Calculate volume (converts from mm³ to cm³)
        volume = abs(stl_mesh.get_mass_properties()[0]) / 1000
        
        # Get vertices for visualization
        vertices = stl_mesh.vectors.reshape(-1, 3)
        
        return volume, vertices
    except Exception as e:
        raise ValueError(f"Error processing STL file: {str(e)}")

def calculate_print_cost(volume: float, material_properties: dict, layer_height: float) -> dict:
    """
    Calculate printing costs based on volume and material properties
    
    Args:
        volume: Volume in cm³
        material_properties: Dictionary containing material properties
        layer_height: Layer height in mm
    
    Returns:
        dict: Dictionary containing cost calculations
    """
    # Calculate material weight in kg
    weight = volume * material_properties['density'] / 1000
    
    # Calculate material cost
    material_cost = weight * material_properties['cost_per_kg']
    
    # Calculate printing time factor (simplified)
    time_factor = 1 + (0.3 - layer_height) * 2  # Higher time factor for smaller layer heights
    
    # Calculate machine time cost (assumed 30€/hour base rate)
    machine_time_cost = (volume * time_factor * 0.5)  # Simplified calculation
    
    return {
        'volume_cm3': round(volume, 2),
        'weight_kg': round(weight, 3),
        'material_cost': round(material_cost, 2),
        'machine_cost': round(machine_time_cost, 2),
        'total_cost': round(material_cost + machine_time_cost, 2)
    }
