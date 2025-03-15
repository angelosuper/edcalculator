import numpy as np
from numpy.typing import NDArray
from stl import mesh  # Modifica dell'import per numpy-stl
import io
import tempfile
import os

def process_stl(file_content: bytes) -> tuple[float, NDArray, dict]:
    """
    Process STL file and return volume, vertices and dimensions for visualization

    Args:
        file_content: Binary content of the STL file

    Returns:
        tuple: (volume in cm³, vertices array for plotting, dimensions in mm)
    """
    try:
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.stl') as tmp_file:
            # Write the binary content to the temporary file
            tmp_file.write(file_content)
            tmp_file.flush()
            tmp_file_path = tmp_file.name

        try:
            # Load STL file from the temporary path
            stl_mesh = mesh.Mesh.from_file(tmp_file_path)

            # Calculate volume (converts from mm³ to cm³)
            volume = abs(stl_mesh.get_mass_properties()[0]) / 1000

            # Get vertices for visualization
            vertices = stl_mesh.vectors.reshape(-1, 3)

            # Calculate dimensions in mm
            dimensions = {
                'width': round(np.max(vertices[:, 0]) - np.min(vertices[:, 0]), 2),
                'depth': round(np.max(vertices[:, 1]) - np.min(vertices[:, 1]), 2),
                'height': round(np.max(vertices[:, 2]) - np.min(vertices[:, 2]), 2)
            }

            return volume, vertices, dimensions
        finally:
            # Clean up the temporary file
            if os.path.exists(tmp_file_path):
                os.unlink(tmp_file_path)

    except Exception as e:
        raise ValueError(f"Errore nel processare il file STL: {str(e)}")

def estimate_print_time(volume: float, layer_height: float, velocita_stampa: float = 60) -> float:
    """
    Stima il tempo di stampa in ore

    Args:
        volume: Volume in cm³
        layer_height: Altezza layer in mm
        velocita_stampa: Velocità media di stampa in mm/s

    Returns:
        float: Tempo stimato in ore
    """
    # Stima la lunghezza del filamento (approssimativa)
    diametro_filamento = 1.75  # mm
    area_filamento = np.pi * (diametro_filamento/2)**2
    lunghezza_filamento = (volume * 1000) / area_filamento  # mm

    # Calcola il numero approssimativo di layer
    altezza_media = np.cbrt(volume * 1000)  # mm
    numero_layer = altezza_media / layer_height

    # Tempo totale considerando movimenti non di stampa
    tempo_stampa = lunghezza_filamento / velocita_stampa  # secondi
    tempo_movimento = numero_layer * 2  # 2 secondi per layer per movimenti

    return (tempo_stampa + tempo_movimento) / 3600  # converti in ore

def calculate_print_cost(volume: float, material_properties: dict, layer_height: float, velocita_stampa: float = 60) -> dict:
    """
    Calcola i costi di stampa basati su volume e proprietà del materiale

    Args:
        volume: Volume in cm³
        material_properties: Dictionary con le proprietà del materiale
        layer_height: Altezza layer in mm
        velocita_stampa: Velocità media di stampa in mm/s

    Returns:
        dict: Dizionario con i calcoli dei costi
    """
    # Calcola peso in kg
    weight = volume * material_properties['density'] / 1000

    # Calcola costo materiale
    material_cost = weight * material_properties['cost_per_kg']

    # Stima tempo di stampa
    print_time = estimate_print_time(volume, layer_height, velocita_stampa)

    # Usa il costo orario specifico del materiale
    hourly_cost = material_properties.get('hourly_cost', 30)  # EUR/ora
    machine_cost = print_time * hourly_cost

    return {
        'volume_cm3': round(volume, 2),
        'weight_kg': round(weight, 3),
        'material_cost': round(material_cost, 2),
        'tempo_stampa': round(print_time, 2),
        'machine_cost': round(machine_cost, 2),
        'total_cost': round(material_cost + machine_cost, 2)
    }