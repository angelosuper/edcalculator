from pydantic import BaseModel, Field
from typing import Optional

# Material schemas
class MaterialBase(BaseModel):
    name: str
    density: float = Field(..., gt=0, description="Densità in g/cm³")
    cost_per_kg: float = Field(..., gt=0, description="Costo per kg in EUR")
    min_layer_height: float = Field(..., gt=0, description="Altezza minima layer in mm")
    max_layer_height: float = Field(..., gt=0, description="Altezza massima layer in mm")
    hourly_cost: float = Field(30.0, gt=0, description="Costo orario della macchina in EUR/h")

    # Parametri di stampa con valori di default e validazione
    default_temperature: float = Field(200.0, ge=150.0, le=300.0, description="Temperatura di stampa in °C")
    default_bed_temperature: float = Field(60.0, ge=0.0, le=120.0, description="Temperatura del piano in °C")
    retraction_enabled: bool = Field(True, description="Abilitazione retrazione")
    retraction_distance: float = Field(6.0, ge=0.0, le=10.0, description="Distanza di retrazione in mm")
    retraction_speed: float = Field(25.0, ge=10.0, le=100.0, description="Velocità di retrazione in mm/s")
    print_speed: float = Field(60.0, ge=10.0, le=200.0, description="Velocità di stampa in mm/s")
    first_layer_speed: float = Field(30.0, ge=5.0, le=100.0, description="Velocità primo layer in mm/s")
    fan_speed: int = Field(100, ge=0, le=100, description="Velocità ventola in %")
    flow_rate: int = Field(100, ge=50, le=200, description="Flusso di estrusione in %")

class MaterialCreate(MaterialBase):
    pass

class MaterialUpdate(BaseModel):
    name: Optional[str] = None
    density: Optional[float] = Field(None, gt=0)
    cost_per_kg: Optional[float] = Field(None, gt=0)
    min_layer_height: Optional[float] = Field(None, gt=0)
    max_layer_height: Optional[float] = Field(None, gt=0)
    hourly_cost: Optional[float] = Field(None, gt=0)
    default_temperature: Optional[float] = Field(None, ge=150.0, le=300.0)
    default_bed_temperature: Optional[float] = Field(None, ge=0.0, le=120.0)
    retraction_enabled: Optional[bool] = None
    retraction_distance: Optional[float] = Field(None, ge=0.0, le=10.0)
    retraction_speed: Optional[float] = Field(None, ge=10.0, le=100.0)
    print_speed: Optional[float] = Field(None, ge=10.0, le=200.0)
    first_layer_speed: Optional[float] = Field(None, ge=5.0, le=100.0)
    fan_speed: Optional[int] = Field(None, ge=0, le=100)
    flow_rate: Optional[int] = Field(None, ge=50, le=200)

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