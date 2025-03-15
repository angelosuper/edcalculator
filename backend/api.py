import logging
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import numpy as np

from . import models, schemas, database
from .recommendation_engine import (
    analyze_model_characteristics,
    generate_print_recommendations
)
from stl_processor import process_stl  # Importa la funzione esistente

# Configura logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="3D Print Cost Calculator API")

# Initialize database tables at startup
@app.on_event("startup")
async def startup_event():
    database.init_db()

# Endpoint per analizzare un modello e ottenere raccomandazioni
@app.post("/analyze-model/", response_model=schemas.ModelCharacteristics)
async def analyze_model(
    file: UploadFile = File(...),
    material_id: int = None,
    db: Session = Depends(database.get_db)
):
    try:
        # Leggi il contenuto del file
        file_content = await file.read()

        # Processa il file STL
        volume, vertices, dimensions = process_stl(file_content)

        # Analizza le caratteristiche del modello
        characteristics = analyze_model_characteristics(
            file_content,
            volume,
            vertices
        )

        # Se è specificato un materiale, genera raccomandazioni
        if material_id:
            recommendations = generate_print_recommendations(
                db,
                characteristics,
                material_id
            )
            characteristics.recommended_settings = recommendations

        # Salva le caratteristiche nel database
        db_characteristics = models.ModelCharacteristics(**characteristics.dict())
        db.add(db_characteristics)
        db.commit()
        db.refresh(db_characteristics)

        return db_characteristics
    except Exception as e:
        logger.error(f"Errore nell'analisi del modello: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint per salvare il feedback sulla stampa
@app.post("/print-feedback/", response_model=schemas.PrintRecommendation)
def save_print_feedback(
    feedback: schemas.PrintRecommendationCreate,
    db: Session = Depends(database.get_db)
):
    try:
        db_feedback = models.PrintRecommendation(**feedback.dict())
        db.add(db_feedback)
        db.commit()
        db.refresh(db_feedback)
        return db_feedback
    except Exception as e:
        logger.error(f"Errore nel salvare il feedback: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Materials endpoints
@app.get("/materials/", response_model=List[schemas.Material])
def read_materials(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    try:
        materials = db.query(models.Material).offset(skip).limit(limit).all()
        return materials
    except Exception as e:
        logger.error(f"Error fetching materials: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/materials/", response_model=schemas.Material)
def create_material(material: schemas.MaterialCreate, db: Session = Depends(database.get_db)):
    try:
        db_material = models.Material(**material.dict())
        db.add(db_material)
        db.commit()
        db.refresh(db_material)
        return db_material
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating material: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.patch("/materials/{material_id}", response_model=schemas.Material)
def update_material(material_id: int, material: schemas.MaterialUpdate, db: Session = Depends(database.get_db)):
    try:
        db_material = db.query(models.Material).filter(models.Material.id == material_id).first()
        if not db_material:
            raise HTTPException(status_code=404, detail="Material not found")

        for field, value in material.dict(exclude_unset=True).items():
            setattr(db_material, field, value)

        db.commit()
        db.refresh(db_material)
        return db_material
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating material: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/materials/{material_id}")
def delete_material(material_id: int, db: Session = Depends(database.get_db)):
    try:
        db_material = db.query(models.Material).filter(models.Material.id == material_id).first()
        if not db_material:
            raise HTTPException(status_code=404, detail="Material not found")

        db.delete(db_material)
        db.commit()
        return {"message": "Material deleted successfully"}
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting material: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Printers endpoints
@app.post("/printers/", response_model=schemas.Printer)
def create_printer(printer: schemas.PrinterCreate, db: Session = Depends(database.get_db)):
    logger.info(f"Creating new printer: {printer.name}")
    db_printer = models.Printer(**printer.dict())
    db.add(db_printer)
    try:
        db.commit()
        db.refresh(db_printer)
        logger.info(f"Printer {printer.name} created successfully")
        return db_printer
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating printer: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/printers/", response_model=List[schemas.Printer])
def read_printers(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    printers = db.query(models.Printer).offset(skip).limit(limit).all()
    return printers

# Energy costs endpoints
@app.post("/energy-costs/", response_model=schemas.EnergyCost)
def create_energy_cost(energy_cost: schemas.EnergyCostCreate, db: Session = Depends(database.get_db)):
    logger.info("Creating new energy cost entry")
    db_energy_cost = models.EnergyCost(**energy_cost.dict())
    db.add(db_energy_cost)
    try:
        db.commit()
        db.refresh(db_energy_cost)
        logger.info("Energy cost entry created successfully")
        return db_energy_cost
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating energy cost: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/energy-costs/", response_model=List[schemas.EnergyCost])
def read_energy_costs(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    energy_costs = db.query(models.EnergyCost).offset(skip).limit(limit).all()
    return energy_costs