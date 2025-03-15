import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Configura logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Get database URL from environment
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")
if not SQLALCHEMY_DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

# Fix per la compatibilità con SQLAlchemy
if SQLALCHEMY_DATABASE_URL.startswith("postgres://"):
    SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Create engine with enhanced logging
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=True,  # Enable SQL logging
    pool_pre_ping=True  # Enable connection health checks
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Database dependency"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database"""
    from .base import Base
    from . import models

    try:
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")

        # Add default materials if needed
        db = SessionLocal()
        try:
            if db.query(models.Material).count() == 0:
                logger.info("Adding default materials...")
                default_materials = [
                    models.Material(
                        name="PLA",
                        density=1.24,
                        cost_per_kg=20.0,
                        min_layer_height=0.1,
                        max_layer_height=0.3,
                        default_temperature=200.0,
                        default_bed_temperature=60.0,
                        retraction_enabled=True,
                        retraction_distance=6.0,
                        retraction_speed=25.0,
                        print_speed=60.0,
                        first_layer_speed=30.0,
                        fan_speed=100,
                        flow_rate=100
                    ),
                    models.Material(
                        name="PETG",
                        density=1.27,
                        cost_per_kg=25.0,
                        min_layer_height=0.1,
                        max_layer_height=0.3,
                        default_temperature=240.0,
                        default_bed_temperature=80.0,
                        retraction_enabled=True,
                        retraction_distance=7.0,
                        retraction_speed=30.0,
                        print_speed=50.0,
                        first_layer_speed=25.0,
                        fan_speed=50,
                        flow_rate=100
                    )
                ]
                for material in default_materials:
                    db.add(material)
                db.commit()
                logger.info("Default materials added successfully")
        except Exception as e:
            logger.error(f"Error adding default materials: {str(e)}")
            db.rollback()
            raise
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise