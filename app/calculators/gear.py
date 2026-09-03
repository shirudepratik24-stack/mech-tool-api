"""
AGMA Gear Design Calculator
Implements AGMA 2001-D04 / AGMA 2101-D04 formulas for spur and helical gears.
All inputs in SI units: kW, RPM, N·mm, MPa.
"""

import math
from typing import Dict, Any, Tuple
from app.materials import (
    GEAR_MATERIALS, ELASTIC_COEFFICIENT,
    get_lewis_factor
)


def _velocity_factor(V: float) -> float:
    """
    AGMA velocity (dynamic) factor Kv using Barth equation.
    V: pitch line velocity in m/s
    Returns Kv (>1, applied as divisor in Lewis equation form,
    or multiplier in stress form).
    """
    # For cut or milled profile gears (Grade 6): Kv = (6.1 + V) / 6.1
    # For shaved / ground gears a finer formula is used; we use the
    # conservative Barth form common in IS / textbook practice.
    return (6.1 + V) / 6.1


def _overload_factor(load_type: str) -> float:
    """Ko overload factor — AGMA 2001 Table 1."""
    table = {
        "uniform": 1.00,
        "light_shock": 1.25,
        "moderate_shock": 1.50,
        "heavy_shock": 1.75,
    }
    return table.get(load_type, 1.25)


def _size_factor(m: float) -> float:
    """Ks size factor (AGMA 2001-D04 §6.3)."""
    if m < 5:
        return 1.0
    return 1.192 * (m / 25.4) ** 0.0535  # simplified


def _load_distribution_factor(b: float, d: float) -> float:
    """
    Km (KH) load distribution factor.
    Simplified formula for commercial enclosed gear units:
    Km = 1 + Cmc*(Cpf*Cpm + Cma*Ce)
    We use the simplified empirical approach:
    b/d ratio-based estimate.
    """
    bd = b / d
    if bd <= 0.5:
        return 1.3
    elif bd <= 2.0:
        return 1.3 + 0.1 * (bd - 0.5)
    else:
        return 1.45


def _geometry_factor_bending(N: int, helix_angle_deg: float = 0.0) -> float:
    """
    J factor for bending (AGMA 2001).
    Approximated via Lewis form factor Y with helix correction.
    """
    Y = get_lewis_factor(N)
    if helix_angle_deg > 0:
        psi = math.radians(helix_angle_deg)
        Y = Y / math.cos(psi)
    return Y


