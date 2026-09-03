"""
IS 7907 Helical Spring Design Calculator
Implements Wahl's correction factor method per IS 7907 / Shigley.
All units: N for force, mm for length, MPa for stress, GPa for modulus.
"""

import math
from typing import Dict, Any, Optional
from app.materials import SPRING_MATERIALS, get_spring_sut


def _wahls_factor(C: float) -> float:
    """Wahl's stress correction factor K for direct shear + curvature."""
    return (4 * C - 1) / (4 * C - 4) + 0.615 / C


def _preferred_wire_diameter(d_calc: float) -> float:
    """Return next preferred wire diameter (IS 4454 preferred series, mm)."""
    preferred = [
        0.10, 0.12, 0.16, 0.20, 0.25, 0.315, 0.40, 0.50,
        0.63, 0.80, 1.00, 1.25, 1.60, 2.00, 2.50, 3.00,
        3.15, 4.00, 5.00, 6.00, 6.30, 8.00, 10.0, 12.5,
        16.0, 20.0, 25.0, 28.0, 32.0,
    ]
    for d in preferred:
        if d >= d_calc:
            return d
    return d_calc  # fallback to calculated


def design_compression_spring(
    load_N: float,
    deflection_mm: float,
    spring_index: float = 6.0,
    material: str = "hard_drawn_wire",
    safety_factor: float = 1.5,
    end_type: str = "closed_ground",
    clash_allowance: float = 0.15,
) -> Dict[str, Any]:
    """
    Design a helical compression spring per IS 7907.

    Parameters
    ----------
    load_N          : Working load (N)
    deflection_mm   : Required deflection under working load (mm)
    spring_index    : C = D/d (typically 4–12, default 6)
    material        : Key from SPRING_MATERIALS
    safety_factor   : Factor on allowable shear stress
    end_type        : 'plain', 'plain_ground', 'closed', 'closed_ground'
    clash_allowance : Fraction of free length reserved as clash allowance (default 15%)

    Returns
    -------
    dict with all design values
    """
    mat = SPRING_MATERIALS.get(material)
    if mat is None:
        raise ValueError(f"Unknown spring material: {material}. Valid: {list(SPRING_MATERIALS.keys())}")
    if spring_index < 4:
        raise ValueError("Spring index C < 4 is impractical (high curvature stress).")
    if spring_index > 12:
        raise ValueError("Spring index C > 12 leads to tangling; use C ≤ 12.")

    C = spring_index
    K = _wahls_factor(C)
    G = mat["G"] * 1000  # GPa → MPa·mm²/mm² = MPa; G in MPa for mm formulas

    # ---- Iterative wire diameter design ----
    # Shear stress: τ = 8*K*W*D / (π*d³)  = 8*K*W*C / (π*d²)
    # Allow:       τ_allow = Ssy / SF   where Ssy = Ssy_coeff * Sut(d)
    # Solve iteratively for d

    d = 2.0  # initial guess mm
    for _ in range(30):
        Sut = get_spring_sut(material, d)
        Ssy = mat["Ssy_coeff"] * Sut
        tau_allow = Ssy / safety_factor
        d_new = math.sqrt(8 * K * load_N * C / (math.pi * tau_allow))
        if abs(d_new - d) < 1e-6:
            break
        d = d_new

    # Round up to preferred diameter
    d = _preferred_wire_diameter(d)
    D = C * d   # mean coil diameter (mm)

    # ---- Recompute with selected d ----
    Sut = get_spring_sut(material, d)
    Ssy = mat["Ssy_coeff"] * Sut
    tau_allow = Ssy / safety_factor

    # Actual shear stress
    tau = 8 * K * load_N * D / (math.pi * d ** 3)
    actual_SF = Ssy / tau

    # ---- Spring rate and number of active coils ----
    k = load_N / deflection_mm       # spring rate (N/mm)
    Na = (G * d ** 4) / (8 * D ** 3 * k)   # active coils
    Na = math.ceil(Na * 4) / 4  # round to nearest 0.25

    # ---- End coils ----
    end_coil_table = {
        "plain": (0, 0),
        "plain_ground": (0, 1),
        "closed": (1, 2),
        "closed_ground": (1, 2),
    }
    Ni, Ne = end_coil_table.get(end_type, (1, 2))
    Nt = Na + Ne   # total coils

    # ---- Lengths ----
    Ls = Nt * d            # solid length (mm)
    delta_max = Na * (d if end_type.endswith("ground") else d)
    Lf = Ls / (1 - clash_allowance) + deflection_mm   # free length with clash
    Lo = Lf                 # free length
    Lw = Lf - deflection_mm  # working length (under load)

    # Solid check: Lf - Ls ≥ δ + clash
    clash_mm = clash_allowance * Lf
    if (Lf - Ls) < (deflection_mm + clash_mm):
        # Adjust Lf
        Lf = Ls + deflection_mm + clash_mm
        Lo = Lf

    # ---- Buckling check ----
    # Spring buckles if Lf/D > 5.26 (fixed-free) or > 2.63 (fixed-fixed)
    lf_d_ratio = Lf / D
    buckling_risk = lf_d_ratio > 4.0
    buckling_note = (
        "Buckling risk: Lf/D > 4. Consider guide rod or end fixtures."
        if buckling_risk else
        "No buckling risk (Lf/D ≤ 4)."
    )

    # ---- Outer / Inner diameter ----
    OD = D + d
    ID = D - d

    # ---- Pitch ----
    p = Lf / (Na + 1) if Na > 0 else Lf

    # ---- Weight ----
    wire_length = math.pi * D * Nt
    volume = math.pi * (d / 2) ** 2 * wire_length  # mm³
    weight_N = volume * mat["density"] * 9.81e-9   # convert kg to N (ρ in kg/m³)

    status = "PASS" if tau <= tau_allow and actual_SF >= safety_factor else "FAIL"

    return {
        "standard": "IS 7907 / IS 4454",
        "spring_type": "Helical Compression Spring",
        "inputs": {
            "load_N": load_N,
            "deflection_mm": deflection_mm,
            "spring_index_C": C,
            "material": mat["name"],
            "safety_factor": safety_factor,
            "end_type": end_type,
            "clash_allowance_fraction": clash_allowance,
        },
        "design_values": {
            "wire_diameter_d_mm": round(d, 3),
            "mean_coil_diameter_D_mm": round(D, 3),
            "outer_diameter_OD_mm": round(OD, 3),
            "inner_diameter_ID_mm": round(ID, 3),
            "active_coils_Na": Na,
            "total_coils_Nt": Nt,
            "spring_rate_k_N_mm": round(k, 4),
            "free_length_Lo_mm": round(Lf, 3),
            "working_length_Lw_mm": round(Lw, 3),
            "solid_length_Ls_mm": round(Ls, 3),
            "pitch_p_mm": round(p, 3),
            "clash_allowance_mm": round(clash_mm, 3),
            "spring_index_C": round(C, 3),
            "Wahl_correction_K": round(K, 4),
        },
        "stress_analysis": {
            "actual_shear_stress_tau_MPa": round(tau, 2),
            "allowable_shear_stress_MPa": round(tau_allow, 2),
            "Sut_MPa": round(Sut, 2),
            "Ssy_MPa": round(Ssy, 2),
            "actual_safety_factor": round(actual_SF, 3),
            "required_safety_factor": safety_factor,
            "status": status,
        },
        "geometry_checks": {
            "Lf_D_ratio": round(lf_d_ratio, 3),
            "buckling_risk": buckling_risk,
            "buckling_note": buckling_note,
        },
        "material_properties": {
            "name": mat["name"],
            "shear_modulus_G_GPa": mat["G"],
            "elastic_modulus_E_GPa": mat["E"],
            "max_service_temp_C": mat["max_service_temp_C"],
        },
        "misc": {
            "wire_length_mm": round(wire_length, 1),
            "approximate_weight_N": round(weight_N, 4),
        },
        "overall_status": status,
        "recommendations": _spring_recommendations(d, D, C, Na, lf_d_ratio, actual_SF, safety_factor),
    }


