import logging
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from . import models, schemas, database

# Configura logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="3D Print Cost Calculator API")

# Initialize database tables at startup
@app.on_event("startup")
async def startup_event():
    database.init_db()

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

        # Log dei dati ricevuti per debug
        logger.info(f"Updating material {material_id} with data: {material.dict(exclude_unset=True)}")

        for field, value in material.dict(exclude_unset=True).items():
            logger.info(f"Setting {field} = {value}")
            setattr(db_material, field, value)

        try:
            db.commit()
            db.refresh(db_material)
            logger.info(f"Material {material_id} updated successfully")
            return db_material
        except Exception as e:
            logger.error(f"Database error while updating material: {str(e)}")
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    except Exception as e:
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