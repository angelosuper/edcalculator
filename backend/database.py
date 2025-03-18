import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import time

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

# Create engine with enhanced logging and longer timeout
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=True,  # Enable SQL logging
    pool_pre_ping=True,  # Enable connection health checks
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800,
    connect_args={
        'connect_timeout': 30,
        'options': '-c statement_timeout=30000'
    }
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Database dependency"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def wait_for_db(max_retries=10, retry_delay=5):
    """Wait for database to be available"""
    for attempt in range(max_retries):
        try:
            # Try to connect to the database
            with engine.connect() as conn:
                conn.execute("SELECT 1")
                logger.info("Successfully connected to database")
                return True
        except Exception as e:
            if attempt < max_retries - 1:
                logger.warning(f"Database connection attempt {attempt + 1} failed: {str(e)}")
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                logger.error("Max retries reached, could not connect to database")
                raise

def init_db():
    """Initialize database with retry mechanism"""
    try:
        # First wait for database to be available
        wait_for_db()

        from backend.base import Base
        from backend.models import Material

        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")

        # Add default materials if needed
        db = SessionLocal()
        try:
            if db.query(Material).count() == 0:
                logger.info("Adding default materials...")
                default_materials = [
                    Material(
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
                        flow_rate=100,
                        hourly_cost=30.0
                    ),
                    Material(
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
                        flow_rate=100,
                        hourly_cost=30.0
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