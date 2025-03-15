import numpy as np
from typing import Dict, Any
import hashlib
import logging
from . import models
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

def calculate_model_hash(stl_content: bytes) -> str:
    """Calcola l'hash del modello STL per l'identificazione"""
    return hashlib.sha256(stl_content).hexdigest()

def analyze_model_characteristics(
    stl_content: bytes,
    volume: float,
    vertices: np.ndarray
) -> models.ModelCharacteristics:
    """Analizza le caratteristiche del modello STL"""
    try:
        # Calcola l'hash del file
        file_hash = calculate_model_hash(stl_content)
        
        # Calcola l'area superficiale (approssimata)
        surface_area = calculate_surface_area(vertices)
        
        # Analizza gli angoli di sporgenza
        max_overhang = calculate_max_overhang(vertices)
        
        # Calcola lo score di complessità
        complexity = calculate_complexity_score(vertices, volume, surface_area)
        
        # Determina se sono necessari supporti
        needs_supports = max_overhang > 45.0

        return models.ModelCharacteristics(
            file_hash=file_hash,
            volume=volume,
            surface_area=surface_area,
            max_overhang_angle=max_overhang,
            has_supports=needs_supports,
            complexity_score=complexity,
            recommended_settings={}  # Sarà popolato in seguito
        )
    except Exception as e:
        logger.error(f"Errore nell'analisi del modello: {str(e)}")
        raise

def calculate_surface_area(vertices: np.ndarray) -> float:
    """Calcola l'area superficiale approssimata del modello"""
    try:
        # Implementazione semplificata per il calcolo dell'area superficiale
        # TODO: Implementare un calcolo più preciso
        return float(len(vertices) * 0.1)
    except Exception as e:
        logger.error(f"Errore nel calcolo dell'area superficiale: {str(e)}")
        return 0.0

def calculate_max_overhang(vertices: np.ndarray) -> float:
    """Calcola l'angolo massimo di sporgenza"""
    try:
        # Implementazione semplificata per il calcolo dell'angolo di sporgenza
        # TODO: Implementare un calcolo più preciso
        return 45.0
    except Exception as e:
        logger.error(f"Errore nel calcolo dell'angolo di sporgenza: {str(e)}")
        return 0.0

def calculate_complexity_score(
    vertices: np.ndarray,
    volume: float,
    surface_area: float
) -> float:
    """Calcola uno score di complessità del modello"""
    try:
        # Più alto è il rapporto superficie/volume, più complesso è il modello
        complexity = (surface_area / volume) * 100 if volume > 0 else 100
        return min(max(complexity, 0), 100)  # Normalizza tra 0 e 100
    except Exception as e:
        logger.error(f"Errore nel calcolo dello score di complessità: {str(e)}")
        return 50.0

def generate_print_recommendations(
    db: Session,
    model_characteristics: models.ModelCharacteristics,
    material_id: int
) -> Dict[str, Any]:
    """Genera raccomandazioni di stampa basate sulle caratteristiche del modello"""
    try:
        # Recupera il materiale
        material = db.query(models.Material).filter(models.Material.id == material_id).first()
        if not material:
            raise ValueError(f"Materiale con ID {material_id} non trovato")

        # Recupera le raccomandazioni precedenti per modelli simili
        similar_recommendations = db.query(models.PrintRecommendation).filter(
            models.PrintRecommendation.material_id == material_id,
            models.PrintRecommendation.success_rating >= 4.0
        ).all()

        # Calcola le impostazioni raccomandate
        layer_height = calculate_optimal_layer_height(
            model_characteristics,
            material,
            similar_recommendations
        )
        
        print_speed = calculate_optimal_print_speed(
            model_characteristics,
            material,
            similar_recommendations
        )

        # Crea le raccomandazioni
        recommendations = {
            "layer_height": layer_height,
            "print_speed": print_speed,
            "temperature": material.default_temperature,
            "bed_temperature": material.default_bed_temperature,
            "fan_speed": calculate_optimal_fan_speed(model_characteristics),
            "supports_required": model_characteristics.has_supports,
            "estimated_quality_score": estimate_print_quality(
                model_characteristics,
                layer_height,
                print_speed
            )
        }

        return recommendations

    except Exception as e:
        logger.error(f"Errore nella generazione delle raccomandazioni: {str(e)}")
        raise

def calculate_optimal_layer_height(
    model: models.ModelCharacteristics,
    material: models.Material,
    similar_recommendations: list
) -> float:
    """Calcola l'altezza layer ottimale"""
    if model.complexity_score > 80:
        # Per modelli complessi, usa layer più sottili
        return material.min_layer_height
    elif model.complexity_score < 30:
        # Per modelli semplici, usa layer più spessi
        return material.max_layer_height
    else:
        # Per modelli di media complessità, usa un valore intermedio
        return (material.min_layer_height + material.max_layer_height) / 2

def calculate_optimal_print_speed(
    model: models.ModelCharacteristics,
    material: models.Material,
    similar_recommendations: list
) -> float:
    """Calcola la velocità di stampa ottimale"""
    base_speed = material.print_speed
    
    # Riduci la velocità per modelli complessi
    if model.complexity_score > 70:
        return base_speed * 0.7
    elif model.complexity_score < 30:
        return base_speed * 1.2
    else:
        return base_speed

def calculate_optimal_fan_speed(model: models.ModelCharacteristics) -> int:
    """Calcola la velocità ottimale della ventola"""
    if model.max_overhang_angle > 40:
        return 100  # Massimo raffreddamento per sporgenze significative
    elif model.complexity_score > 70:
        return 80  # Raffreddamento elevato per dettagli complessi
    else:
        return 60  # Raffreddamento moderato per modelli semplici

def estimate_print_quality(
    model: models.ModelCharacteristics,
    layer_height: float,
    print_speed: float
) -> float:
    """Stima la qualità di stampa attesa (0-100)"""
    quality_score = 100.0
    
    # Penalità per layer height elevata
    quality_score -= (layer_height * 100) # Più alto il layer, minore la qualità
    
    # Penalità per velocità elevata
    quality_score -= (print_speed / 2)  # Velocità maggiore può ridurre la qualità
    
    # Penalità per complessità
    quality_score -= (model.complexity_score * 0.2)
    
    return max(min(quality_score, 100), 0)  # Normalizza tra 0 e 100
