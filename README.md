# ⚙️ Gear / Spring Design Calculator API

A production-ready REST API for mechanical engineering gear and spring design calculations.

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template)

## Standards Implemented

| Component | Standard |
|-----------|----------|
| Spur & Helical Gears | **AGMA 2001-D04** |
| Helical Springs | **IS 7907** |
| Wire Materials | **IS 4454** |

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API info |
| GET | `/health` | Health check |
| POST | `/api/v1/gear/spur` | Spur gear design |
| POST | `/api/v1/gear/helical` | Helical gear design |
| GET | `/api/v1/gear/materials` | Gear materials list |
| POST | `/api/v1/spring/helical-compression` | Compression spring design |
| POST | `/api/v1/spring/helical-tension` | Tension spring design |
| GET | `/api/v1/spring/materials` | Spring materials list |

Interactive docs: **`/docs`** (Swagger UI) | **`/redoc`** (ReDoc)

## Units

All inputs and outputs use **SI units**: N, mm, MPa, kW, RPM

## Quick Start

### Local Development

```bash
pip install -r requirements.txt
uvicorn main:app --reload
# Open http://localhost:8000/docs
```

### Example — Spur Gear Design

```bash
curl -X POST http://localhost:8000/api/v1/gear/spur \
  -H "Content-Type: application/json" \
  -d "{
    \"power_kw\": 10,
    \"speed_rpm\": 1450,
    \"gear_ratio\": 3,
    \"pinion_material\": \"c45_hardened\",
    \"gear_material\": \"c45_normalised\",
    \"safety_factor_bending\": 1.5,
    \"safety_factor_contact\": 1.2
  }"
```

### Example — Compression Spring Design

```bash
curl -X POST http://localhost:8000/api/v1/spring/helical-compression \
  -H "Content-Type: application/json" \
  -d "{
    \"load_N\": 500,
    \"deflection_mm\": 25,
    \"spring_index\": 6,
    \"material\": \"hard_drawn_wire\",
    \"safety_factor\": 1.5,
    \"end_type\": \"closed_ground\"
  }"
```

## Response Structure

Every response includes:
- `inputs` — Echo of all input parameters
- `design_values` — Computed dimensions (module, face width, wire dia, etc.)
- `stress_analysis` — Stress values vs allowable with PASS/FAIL
- `overall_status` — `"PASS"` or `"FAIL"`
- `recommendations` — Design improvement notes

## Supported Materials

### Gear Materials (AGMA)
- Cast Iron Grade 20 / Grade 30
- C45 Steel (Normalised / Q&T)
- EN36 Case Hardened
- 20Cr4 Alloy Steel
- Stainless Steel 316
- Phosphor Bronze

### Spring Wire Materials (IS 4454)
- Hard Drawn Wire (IS 4454 Gr.2)
- Music Wire (IS 4454 Gr.1)
- Oil Tempered Wire
- Chrome-Vanadium
- Chrome-Silicon
- Stainless 302/304
- Phosphor Bronze

## Deploy to Railway

1. Fork this repository
2. Go to [railway.app](https://railway.app) → New Project → Deploy from GitHub
3. Select this repo → Railway auto-detects Python via Nixpacks
4. The `railway.toml` configures gunicorn with 4 workers

## License

MIT License