def design_spur_gear(
    power_kw: float,
    speed_rpm: float,
    gear_ratio: float,
    pinion_material: str,
    gear_material: str,
    safety_factor_bending: float = 1.5,
    safety_factor_contact: float = 1.2,
    load_type: str = "uniform",
    pressure_angle_deg: float = 20.0,
    min_teeth_pinion: int = 18,
) -> Dict[str, Any]:
    """
    Design a spur gear pair using AGMA 2001-D04.

    Returns a dict with all computed design values.
    """
    mat_p = GEAR_MATERIALS.get(pinion_material)
    mat_g = GEAR_MATERIALS.get(gear_material)
    if mat_p is None:
        raise ValueError(f"Unknown pinion material: {pinion_material}")
    if mat_g is None:
        raise ValueError(f"Unknown gear material: {gear_material}")

    # ---- Torque on pinion ----
    T_pinion_Nm = (power_kw * 1000 * 60) / (2 * math.pi * speed_rpm)  # N·m
    T_pinion_Nmm = T_pinion_Nm * 1000  # N·mm

    # ---- Number of teeth ----
    N1 = min_teeth_pinion
    N2 = round(gear_ratio * N1)

    # ---- Module estimation: iterate over standard modules until SF is met ----
    Y1 = get_lewis_factor(N1)
    Ko = _overload_factor(load_type)
    sat_p = mat_p["Sat"] / safety_factor_bending

    standard_modules = [1, 1.25, 1.5, 2, 2.5, 3, 4, 5, 6, 8, 10, 12, 16, 20]

    m = standard_modules[0]
    for m_candidate in standard_modules:
        m = m_candidate
        d1_c = m * N1
        V_c = math.pi * d1_c * speed_rpm / 60_000
        Kv_c = _velocity_factor(V_c)
        Ks_c = _size_factor(m)
        F_c = 10 * m
        Km_c = _load_distribution_factor(F_c, d1_c)
        Wt_c = T_pinion_Nmm / (d1_c / 2)
        sigma_c = (Wt_c * Kv_c * Ko * Ks_c * Km_c) / (F_c * m * Y1)
        if sigma_c <= sat_p:
            break  # found adequate module

    # ---- Final geometry ----
    d1 = m * N1       # pinion pitch diameter (mm)
    d2 = m * N2       # gear pitch diameter (mm)
    V = math.pi * d1 * speed_rpm / 60_000   # pitch line velocity (m/s)
    Kv = _velocity_factor(V)
    Ks = _size_factor(m)
    F = 10 * m         # face width (mm)  — AGMA recommended 8m to 16m
    Km = _load_distribution_factor(F, d1)

    Wt = T_pinion_Nmm / (d1 / 2)   # tangential load (N)

    # ---- Lewis bending stress check ----
    sigma_b_pinion = (Wt * Kv * Ko * Ks * Km) / (F * m * Y1)
    Y2 = get_lewis_factor(N2)
    sigma_b_gear = (Wt * Kv * Ko * Ks * Km) / (F * m * Y2)

    SF_b_pinion = mat_p["Sat"] / sigma_b_pinion
    SF_b_gear = mat_g["Sat"] / sigma_b_gear

    # ---- AGMA contact stress (Hertz) ----
    # σH = Ze * sqrt(Wt * Ko * Kv * Ks * Km / (d1 * F * ZR))
    # ZR (surface condition factor) ≈ 1.0 (well-finished)
    ZR = 1.0
    Ze = ELASTIC_COEFFICIENT.get("steel_steel", 191.0)
    if "cast_iron" in pinion_material and "cast_iron" in gear_material:
        Ze = ELASTIC_COEFFICIENT["cast_iron_cast_iron"]
    elif "cast_iron" in pinion_material or "cast_iron" in gear_material:
        Ze = ELASTIC_COEFFICIENT["steel_cast_iron"]
    elif "bronze" in pinion_material or "bronze" in gear_material:
        Ze = ELASTIC_COEFFICIENT["steel_bronze"]

    sigma_H = Ze * math.sqrt(Wt * Ko * Kv * Ks * Km / (d1 * F * ZR))
    SF_H_pinion = mat_p["Sac"] / sigma_H
    SF_H_gear = mat_g["Sac"] / sigma_H

    # ---- Additional geometric values ----
    centre_distance = (d1 + d2) / 2
    circular_pitch = math.pi * m
    addendum = m
    dedendum = 1.25 * m
    clearance = 0.25 * m
    whole_depth = addendum + dedendum
    outside_dia_pinion = d1 + 2 * addendum
    outside_dia_gear = d2 + 2 * addendum
    speed_gear_rpm = speed_rpm / gear_ratio

    status_bending = "PASS" if (SF_b_pinion >= safety_factor_bending and
                                SF_b_gear >= safety_factor_bending) else "FAIL"
    status_contact = "PASS" if (SF_H_pinion >= safety_factor_contact and
                                SF_H_gear >= safety_factor_contact) else "FAIL"

    return {
        "standard": "AGMA 2001-D04",
        "gear_type": "Spur Gear",
        "inputs": {
            "power_kW": power_kw,
            "pinion_speed_rpm": speed_rpm,
            "gear_ratio": gear_ratio,
            "pinion_material": mat_p["name"],
            "gear_material": mat_g["name"],
            "safety_factor_bending": safety_factor_bending,
            "safety_factor_contact": safety_factor_contact,
            "load_type": load_type,
            "pressure_angle_deg": pressure_angle_deg,
        },
        "design_values": {
            "module_m": m,
            "face_width_mm": round(F, 2),
            "pinion_teeth": N1,
            "gear_teeth": N2,
            "actual_gear_ratio": round(N2 / N1, 4),
            "pinion_pitch_diameter_mm": round(d1, 2),
            "gear_pitch_diameter_mm": round(d2, 2),
            "centre_distance_mm": round(centre_distance, 2),
            "circular_pitch_mm": round(circular_pitch, 4),
            "addendum_mm": round(addendum, 3),
            "dedendum_mm": round(dedendum, 3),
            "whole_depth_mm": round(whole_depth, 3),
            "clearance_mm": round(clearance, 3),
            "outside_dia_pinion_mm": round(outside_dia_pinion, 2),
            "outside_dia_gear_mm": round(outside_dia_gear, 2),
        },
        "loads_and_factors": {
            "tangential_load_Wt_N": round(Wt, 2),
            "pitch_line_velocity_m_s": round(V, 4),
            "torque_on_pinion_Nm": round(T_pinion_Nm, 3),
            "Ko_overload_factor": Ko,
            "Kv_dynamic_factor": round(Kv, 4),
            "Ks_size_factor": round(Ks, 4),
            "Km_load_distribution_factor": round(Km, 4),
            "Ze_elastic_coefficient_sqrt_MPa": Ze,
        },
        "stress_analysis": {
            "bending": {
                "pinion_bending_stress_MPa": round(sigma_b_pinion, 2),
                "gear_bending_stress_MPa": round(sigma_b_gear, 2),
                "pinion_allowable_bending_MPa": mat_p["Sat"],
                "gear_allowable_bending_MPa": mat_g["Sat"],
                "pinion_bending_SF": round(SF_b_pinion, 3),
                "gear_bending_SF": round(SF_b_gear, 3),
                "status": status_bending,
            },
            "contact": {
                "contact_stress_MPa": round(sigma_H, 2),
                "pinion_allowable_contact_MPa": mat_p["Sac"],
                "gear_allowable_contact_MPa": mat_g["Sac"],
                "pinion_contact_SF": round(SF_H_pinion, 3),
                "gear_contact_SF": round(SF_H_gear, 3),
                "status": status_contact,
            },
        },
        "output_speeds": {
            "pinion_speed_rpm": round(speed_rpm, 1),
            "gear_speed_rpm": round(speed_gear_rpm, 2),
        },
        "material_properties": {
            "pinion": {k: mat_p[k] for k in ("name", "Sut", "Sy", "BHN", "Sat", "Sac")},
            "gear": {k: mat_g[k] for k in ("name", "Sut", "Sy", "BHN", "Sat", "Sac")},
        },
        "overall_status": "PASS" if status_bending == "PASS" and status_contact == "PASS" else "FAIL",
        "recommendations": _gear_recommendations(m, F, SF_b_pinion, SF_b_gear, SF_H_pinion, SF_H_gear),
    }


