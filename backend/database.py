import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Configura logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

# Ensure database URL is properly formatted for PostgreSQL
if SQLALCHEMY_DATABASE_URL and SQLALCHEMY_DATABASE_URL.startswith("postgres://"):
    SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("postgres://", "postgresql://", 1)

logger.info(f"Connecting to database...")

# Add SSL mode=require and other connection parameters
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={
        "sslmode": "require"
    },
    echo=True  # Enable SQL logging
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database and create tables"""
    try:
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")

        # Add default materials if they don't exist
        from . import models
        db = SessionLocal()
        try:
            # Check if we have any materials
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
                    ),
                    models.Material(
                        name="ABS",
                        density=1.04,
                        cost_per_kg=22.0,
                        min_layer_height=0.1,
                        max_layer_height=0.3,
                        default_temperature=230.0,
                        default_bed_temperature=100.0,
                        retraction_enabled=True,
                        retraction_distance=5.0,
                        retraction_speed=35.0,
                        print_speed=55.0,
                        first_layer_speed=25.0,
                        fan_speed=0,
                        flow_rate=100
                    ),
                    models.Material(
                        name="TPU",
                        density=1.21,
                        cost_per_kg=35.0,
                        min_layer_height=0.15,
                        max_layer_height=0.3,
                        default_temperature=220.0,
                        default_bed_temperature=60.0,
                        retraction_enabled=False,
                        retraction_distance=4.0,
                        retraction_speed=20.0,
                        print_speed=25.0,
                        first_layer_speed=15.0,
                        fan_speed=50,
                        flow_rate=110
                    )
                ]
                db.bulk_save_objects(default_materials)
                db.commit()
                logger.info("Default materials added successfully")
        except Exception as e:
            logger.error(f"Error adding default materials: {str(e)}")
            db.rollback()
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Error creating database tables: {str(e)}")
        raise