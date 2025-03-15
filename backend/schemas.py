from pydantic import BaseModel, Field
from typing import Optional

# Material schemas
class MaterialBase(BaseModel):
    name: str
    density: float = Field(..., gt=0, description="Densità in g/cm³")
    cost_per_kg: float = Field(..., gt=0, description="Costo per kg in EUR")
    min_layer_height: float = Field(..., gt=0, description="Altezza minima layer in mm")
    max_layer_height: float = Field(..., gt=0, description="Altezza massima layer in mm")

class MaterialCreate(MaterialBase):
    pass

class Material(MaterialBase):
    id: int

    class Config:
        from_attributes = True

# Printer schemas
class PrinterBase(BaseModel):
    name: str
    hourly_cost: float = Field(..., gt=0, description="Costo orario in EUR")
    power_consumption: float = Field(..., gt=0, description="Consumo energetico in kW")

class PrinterCreate(PrinterBase):
    pass

class Printer(PrinterBase):
    id: int

    class Config:
        from_attributes = True

# Energy cost schemas
class EnergyCostBase(BaseModel):
    cost_per_kwh: float = Field(..., gt=0, description="Costo per kWh in EUR")
    description: str

class EnergyCostCreate(EnergyCostBase):
    pass

class EnergyCost(EnergyCostBase):
    id: int

    class Config:
        from_attributes = True