def design_helical_gear(
    power_kw: float,
    speed_rpm: float,
    gear_ratio: float,
    helix_angle_deg: float = 20.0,
    pinion_material: str = "c45_hardened",
    gear_material: str = "c45_normalised",
    safety_factor_bending: float = 1.5,
    safety_factor_contact: float = 1.2,
    load_type: str = "uniform",
    min_teeth_pinion: int = 18,
) -> Dict[str, Any]:
    """
    Design a helical gear pair using AGMA 2001-D04.
    Helix angle modifies the effective form factor and face load.
    """
    psi = math.radians(helix_angle_deg)

    # Normal module to transverse module conversion
    # mn = mt * cos(psi)  → we design in normal module then convert
    mat_p = GEAR_MATERIALS.get(pinion_material)
    mat_g = GEAR_MATERIALS.get(gear_material)
    if mat_p is None:
        raise ValueError(f"Unknown pinion material: {pinion_material}")
    if mat_g is None:
        raise ValueError(f"Unknown gear material: {gear_material}")

    T_pinion_Nm = (power_kw * 1000 * 60) / (2 * math.pi * speed_rpm)
    T_pinion_Nmm = T_pinion_Nm * 1000

    N1 = min_teeth_pinion
    N2 = round(gear_ratio * N1)

    # Virtual number of teeth (formative teeth) for helical gears
    N1v = round(N1 / (math.cos(psi) ** 3))
    N2v = round(N2 / (math.cos(psi) ** 3))
    Y1 = _geometry_factor_bending(N1v, helix_angle_deg)
    Ko = _overload_factor(load_type)

    sat_p = mat_p["Sat"] / safety_factor_bending
    standard_modules = [1, 1.25, 1.5, 2, 2.5, 3, 4, 5, 6, 8, 10, 12, 16, 20]

    # Iterate through standard modules until bending SF is satisfied
    m_n = standard_modules[0]
    m_t = m_n / math.cos(psi)
    d1 = d2 = V = Kv = Ks = F = Km = Wt = 0.0
    for m_candidate in standard_modules:
        m_n = m_candidate
        m_t = m_n / math.cos(psi)
        d1 = m_t * N1
        d2 = m_t * N2
        V = math.pi * d1 * speed_rpm / 60_000
        Kv = _velocity_factor(V)
        Ks = _size_factor(m_n)
        F = 12 * m_n
        Km = _load_distribution_factor(F, d1)
        Wt = T_pinion_Nmm / (d1 / 2)
        sigma_c = (Wt * math.cos(psi) * Kv * Ko * Ks * Km) / (F * m_n * Y1)
        if sigma_c <= sat_p:
            break  # adequate module found

    sigma_b_pinion = (Wt * math.cos(psi) * Kv * Ko * Ks * Km) / (F * m_n * Y1)
    Y2 = _geometry_factor_bending(N2v, helix_angle_deg)
    sigma_b_gear = (Wt * math.cos(psi) * Kv * Ko * Ks * Km) / (F * m_n * Y2)

    SF_b_pinion = mat_p["Sat"] / sigma_b_pinion
        "standard": "AGMA 2001-D04",
        "gear_type": "Helical Gear",
        "inputs": {
            "power_kW": power_kw,
            "pinion_speed_rpm": speed_rpm,
            "gear_ratio": gear_ratio,
            "helix_angle_deg": helix_angle_deg,
            "pinion_material": mat_p["name"],
            "gear_material": mat_g["name"],
            "safety_factor_bending": safety_factor_bending,
            "safety_factor_contact": safety_factor_contact,
        },
        "design_values": {
            "normal_module_mn": m_n,
            "transverse_module_mt": round(m_t, 4),
            "face_width_mm": round(F, 2),
            "pinion_teeth": N1,
            "gear_teeth": N2,
            "actual_gear_ratio": round(N2 / N1, 4),
            "pinion_pitch_diameter_mm": round(d1, 2),
            "gear_pitch_diameter_mm": round(d2, 2),
            "centre_distance_mm": round(centre_distance, 2),
            "normal_circular_pitch_mm": round(normal_circular_pitch, 4),
            "lead_mm": round(lead, 2),
            "outside_dia_pinion_mm": round(outside_dia_pinion, 2),
            "outside_dia_gear_mm": round(outside_dia_gear, 2),
            "virtual_teeth_pinion": N1v,
            "virtual_teeth_gear": N2v,
        },
        "loads_and_factors": {
            "tangential_load_Wt_N": round(Wt, 2),
            "pitch_line_velocity_m_s": round(V, 4),
            "torque_on_pinion_Nm": round(T_pinion_Nm, 3),
            "Ko": Ko, "Kv": round(Kv, 4),
            "Ks": round(Ks, 4), "Km": round(Km, 4),
        },
        "stress_analysis": {
            "bending": {
                "pinion_bending_stress_MPa": round(sigma_b_pinion, 2),
                "gear_bending_stress_MPa": round(sigma_b_gear, 2),
                "pinion_bending_SF": round(SF_b_pinion, 3),
                "gear_bending_SF": round(SF_b_gear, 3),
                "status": status_bending,
            },
            "contact": {
                "contact_stress_MPa": round(sigma_H, 2),
                "pinion_contact_SF": round(SF_H_pinion, 3),
                "gear_contact_SF": round(SF_H_gear, 3),
                "status": status_contact,
            },
        },
        "output_speeds": {
            "pinion_speed_rpm": round(speed_rpm, 1),
            "gear_speed_rpm": round(speed_gear_rpm, 2),
        },
        "overall_status": "PASS" if status_bending == "PASS" and status_contact == "PASS" else "FAIL",
        "recommendations": _gear_recommendations(m_n, F, SF_b_pinion, SF_b_gear, SF_H_pinion, SF_H_gear),
    }


def _gear_recommendations(m, F, SF_bp, SF_bg, SF_hp, SF_hg) -> list:
    recs = []
    if m < 2:
        recs.append("Module is very small (<2); consider increasing for ease of manufacture.")
    if F < 8 * m:
        recs.append(f"Face width ({F:.1f} mm) is below AGMA minimum (8m = {8*m} mm).")
    if F > 16 * m:
        recs.append(f"Face width ({F:.1f} mm) exceeds AGMA maximum (16m = {16*m} mm); reduce to avoid crowning issues.")
    if min(SF_bp, SF_bg) < 1.5:
        recs.append("Bending safety factor < 1.5; use harder material or increase module.")
    if min(SF_hp, SF_hg) < 1.2:
        recs.append("Contact safety factor < 1.2; consider surface hardening or better material.")
    if not recs:
        recs.append("Design satisfies all AGMA criteria. Ready for detailed drawing.")
    return recs

