"""
Gear / Spring Design Calculator API & Web UI
============================================
FastAPI application with AGMA 2001-D04 gear formulas,
IS 7907 spring formulas, and interactive Web UI.
"""

import os
from pathlib import Path
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.routers import gear, spring
from app.materials import GEAR_MATERIALS, SPRING_MATERIALS
from app.schemas.gear import SpurGearInput
from app.schemas.spring import CompressionSpringInput

app = FastAPI(
    title="Gear / Spring Design Calculator API",
    description="AGMA 2001-D04 Gear Design & IS 7907 Spring Design Calculator Suite",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static folder if exists
static_path = Path(__file__).parent / "static"
if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

# Include routers
app.include_router(gear.router)
app.include_router(spring.router)


# ---------------------------------------------------------------------------
# Root UI — Serves the interactive calculator web interface
# ---------------------------------------------------------------------------
@app.get("/", response_class=HTMLResponse, tags=["Web UI"], summary="Interactive Web Calculator UI")
def serve_home(request: Request):
    index_file = static_path / "index.html"
    if index_file.exists():
        return HTMLResponse(content=index_file.read_text(encoding="utf-8"))
    return HTMLResponse("<h2>MechCalc API is running. Visit <a href='/docs'>/docs</a></h2>")


# ---------------------------------------------------------------------------
# Health check (used by Railway.app)
# ---------------------------------------------------------------------------
@app.get("/health", tags=["Info"], summary="Health check")
def health():
    return JSONResponse(content={"status": "ok", "api": "Gear/Spring Design Calculator"})


# ---------------------------------------------------------------------------
# Compatibility Endpoints
# ---------------------------------------------------------------------------
@app.get("/materials", tags=["Materials"], summary="Combined Materials Catalog")
def get_all_materials():
    return {
        "gear_materials": GEAR_MATERIALS,
        "spring_materials": SPRING_MATERIALS,
    }


@app.post("/gear", tags=["Gear Design (AGMA)"], summary="Spur gear calculation (alias)")
def gear_alias(data: SpurGearInput):
    return gear.design_spur(data)


@app.post("/spring", tags=["Spring Design (IS 7907)"], summary="Compression spring calculation (alias)")
def spring_alias(data: CompressionSpringInput):
    return spring.design_compression(data)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)