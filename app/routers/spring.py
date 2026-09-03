"""Spring design API routes."""

from fastapi import APIRouter, HTTPException
from app.schemas.spring import CompressionSpringInput, TensionSpringInput
from app.calculators.spring import design_compression_spring, design_tension_spring
from app.materials import SPRING_MATERIALS

router = APIRouter(prefix="/api/v1/spring", tags=["Spring Design (IS 7907)"])


@router.get("/materials", summary="List supported spring materials")
def list_spring_materials():
    """Returns all supported spring wire materials with their properties."""
    return {
        "count": len(SPRING_MATERIALS),
        "materials": {
            key: {
                "name": v["name"],
                "description": v["description"],
                "shear_modulus_G_GPa": v["G"],
                "elastic_modulus_E_GPa": v["E"],
                "max_service_temp_C": v["max_service_temp_C"],
                "Ssy_coeff": v["Ssy_coeff"],
            }
            for key, v in SPRING_MATERIALS.items()
        },
    }


@router.post("/helical-compression", summary="Design a helical compression spring (IS 7907)")
def design_compression(data: CompressionSpringInput):
    """
    Designs a helical compression spring per IS 7907 using Wahl's correction factor.

    **Outputs include:**
    - Wire diameter, mean/outer/inner coil diameters
    - Number of active and total coils
    - Free length, working length, solid length
    - Spring rate, pitch, clash allowance
    - Shear stress, safety factor, buckling check
    """
    try:
        result = design_compression_spring(
            load_N=data.load_N,
            deflection_mm=data.deflection_mm,
            spring_index=data.spring_index,
            material=data.material,
            safety_factor=data.safety_factor,
            end_type=data.end_type,
            clash_allowance=data.clash_allowance,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Calculation error: {e}")


@router.post("/helical-tension", summary="Design a helical tension spring (IS 7907)")
def design_tension(data: TensionSpringInput):
    """
    Designs a helical tension spring per IS 7907.
    Includes hook stress check as per IS 7907 §4.6.

    **Outputs include:**
    - Wire diameter, coil diameters
    - Active coils, body length, extended length
    - Body shear stress and hook bending stress
    """
    try:
        result = design_tension_spring(
            load_N=data.load_N,
            deflection_mm=data.deflection_mm,
            spring_index=data.spring_index,
            material=data.material,
            safety_factor=data.safety_factor,
            hook_type=data.hook_type,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Calculation error: {e}")
