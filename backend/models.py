from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class Material(Base):
    __tablename__ = "materials"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    density = Column(Float)  # g/cm³
    cost_per_kg = Column(Float)  # EUR/kg
    min_layer_height = Column(Float)  # mm
    max_layer_height = Column(Float)  # mm

class Printer(Base):
    __tablename__ = "printers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    hourly_cost = Column(Float)  # EUR/hour (include ammortamento)
    power_consumption = Column(Float)  # kW

class EnergyCost(Base):
    __tablename__ = "energy_costs"

    id = Column(Integer, primary_key=True, index=True)
    cost_per_kwh = Column(Float)  # EUR/kWh
    description = Column(String)  # es: "Tariffa diurna", "Tariffa notturna"
