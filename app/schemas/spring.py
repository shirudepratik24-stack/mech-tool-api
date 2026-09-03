"""Pydantic schemas for spring design endpoints."""

from pydantic import BaseModel, Field
from typing import Literal


class CompressionSpringInput(BaseModel):
    load_N: float = Field(..., gt=0, description="Applied load in Newtons", example=500.0)
    deflection_mm: float = Field(..., gt=0, description="Required deflection in mm", example=25.0)
    spring_index: float = Field(6.0, ge=4.0, le=12.0, description="Spring index C = D/d (4–12)", example=6.0)
    material: str = Field("hard_drawn_wire", description="Spring wire material key", example="hard_drawn_wire")
    safety_factor: float = Field(1.5, ge=1.0, le=4.0, description="Safety factor on shear stress")
    end_type: Literal["plain", "plain_ground", "closed", "closed_ground"] = Field(
        "closed_ground", description="End type of spring"
    )
    clash_allowance: float = Field(0.15, ge=0.05, le=0.30, description="Clash allowance as fraction of free length")

    model_config = {"json_schema_extra": {"example": {
        "load_N": 500.0,
        "deflection_mm": 25.0,
        "spring_index": 6.0,
        "material": "hard_drawn_wire",
        "safety_factor": 1.5,
        "end_type": "closed_ground",
        "clash_allowance": 0.15,
    }}}


class TensionSpringInput(BaseModel):
    load_N: float = Field(..., gt=0, description="Applied load in Newtons", example=200.0)
    deflection_mm: float = Field(..., gt=0, description="Required deflection in mm", example=15.0)
    spring_index: float = Field(6.0, ge=4.0, le=12.0, description="Spring index C = D/d")
    material: str = Field("music_wire", description="Spring wire material key")
    safety_factor: float = Field(1.5, ge=1.0, le=4.0)
    hook_type: Literal["standard_hook", "extended_hook", "half_loop"] = "standard_hook"

    model_config = {"json_schema_extra": {"example": {
        "load_N": 200.0,
        "deflection_mm": 15.0,
        "spring_index": 6.0,
        "material": "music_wire",
        "safety_factor": 1.5,
        "hook_type": "standard_hook",
    }}}
