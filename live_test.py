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
    with urllib.request.urlopen(req, timeout=30, context=ctx) as r:
        return json.loads(r.read())

def get(path):
    with urllib.request.urlopen(BASE + path, timeout=30, context=ctx) as r:
        return json.loads(r.read())

sep = "=" * 60
print(sep)
print(f"LIVE API TEST  ->  {BASE}")
print(sep)

# 1. Health
h = get("/health")
print(f"\n[1] GET /health           -> status={h['status']!r}   PASS={h['status']=='ok'}")
assert h["status"] == "ok"

# 2. Root
root = get("/")
print(f"[2] GET /                 -> version={root['version']!r}  standards={root['standards']}")

# 3. Gear materials
gm = get("/api/v1/gear/materials")
print(f"[3] GET /api/v1/gear/materials      -> {gm['count']} materials: {list(gm['materials'].keys())[:3]}...")

# 4. Spring materials
sm = get("/api/v1/spring/materials")
print(f"[4] GET /api/v1/spring/materials    -> {sm['count']} materials: {list(sm['materials'].keys())[:3]}...")

# 5. Spur gear
print(f"\n[5] POST /api/v1/gear/spur  (10kW, 1450rpm, ratio=3, c45_hardened x c45_normalised)")
g = post("/api/v1/gear/spur", {
    "power_kw": 10, "speed_rpm": 1450, "gear_ratio": 3.0,
    "pinion_material": "c45_hardened", "gear_material": "c45_normalised",
    "safety_factor_bending": 1.5, "safety_factor_contact": 1.2
})
dv = g["design_values"]; sa = g["stress_analysis"]
print(f"    Module m            : {dv['module_m']}")
print(f"    Face width          : {dv['face_width_mm']} mm")
print(f"    Pinion PCD          : {dv['pinion_pitch_diameter_mm']} mm  |  Gear PCD: {dv['gear_pitch_diameter_mm']} mm")
print(f"    Centre distance     : {dv['centre_distance_mm']} mm")
print(f"    Wt (tangential)     : {g['loads_and_factors']['tangential_load_Wt_N']} N")
print(f"    Kv (dynamic)        : {g['loads_and_factors']['Kv_dynamic_factor']}")
print(f"    Bending SF (pinion) : {sa['bending']['pinion_bending_SF']}  (required >= 1.5)")
print(f"    Contact SF (pinion) : {sa['contact']['pinion_contact_SF']}  (required >= 1.2)")
print(f"    Recommendation      : {g['recommendations'][0]}")
print(f"    Overall STATUS      : {g['overall_status']}")
assert g["overall_status"] == "PASS"

# 6. Helical gear
print(f"\n[6] POST /api/v1/gear/helical  (15kW, 1450rpm, ratio=4, helix=20deg)")
hg = post("/api/v1/gear/helical", {
    "power_kw": 15, "speed_rpm": 1450, "gear_ratio": 4.0,
    "helix_angle_deg": 20.0,
    "pinion_material": "c45_hardened", "gear_material": "c45_normalised",
    "safety_factor_bending": 1.5, "safety_factor_contact": 1.2
})
dv2 = hg["design_values"]; sa2 = hg["stress_analysis"]
print(f"    Normal module mn    : {dv2['normal_module_mn']}  |  Transverse mt: {dv2['transverse_module_mt']}")
print(f"    Face width          : {dv2['face_width_mm']} mm  |  Lead: {dv2['lead_mm']} mm")
print(f"    Pinion PCD          : {dv2['pinion_pitch_diameter_mm']} mm  |  Virtual teeth N1v: {dv2['virtual_teeth_pinion']}")
print(f"    Bending SF (pinion) : {sa2['bending']['pinion_bending_SF']}")
print(f"    Contact SF          : {sa2['contact']['pinion_contact_SF']}")
print(f"    Overall STATUS      : {hg['overall_status']}")
assert hg["overall_status"] == "PASS"

# 7. Compression spring
print(f"\n[7] POST /api/v1/spring/helical-compression  (500N, 25mm, C=6, hard_drawn_wire)")
s = post("/api/v1/spring/helical-compression", {
    "load_N": 500, "deflection_mm": 25, "spring_index": 6.0,
    "material": "hard_drawn_wire", "safety_factor": 1.5, "end_type": "closed_ground"
})
sv = s["design_values"]; ss = s["stress_analysis"]
print(f"    Wire dia d          : {sv['wire_diameter_d_mm']} mm (IS 4454 preferred)")
print(f"    Mean coil dia D     : {sv['mean_coil_diameter_D_mm']} mm  |  OD: {sv['outer_diameter_OD_mm']} mm")
print(f"    Active coils Na     : {sv['active_coils_Na']}  |  Total Nt: {sv['total_coils_Nt']}")
print(f"    Free length Lo      : {sv['free_length_Lo_mm']} mm  |  Solid Ls: {sv['solid_length_Ls_mm']} mm")
print(f"    Spring rate k       : {sv['spring_rate_k_N_mm']} N/mm")
print(f"    Wahl's K            : {sv['Wahl_correction_K']}")
print(f"    Actual shear stress : {ss['actual_shear_stress_tau_MPa']} MPa  (allow: {ss['allowable_shear_stress_MPa']} MPa)")
print(f"    Safety factor       : {ss['actual_safety_factor']}  (required >= 1.5)")
print(f"    Buckling            : {s['geometry_checks']['buckling_note']}")
print(f"    Overall STATUS      : {s['overall_status']}")
assert s["overall_status"] == "PASS"

# 8. Tension spring
print(f"\n[8] POST /api/v1/spring/helical-tension  (300N, 20mm, chrome_vanadium)")
t = post("/api/v1/spring/helical-tension", {
    "load_N": 300, "deflection_mm": 20, "spring_index": 6.0,
    "material": "chrome_vanadium", "safety_factor": 1.5
})
tv = t["design_values"]; ts = t["stress_analysis"]
print(f"    Wire dia d          : {tv['wire_diameter_d_mm']} mm")
print(f"    Mean coil dia D     : {tv['mean_coil_diameter_D_mm']} mm")
print(f"    Active coils Na     : {tv['active_coils_Na']}")
print(f"    Body shear tau      : {ts['body_shear_stress_tau_MPa']} MPa  |  Allowable: {ts['allowable_shear_stress_MPa']} MPa")
print(f"    Hook stress         : {ts['hook_bending_stress_MPa']} MPa  |  Allowable: {ts['hook_allowable_stress_MPa']} MPa")
print(f"    Body SF             : {ts['actual_safety_factor']}")
print(f"    Hook status         : {ts['hook_status']}")
print(f"    Overall STATUS      : {t['overall_status']}")
assert t["overall_status"] == "PASS"

print()
print(sep)
print("  ALL 8 LIVE ENDPOINT TESTS PASSED")
print(f"  Swagger UI  ->  {BASE}/docs")
print(f"  ReDoc       ->  {BASE}/redoc")
print(sep)
