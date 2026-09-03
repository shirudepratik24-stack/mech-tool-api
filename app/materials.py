"""
Material Property Database
Contains properties for gear materials (AGMA) and spring materials (IS 7907).
All stress values in MPa, modulus in GPa.
"""

from typing import Dict, Any

# ---------------------------------------------------------------------------
# GEAR MATERIALS  (AGMA 2101-D04)
# ---------------------------------------------------------------------------
GEAR_MATERIALS: Dict[str, Dict[str, Any]] = {
    "cast_iron_grade20": {
        "name": "Cast Iron Grade 20",
        "Sut": 200, "Sy": 140, "BHN": 180, "E": 100.0,
        "Sat": 55.0, "Sac": 490.0,
        "description": "General purpose cast iron",
    },
    "cast_iron_grade30": {
        "name": "Cast Iron Grade 30",
        "Sut": 310, "Sy": 210, "BHN": 220, "E": 110.0,
        "Sat": 69.0, "Sac": 550.0,
        "description": "Higher strength cast iron",
    },
    "c45_normalised": {
        "name": "C45 Steel (Normalised)",
        "Sut": 700, "Sy": 380, "BHN": 200, "E": 207.0,
        "Sat": 186.0, "Sac": 1240.0,
        "description": "Medium carbon steel, normalised",
    },
    "c45_hardened": {
        "name": "C45 Steel (Q&T)",
        "Sut": 900, "Sy": 650, "BHN": 280, "E": 207.0,
        "Sat": 241.0, "Sac": 1550.0,
        "description": "Medium carbon steel, quenched & tempered",
    },
    "en36_case_hardened": {
        "name": "EN36 Case Hardened",
        "Sut": 1100, "Sy": 850, "BHN": 350, "E": 207.0,
        "Sat": 380.0, "Sac": 1900.0,
        "description": "Case hardened alloy steel (55 HRC surface)",
    },
    "20cr4_alloy": {
        "name": "20Cr4 Alloy Steel",
        "Sut": 1000, "Sy": 800, "BHN": 320, "E": 207.0,
        "Sat": 310.0, "Sac": 1750.0,
        "description": "Chromium alloy steel, carburised & hardened",
    },
    "stainless_316": {
        "name": "Stainless Steel 316",
        "Sut": 515, "Sy": 205, "BHN": 149, "E": 193.0,
        "Sat": 138.0, "Sac": 862.0,
        "description": "Austenitic stainless steel",
    },
    "bronze_tin": {
        "name": "Phosphor Bronze",
        "Sut": 310, "Sy": 140, "BHN": 90, "E": 103.0,
        "Sat": 65.0, "Sac": 490.0,
        "description": "Used for worm wheel pairing",
    },
}

# Lewis form factor Y for 20-degree full-depth involute teeth
LEWIS_FORM_FACTOR: Dict[int, float] = {
    12: 0.245, 13: 0.261, 14: 0.277, 15: 0.290, 16: 0.296,
    17: 0.303, 18: 0.309, 19: 0.314, 20: 0.322, 22: 0.331,
    24: 0.337, 26: 0.346, 28: 0.353, 30: 0.360, 34: 0.371,
    38: 0.384, 43: 0.397, 50: 0.409, 60: 0.422, 75: 0.435,
    100: 0.447, 150: 0.460, 300: 0.472, 400: 0.480,
}

# Elastic coefficient Ze sqrt(MPa) — AGMA 2001-D04 Table 3
ELASTIC_COEFFICIENT: Dict[str, float] = {
    "steel_steel": 191.0,
    "steel_cast_iron": 165.0,
    "steel_bronze": 158.0,
    "cast_iron_cast_iron": 149.0,
    "cast_iron_bronze": 145.0,
}

