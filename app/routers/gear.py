"""Gear design API routes."""

from fastapi import APIRouter, HTTPException
from app.schemas.gear import SpurGearInput, HelicalGearInput
from app.calculators.gear import design_spur_gear, design_helical_gear
from app.materials import GEAR_MATERIALS

router = APIRouter(prefix="/api/v1/gear", tags=["Gear Design (AGMA)"])


@router.get("/materials", summary="List supported gear materials")
def list_gear_materials():
    """Returns all supported gear materials with their properties."""
    return {
        "count": len(GEAR_MATERIALS),
        "materials": {
            key: {
                "name": v["name"],
                "description": v["description"],
                "Sut_MPa": v["Sut"],
                "Sy_MPa": v["Sy"],
                "BHN": v["BHN"],
                "Sat_MPa": v["Sat"],
                "Sac_MPa": v["Sac"],
            }
            for key, v in GEAR_MATERIALS.items()
        },
    }


@router.post("/spur", summary="Design a spur gear pair (AGMA 2001-D04)")
def design_spur(data: SpurGearInput):
    """
    Designs a spur gear pair using AGMA 2001-D04 bending and contact stress criteria.

    **Outputs include:**
    - Module, face width, number of teeth
    - Pitch diameters, centre distance, outside diameters
    - Lewis bending stress & AGMA contact stress
    - Safety factors for both failure modes
    - Overload, dynamic, size and load-distribution factors
    """
    try:
        result = design_spur_gear(
            power_kw=data.power_kw,
            speed_rpm=data.speed_rpm,
            gear_ratio=data.gear_ratio,
            pinion_material=data.pinion_material,
            gear_material=data.gear_material,
            safety_factor_bending=data.safety_factor_bending,
            safety_factor_contact=data.safety_factor_contact,
            load_type=data.load_type,
            pressure_angle_deg=data.pressure_angle_deg,
            min_teeth_pinion=data.min_teeth_pinion,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Calculation error: {e}")


@router.post("/helical", summary="Design a helical gear pair (AGMA 2001-D04)")
def design_helical(data: HelicalGearInput):
    """
    Designs a helical gear pair using AGMA 2001-D04.
    Uses virtual (formative) tooth count for Lewis form factor.

    **Outputs include:**
    - Normal and transverse module, face width
    - Lead, virtual teeth, pitch diameters
    - Bending and contact stress analysis
    """
    try:
        result = design_helical_gear(
            power_kw=data.power_kw,
            speed_rpm=data.speed_rpm,
            gear_ratio=data.gear_ratio,
            helix_angle_deg=data.helix_angle_deg,
            pinion_material=data.pinion_material,
            gear_material=data.gear_material,
            safety_factor_bending=data.safety_factor_bending,
            safety_factor_contact=data.safety_factor_contact,
            load_type=data.load_type,
            min_teeth_pinion=data.min_teeth_pinion,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Calculation error: {e}")
