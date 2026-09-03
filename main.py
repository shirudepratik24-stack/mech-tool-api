"""
Gear / Spring Design Calculator API
=====================================
A FastAPI application implementing standard mechanical engineering design
formulas for gears (AGMA 2001-D04) and springs (IS 7907).

Author : Mech Tool API
Version: 1.0.0
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.routers import gear, spring

# ---------------------------------------------------------------------------
# App definition
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Gear / Spring Design Calculator API",
    description="""
## 🔧 Mechanical Engineering Design Calculator

A REST API implementing standard design formulas for:

### Gear Design (AGMA 2001-D04)
- **Spur Gears** — Lewis bending stress, AGMA contact stress, module selection
- **Helical Gears** — Virtual tooth count, helix angle corrections, normal/transverse module

### Spring Design (IS 7907 / IS 4454)
- **Helical Compression Springs** — Wahl's factor, wire sizing, buckling check
- **Helical Tension Springs** — Body stress, hook bending stress

### Features
- Standard module selection (IS/AGMA series)
- Preferred wire diameter selection (IS 4454 series)
- Material databases (8 gear materials, 7 spring materials)
- Automatic safety factor verification
- Design recommendations

### Units
All inputs/outputs use **SI units**: N, mm, MPa, kW, RPM
""",
    version="1.0.0",
    contact={
        "name": "Mech Tool API",
        "url": "https://github.com/yourusername/mech-tool-api",
    },
    license_info={
        "name": "MIT",
    },
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# ---------------------------------------------------------------------------
# CORS — allow all origins (adjust for production)
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Include routers
# ---------------------------------------------------------------------------
app.include_router(gear.router)
app.include_router(spring.router)


# ---------------------------------------------------------------------------
# Root & Health
# ---------------------------------------------------------------------------
@app.get("/", tags=["Info"], summary="API information")
def root():
    return {
        "api": "Gear / Spring Design Calculator API",
        "version": "1.0.0",
        "standards": ["AGMA 2001-D04", "IS 7907", "IS 4454"],
        "endpoints": {
            "docs": "/docs",
            "redoc": "/redoc",
            "health": "/health",
            "gear_spur": "/api/v1/gear/spur",
            "gear_helical": "/api/v1/gear/helical",
            "gear_materials": "/api/v1/gear/materials",
            "spring_compression": "/api/v1/spring/helical-compression",
            "spring_tension": "/api/v1/spring/helical-tension",
            "spring_materials": "/api/v1/spring/materials",
        },
        "units": "SI — N, mm, MPa, kW, RPM",
    }


@app.get("/health", tags=["Info"], summary="Health check")
def health():
    return JSONResponse(content={"status": "ok", "api": "Gear/Spring Design Calculator"})