# ---------------------------------------------------------------------------
# SPRING MATERIALS  (IS 7907 / IS 4454 / ASTM)
# ---------------------------------------------------------------------------
SPRING_MATERIALS: Dict[str, Dict[str, Any]] = {
    "hard_drawn_wire": {
        "name": "Hard Drawn Wire (IS 4454 Gr.2)",
        "G": 81.6, "E": 207.0, "density": 7850,
        "max_service_temp_C": 120, "Ssy_coeff": 0.45,
        "description": "General purpose cold drawn carbon steel",
    },
    "music_wire": {
        "name": "Music Wire (IS 4454 Gr.1 / ASTM A228)",
        "G": 81.6, "E": 207.0, "density": 7850,
        "max_service_temp_C": 120, "Ssy_coeff": 0.45,
        "description": "Highest quality, best fatigue resistance",
    },
    "oil_tempered_wire": {
        "name": "Oil Tempered Wire (ASTM A229)",
        "G": 79.3, "E": 207.0, "density": 7850,
        "max_service_temp_C": 180, "Ssy_coeff": 0.50,
        "description": "Good for static and low-cycle applications",
    },
    "chrome_vanadium": {
        "name": "Chrome-Vanadium (ASTM A232)",
        "G": 79.3, "E": 207.0, "density": 7850,
        "max_service_temp_C": 220, "Ssy_coeff": 0.52,
        "description": "Good fatigue & elevated temperature resistance",
    },
    "chrome_silicon": {
        "name": "Chrome-Silicon (ASTM A401)",
        "G": 79.3, "E": 207.0, "density": 7850,
        "max_service_temp_C": 250, "Ssy_coeff": 0.52,
        "description": "High stress, elevated temperature use",
    },
    "stainless_302": {
        "name": "Stainless 302/304 (ASTM A313)",
        "G": 68.9, "E": 193.0, "density": 8000,
        "max_service_temp_C": 260, "Ssy_coeff": 0.44,
        "description": "Corrosion-resistant, non-magnetic",
    },
    "phosphor_bronze": {
        "name": "Phosphor Bronze (ASTM B197)",
        "G": 41.4, "E": 103.0, "density": 8800,
        "max_service_temp_C": 95, "Ssy_coeff": 0.35,
        "description": "Non-magnetic, corrosion-resistant",
    },
}

# Sut power law: Sut = A / d^b  (d in mm, Sut in MPa) — Shigley Table 10-4
SPRING_WIRE_SUT: Dict[str, Dict[str, Any]] = {
    "music_wire":       {"A": 2211.0, "b": 0.145},
    "hard_drawn_wire":  {"A": 1510.0, "b": 0.201},
    "oil_tempered_wire":{"A": 1610.0, "b": 0.193},
    "chrome_vanadium":  {"A": 1790.0, "b": 0.155},
    "chrome_silicon":   {"A": 1960.0, "b": 0.091},
    "stainless_302":    {"A": 1867.0, "b": 0.146},
    "phosphor_bronze":  {"A":  932.0, "b": 0.064},
}


def get_lewis_factor(N: int) -> float:
    """Interpolate Lewis form factor Y for number of teeth N."""
    teeth = sorted(LEWIS_FORM_FACTOR.keys())
    if N <= teeth[0]:
        return LEWIS_FORM_FACTOR[teeth[0]]
    if N >= teeth[-1]:
        return LEWIS_FORM_FACTOR[teeth[-1]]
    for i in range(len(teeth) - 1):
        if teeth[i] <= N <= teeth[i + 1]:
            t1, t2 = teeth[i], teeth[i + 1]
            y1, y2 = LEWIS_FORM_FACTOR[t1], LEWIS_FORM_FACTOR[t2]
            return y1 + (y2 - y1) * (N - t1) / (t2 - t1)
    return 0.35


def get_spring_sut(material: str, d_mm: float) -> float:
    """Calculate Sut (MPa) for spring wire using Shigley power law."""
    data = SPRING_WIRE_SUT.get(material, SPRING_WIRE_SUT["hard_drawn_wire"])
    return data["A"] / (d_mm ** data["b"])
