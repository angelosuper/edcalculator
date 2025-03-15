from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from .base import Base

class Material(Base):
    __tablename__ = "materials"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    density = Column(Float)  # g/cm³
    cost_per_kg = Column(Float)  # EUR/kg
    min_layer_height = Column(Float)  # mm
    max_layer_height = Column(Float)  # mm

    # Parametri di stampa
    default_temperature = Column(Float, default=200.0)  # °C
    default_bed_temperature = Column(Float, default=60.0)  # °C
    retraction_enabled = Column(Boolean, default=True)
    retraction_distance = Column(Float, default=6.0)  # mm
    retraction_speed = Column(Float, default=25.0)  # mm/s
    print_speed = Column(Float, default=60.0)  # mm/s
    first_layer_speed = Column(Float, default=30.0)  # mm/s
    fan_speed = Column(Integer, default=100)  # %
    flow_rate = Column(Integer, default=100)  # %

    # Relazione con le raccomandazioni
    recommendations = relationship("PrintRecommendation", back_populates="material")

class ModelCharacteristics(Base):
    __tablename__ = "model_characteristics"

    id = Column(Integer, primary_key=True, index=True)
    file_hash = Column(String, unique=True, index=True)  # Hash del file STL per identificazione
    volume = Column(Float)  # cm³
    surface_area = Column(Float)  # cm²
    max_overhang_angle = Column(Float)  # gradi
    has_supports = Column(Boolean, default=False)
    complexity_score = Column(Float)  # 0-100
    recommended_settings = Column(JSON)  # Impostazioni raccomandate basate sull'analisi

class PrintRecommendation(Base):
    __tablename__ = "print_recommendations"

    id = Column(Integer, primary_key=True, index=True)
    material_id = Column(Integer, ForeignKey("materials.id"))
    model_hash = Column(String, index=True)  # Hash del modello STL
    layer_height = Column(Float)
    print_speed = Column(Float)
    temperature = Column(Float)
    bed_temperature = Column(Float)
    fan_speed = Column(Integer)
    success_rating = Column(Float)  # Valutazione del successo della stampa (0-5)
    feedback = Column(String)  # Feedback dell'utente

    # Relazioni
    material = relationship("Material", back_populates="recommendations")

class Printer(Base):
    __tablename__ = "printers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    hourly_cost = Column(Float)  # EUR/hour
    power_consumption = Column(Float)  # kW

class EnergyCost(Base):
    __tablename__ = "energy_costs"

    id = Column(Integer, primary_key=True, index=True)
    cost_per_kwh = Column(Float)  # EUR/kWh
    description = Column(String)  # es: "Tariffa diurna", "Tariffa notturna"