def design_tension_spring(
    load_N: float,
    deflection_mm: float,
    spring_index: float = 6.0,
    material: str = "hard_drawn_wire",
    safety_factor: float = 1.5,
    hook_type: str = "standard_hook",
) -> Dict[str, Any]:
    """
    Design a helical tension spring per IS 7907.
    Tension springs are initially wound close-coiled (no initial gap).
    """
    mat = SPRING_MATERIALS.get(material)
    if mat is None:
        raise ValueError(f"Unknown spring material: {material}")

    C = spring_index
    K = _wahls_factor(C)
    G = mat["G"] * 1000  # MPa

    # Initial tension (pre-load in close-wound tension springs)
    # τ_i = (0.5 * Ssy) for close-wound — IS 7907 guideline
    d = 2.0
    for _ in range(30):
        Sut = get_spring_sut(material, d)
        Ssy = mat["Ssy_coeff"] * Sut
        tau_allow = Ssy / safety_factor
        d_new = math.sqrt(8 * K * load_N * C / (math.pi * tau_allow))
        if abs(d_new - d) < 1e-6:
            break
        d = d_new

    d = _preferred_wire_diameter(d)
    D = C * d
    Sut = get_spring_sut(material, d)
    Ssy = mat["Ssy_coeff"] * Sut
    tau_allow = Ssy / safety_factor
    tau = 8 * K * load_N * D / (math.pi * d ** 3)
    actual_SF = Ssy / tau

    k = load_N / deflection_mm
    Na = (G * d ** 4) / (8 * D ** 3 * k)
    Na = math.ceil(Na * 4) / 4

    # Hook stress — torsional shear at hook bend (IS 7907 / Shigley)
    # Uses Bergstraesser factor KB = (4C+2)/(4C-3)
    KB = (4 * C + 2) / (4 * C - 3)
    sigma_hook = 8 * KB * load_N * D / (math.pi * d ** 3)
    tau_hook_allow = 0.5 * Ssy  # IS 7907: hook allowable = 0.5 * Ssy

    hook_status = "PASS" if sigma_hook <= tau_hook_allow else "FAIL"

    # Body length (close-wound)
    Lb = Na * d
    hook_length = D  # approximate hook extension per end
    total_length = Lb + 2 * hook_length + deflection_mm  # extended length under load

    OD = D + d
    ID = D - d

    status = "PASS" if tau <= tau_allow and actual_SF >= safety_factor and hook_status == "PASS" else "FAIL"

    return {
        "standard": "IS 7907 / IS 4454",
        "spring_type": "Helical Tension Spring",
        "inputs": {
            "load_N": load_N,
            "deflection_mm": deflection_mm,
            "spring_index_C": C,
            "material": mat["name"],
            "safety_factor": safety_factor,
            "hook_type": hook_type,
        },
        "design_values": {
            "wire_diameter_d_mm": round(d, 3),
            "mean_coil_diameter_D_mm": round(D, 3),
            "outer_diameter_OD_mm": round(OD, 3),
            "inner_diameter_ID_mm": round(ID, 3),
            "active_coils_Na": Na,
            "spring_rate_k_N_mm": round(k, 4),
            "body_length_Lb_mm": round(Lb, 3),
            "extended_length_mm": round(total_length, 3),
            "spring_index_C": C,
            "Wahl_correction_K": round(K, 4),
        },
        "stress_analysis": {
            "body_shear_stress_tau_MPa": round(tau, 2),
            "allowable_shear_stress_MPa": round(tau_allow, 2),
            "hook_bending_stress_MPa": round(sigma_hook, 2),
            "hook_allowable_stress_MPa": round(tau_hook_allow, 2),
            "hook_status": hook_status,
            "Sut_MPa": round(Sut, 2),
            "Ssy_MPa": round(Ssy, 2),
            "actual_safety_factor": round(actual_SF, 3),
            "status": "PASS" if tau <= tau_allow else "FAIL",
        },
        "material_properties": {
            "name": mat["name"],
            "shear_modulus_G_GPa": mat["G"],
            "max_service_temp_C": mat["max_service_temp_C"],
        },
        "overall_status": status,
        "recommendations": _spring_recommendations(d, D, C, Na, total_length / D, actual_SF, safety_factor),
    }


def _spring_recommendations(d, D, C, Na, lf_d, actual_SF, req_SF):
    recs = []
    if C < 4:
        recs.append("Spring index C < 4: Very high curvature stresses. Increase C or reduce load.")
    if C > 12:
        recs.append("Spring index C > 12: Risk of tangling. Use C ≤ 12.")
    if Na < 3:
        recs.append("Active coils < 3: Spring may be unstable. Increase Na by reducing wire diameter.")
    if Na > 15:
        recs.append("Active coils > 15: Consider multi-spring arrangement.")
    if lf_d > 4:
        recs.append("Lf/D > 4: Buckling risk. Use a guide rod or change proportions.")
    if actual_SF < req_SF:
        recs.append(f"Safety factor {actual_SF:.2f} < required {req_SF}: Use stronger material or increase wire diameter.")
    if not recs:
        recs.append("Design satisfies IS 7907 criteria. Ready for detailed drawing.")
    return recs
