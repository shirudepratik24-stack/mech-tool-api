"""
Gear / Spring Design Calculator API & Web Studio
================================================
FastAPI application with AGMA 2001-D04 gear formulas,
IS 7907 spring formulas, and professional frontend UI.
"""

import os
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from app.routers import gear, spring
from app.materials import GEAR_MATERIALS, SPRING_MATERIALS
from app.schemas.gear import SpurGearInput
from app.schemas.spring import CompressionSpringInput

app = FastAPI(
    title="MechEngine CAD API",
    description="AGMA 2001-D04 Gear Design & IS 7907 Spring Design Calculator Suite",
    version="1.2.0",
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

# Base frontend directory
frontend_path = Path(__file__).parent / "frontend"
if frontend_path.exists():
    app.mount("/frontend", StaticFiles(directory=str(frontend_path)), name="frontend")

# Include calculation routers
app.include_router(gear.router)
app.include_router(spring.router)


# ---------------------------------------------------------------------------
# Root UI — Serves the Professional Engineering Web CAD
# ---------------------------------------------------------------------------
@app.get("/", response_class=HTMLResponse, tags=["Web UI"], summary="Interactive Engineering CAD UI")
def serve_home(request: Request):
    index_file = frontend_path / "index.html"
    if index_file.exists():
        return FileResponse(index_file, media_type="text/html")
    return HTMLResponse("<h2>MechEngine CAD is running. Visit <a href='/docs'>/docs</a></h2>")


@app.get("/style.css", include_in_schema=False)
def serve_css():
    css_file = frontend_path / "style.css"
    if css_file.exists():
        return FileResponse(css_file, media_type="text/css")
    return JSONResponse(status_code=404, content={"error": "style.css not found"})


@app.get("/script.js", include_in_schema=False)
def serve_js():
    js_file = frontend_path / "script.js"
    if js_file.exists():
        return FileResponse(js_file, media_type="application/javascript")
    return JSONResponse(status_code=404, content={"error": "script.js not found"})


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