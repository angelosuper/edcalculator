from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from . import models, schemas, database

app = FastAPI(title="3D Print Cost Calculator API")

# Ensure tables are created
models.Base.metadata.create_all(bind=database.engine)

# Materials endpoints
@app.post("/materials/", response_model=schemas.Material)
def create_material(material: schemas.MaterialCreate, db: Session = Depends(database.get_db)):
    db_material = models.Material(**material.dict())
    db.add(db_material)
    db.commit()
    db.refresh(db_material)
    return db_material

@app.get("/materials/", response_model=List[schemas.Material])
def read_materials(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    materials = db.query(models.Material).offset(skip).limit(limit).all()
    return materials

@app.get("/materials/{material_id}", response_model=schemas.Material)
def read_material(material_id: int, db: Session = Depends(database.get_db)):
    material = db.query(models.Material).filter(models.Material.id == material_id).first()
    if material is None:
        raise HTTPException(status_code=404, detail="Materiale non trovato")
    return material

# Printers endpoints
@app.post("/printers/", response_model=schemas.Printer)
def create_printer(printer: schemas.PrinterCreate, db: Session = Depends(database.get_db)):
    db_printer = models.Printer(**printer.dict())
    db.add(db_printer)
    db.commit()
    db.refresh(db_printer)
    return db_printer

@app.get("/printers/", response_model=List[schemas.Printer])
def read_printers(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    printers = db.query(models.Printer).offset(skip).limit(limit).all()
    return printers

# Energy costs endpoints
@app.post("/energy-costs/", response_model=schemas.EnergyCost)
def create_energy_cost(energy_cost: schemas.EnergyCostCreate, db: Session = Depends(database.get_db)):
    db_energy_cost = models.EnergyCost(**energy_cost.dict())
    db.add(db_energy_cost)
    db.commit()
    db.refresh(db_energy_cost)
    return db_energy_cost

@app.get("/energy-costs/", response_model=List[schemas.EnergyCost])
def read_energy_costs(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    energy_costs = db.query(models.EnergyCost).offset(skip).limit(limit).all()
    return energy_costs