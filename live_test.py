"""Live test against Railway deployment."""
import urllib.request, json, ssl, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE = "https://web-production-238bb.up.railway.app"
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def post(path, data):
    body = json.dumps(data).encode()
    req = urllib.request.Request(
        BASE + path, data=body,
        headers={"Content-Type": "application/json"}, method="POST"
    )
    with urllib.request.urlopen(req, timeout=15, context=ctx) as r:
        return json.loads(r.read())

def get(path):
    with urllib.request.urlopen(BASE + path, timeout=15, context=ctx) as r:
        return json.loads(r.read())

sep = "=" * 60
print(sep)
print(f"LIVE API & UI TEST -> {BASE}")
print(sep)

# 1. Health check
h = get("/health")
print(f"[1] GET /health                      -> status={h['status']!r} PASS={h['status']=='ok'}")
assert h["status"] == "ok"

# 2. Interactive Web UI check
with urllib.request.urlopen(BASE + "/", timeout=15, context=ctx) as r:
    html = r.read().decode("utf-8")
    print(f"[2] GET / (Interactive Web UI)      -> Status={r.status} Content-Type={r.headers.get('content-type')} Length={len(html)}")
    assert "MechCalc Studio" in html
    assert r.status == 200

# 3. Gear materials catalog
gm = get("/api/v1/gear/materials")
print(f"[3] GET /api/v1/gear/materials       -> {gm['count']} materials")

# 4. Spring materials catalog
sm = get("/api/v1/spring/materials")
print(f"[4] GET /api/v1/spring/materials     -> {sm['count']} materials")

# 5. Spur gear calculation
g = post("/api/v1/gear/spur", {
    "power_kw": 10, "speed_rpm": 1450, "gear_ratio": 3.0,
    "pinion_material": "c45_hardened", "gear_material": "c45_normalised",
    "safety_factor_bending": 1.5, "safety_factor_contact": 1.2
})
print(f"[5] POST /api/v1/gear/spur           -> Status={g['overall_status']} Module={g['design_values']['module_m']}mm BendingSF={g['stress_analysis']['bending']['pinion_bending_SF']}")
assert g["overall_status"] == "PASS"

# 6. Helical gear calculation
hg = post("/api/v1/gear/helical", {
    "power_kw": 15, "speed_rpm": 1450, "gear_ratio": 4.0,
    "helix_angle_deg": 20.0, "pinion_material": "c45_hardened", "gear_material": "c45_normalised"
})
print(f"[6] POST /api/v1/gear/helical        -> Status={hg['overall_status']} NormalModule={hg['design_values']['normal_module_mn']}mm BendingSF={hg['stress_analysis']['bending']['pinion_bending_SF']}")
assert hg["overall_status"] == "PASS"

# 7. Compression spring calculation
s = post("/api/v1/spring/helical-compression", {
    "load_N": 500, "deflection_mm": 25, "spring_index": 6.0,
    "material": "hard_drawn_wire", "safety_factor": 1.5
})
print(f"[7] POST /api/v1/spring/helical-comp -> Status={s['overall_status']} WireDia={s['design_values']['wire_diameter_d_mm']}mm ActualSF={s['stress_analysis']['actual_safety_factor']}")
assert s["overall_status"] == "PASS"

# 8. Tension spring calculation
t = post("/api/v1/spring/helical-tension", {
    "load_N": 300, "deflection_mm": 20, "spring_index": 6.0,
    "material": "chrome_vanadium", "safety_factor": 1.5
})
print(f"[8] POST /api/v1/spring/helical-tens -> Status={t['overall_status']} WireDia={t['design_values']['wire_diameter_d_mm']}mm BodySF={t['stress_analysis']['actual_safety_factor']}")
assert t["overall_status"] == "PASS"

print(sep)
print("ALL LIVE TESTS (HEALTH + WEB UI + 4 CALCULATORS) PASSED 100%!")
print(sep)
