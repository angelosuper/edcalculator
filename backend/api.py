import logging
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

from . import models, schemas, database

# Configura logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="3D Print Cost Calculator API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database tables at startup
@app.on_event("startup")
async def startup_event():
    try:
        logger.info("Initializing database...")
        database.init_db()
        logger.info("Database initialized successfully")

        # Log available routes
        routes = [{"path": route.path, "name": route.name} for route in app.routes]
        logger.info(f"Available routes: {routes}")

    except Exception as e:
        logger.error(f"Error during startup: {str(e)}")
        raise

# Test endpoint
@app.get("/")
def read_root():
    return {"status": "ok", "message": "API is running"}

# Materials endpoints
@app.get("/materials/", response_model=List[schemas.Material])
def read_materials(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    try:
        logger.info("Fetching materials from database")
        materials = db.query(models.Material).offset(skip).limit(limit).all()
        logger.info(f"Found {len(materials)} materials")
        return materials
    except Exception as e:
        logger.error(f"Error fetching materials: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/materials/", response_model=schemas.Material)
def create_material(material: schemas.MaterialCreate, db: Session = Depends(database.get_db)):
    try:
        logger.info(f"Creating new material: {material.dict()}")
        db_material = models.Material(**material.dict())
        db.add(db_material)
        db.commit()
        db.refresh(db_material)
        logger.info(f"Material created successfully: {db_material.id}")
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