"""Pydantic schemas for gear design endpoints."""

from pydantic import BaseModel, Field
from typing import Optional, Literal


class SpurGearInput(BaseModel):
    power_kw: float = Field(..., gt=0, description="Power transmitted in kilowatts", example=10.0)
    speed_rpm: float = Field(..., gt=0, description="Pinion speed in RPM", example=1450.0)
    gear_ratio: float = Field(..., ge=1.0, le=10.0, description="Speed ratio (output/input) >= 1", example=3.0)
    pinion_material: str = Field("c45_hardened", description="Pinion material key", example="c45_hardened")
    gear_material: str = Field("c45_normalised", description="Gear material key", example="c45_normalised")
    safety_factor_bending: float = Field(1.5, ge=1.0, le=5.0, description="Safety factor for bending stress (min 1.5 AGMA)", example=1.5)
    safety_factor_contact: float = Field(1.2, ge=1.0, le=5.0, description="Safety factor for contact stress (min 1.2 AGMA)", example=1.2)
    load_type: Literal["uniform", "light_shock", "moderate_shock", "heavy_shock"] = Field("uniform", description="Nature of applied load")
    pressure_angle_deg: Literal[14.5, 20.0, 25.0] = Field(20.0, description="Pressure angle in degrees")
    min_teeth_pinion: int = Field(18, ge=12, le=30, description="Minimum number of teeth on pinion")

    model_config = {"json_schema_extra": {"example": {
        "power_kw": 10.0,
        "speed_rpm": 1450,
        "gear_ratio": 3.0,
        "pinion_material": "c45_hardened",
        "gear_material": "c45_normalised",
        "safety_factor_bending": 1.5,
        "safety_factor_contact": 1.2,
        "load_type": "uniform",
        "pressure_angle_deg": 20.0,
        "min_teeth_pinion": 18,
    }}}


class HelicalGearInput(BaseModel):
    power_kw: float = Field(..., gt=0, example=15.0)
    speed_rpm: float = Field(..., gt=0, example=1450.0)
    gear_ratio: float = Field(..., ge=1.0, le=10.0, example=4.0)
    helix_angle_deg: float = Field(20.0, ge=10.0, le=45.0, description="Helix angle in degrees (10–45°)")
    pinion_material: str = Field("c45_hardened", example="c45_hardened")
    gear_material: str = Field("c45_normalised", example="c45_normalised")
    safety_factor_bending: float = Field(1.5, ge=1.0, le=5.0)
    safety_factor_contact: float = Field(1.2, ge=1.0, le=5.0)
    load_type: Literal["uniform", "light_shock", "moderate_shock", "heavy_shock"] = "uniform"
    min_teeth_pinion: int = Field(18, ge=12, le=30)

    model_config = {"json_schema_extra": {"example": {
        "power_kw": 15.0,
        "speed_rpm": 1450,
        "gear_ratio": 4.0,
        "helix_angle_deg": 20.0,
        "pinion_material": "c45_hardened",
        "gear_material": "c45_normalised",
        "safety_factor_bending": 1.5,
        "safety_factor_contact": 1.2,
    }}}
