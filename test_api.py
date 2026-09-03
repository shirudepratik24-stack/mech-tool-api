"""Quick verification of all calculators."""
import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from app.calculators.gear import design_spur_gear, design_helical_gear
from app.calculators.spring import design_compression_spring, design_tension_spring

print("=== SPUR GEAR (10kW, 1450rpm, ratio=3) ===")
g = design_spur_gear(10, 1450, 3.0, "c45_hardened", "c45_normalised")
dv = g["design_values"]
sa = g["stress_analysis"]
print(f"  Module          : {dv['module_m']}")
print(f"  Face width      : {dv['face_width_mm']} mm")
print(f"  Pinion PCD      : {dv['pinion_pitch_diameter_mm']} mm")
print(f"  Bending SF(pin) : {sa['bending']['pinion_bending_SF']}")
print(f"  Contact SF(pin) : {sa['contact']['pinion_contact_SF']}")
print(f"  Status          : {g['overall_status']}")
assert g["overall_status"] == "PASS", "Spur gear should PASS"

print()
print("=== HELICAL GEAR (15kW, 1450rpm, ratio=4) ===")
h = design_helical_gear(15, 1450, 4.0, 20.0, "c45_hardened", "c45_normalised")
dv2 = h["design_values"]
sa2 = h["stress_analysis"]
print(f"  Normal module   : {dv2['normal_module_mn']}")
print(f"  Face width      : {dv2['face_width_mm']} mm")
print(f"  Bending SF(pin) : {sa2['bending']['pinion_bending_SF']}")
print(f"  Status          : {h['overall_status']}")
assert h["overall_status"] == "PASS", "Helical gear should PASS"

print()
print("=== COMPRESSION SPRING (500N, 25mm deflection) ===")
s = design_compression_spring(500, 25, 6.0, "hard_drawn_wire", 1.5)
sv = s["design_values"]
ss = s["stress_analysis"]
print(f"  Wire dia d      : {sv['wire_diameter_d_mm']} mm")
print(f"  Mean coil dia D : {sv['mean_coil_diameter_D_mm']} mm")
print(f"  Active coils Na : {sv['active_coils_Na']}")
print(f"  Free length     : {sv['free_length_Lo_mm']} mm")
print(f"  Spring rate k   : {sv['spring_rate_k_N_mm']} N/mm")
print(f"  Actual SF       : {ss['actual_safety_factor']}")
print(f"  Status          : {s['overall_status']}")
assert s["overall_status"] == "PASS", "Compression spring should PASS"

print()
print("=== TENSION SPRING (300N, 20mm deflection, chrome-vanadium) ===")
t = design_tension_spring(300, 20, 6.0, "chrome_vanadium", 1.5)
tv = t["design_values"]
ts = t["stress_analysis"]
print(f"  Wire dia d      : {tv['wire_diameter_d_mm']} mm")
print(f"  Mean coil dia D : {tv['mean_coil_diameter_D_mm']} mm")
print(f"  Body SF         : {ts['actual_safety_factor']}")
print(f"  Hook status     : {ts['hook_status']}")
print(f"  Status          : {t['overall_status']}")

print()
print("=== GEAR MATERIALS API ===")
from app.materials import GEAR_MATERIALS, SPRING_MATERIALS
print(f"  Gear materials  : {len(GEAR_MATERIALS)}")
print(f"  Spring materials: {len(SPRING_MATERIALS)}")
assert len(GEAR_MATERIALS) >= 8
assert len(SPRING_MATERIALS) >= 7

print()
print("ALL TESTS PASSED")
