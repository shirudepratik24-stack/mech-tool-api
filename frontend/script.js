// MechEngine CAD Studio - Interactive JavaScript Engine
let currentTab = 'spur';
let lastCalculatedData = null;

// Tab Management
function switchTab(tabId) {
  currentTab = tabId;
  document.querySelectorAll('.tab-content').forEach(el => el.classList.add('hidden'));
  document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));

  const targetContent = document.getElementById('tab-' + tabId);
  const targetBtn = document.getElementById('tab-btn-' + tabId);
  if (targetContent) targetContent.classList.remove('hidden');
  if (targetBtn) targetBtn.classList.add('active');

  // Trigger canvas resize or materials load if needed
  if (tabId === 'materials') {
    loadMaterialsCatalog();
  }
}

// Visual Schematic Rendering (Canvas 2D)
function drawGearSchematic(d1, d2, F, m) {
  const canvas = document.getElementById('schematic-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  const w = canvas.width;
  const h = canvas.height;

  ctx.clearRect(0, 0, w, h);

  // Background subtle grid
  ctx.strokeStyle = 'rgba(255, 255, 255, 0.05)';
  ctx.lineWidth = 1;
  const gridSize = 20;
  for (let x = 0; x < w; x += gridSize) {
    ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, h); ctx.stroke();
  }
  for (let y = 0; y < h; y += gridSize) {
    ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(w, y); ctx.stroke();
  }

  // Calculate scaling
  const totalD = d1 + d2;
  const maxAllowableW = w * 0.75;
  const scale = Math.min(maxAllowableW / totalD, (h * 0.7) / Math.max(d1, d2));

  const r1 = (d1 / 2) * scale;
  const r2 = (d2 / 2) * scale;

  const cy = h / 2;
  const cx1 = (w / 2) - ((r1 + r2) / 2) + (r1 * 0.3);
  const cx2 = cx1 + r1 + r2;

  // Centerline
  ctx.strokeStyle = 'rgba(56, 189, 248, 0.3)';
  ctx.setLineDash([5, 5]);
  ctx.beginPath();
  ctx.moveTo(cx1 - r1 - 20, cy);
  ctx.lineTo(cx2 + r2 + 20, cy);
  ctx.stroke();
  ctx.setLineDash([]);

  // Pinion Pitch Circle
  ctx.beginPath();
  ctx.arc(cx1, cy, r1, 0, 2 * Math.PI);
  ctx.fillStyle = 'rgba(2, 132, 199, 0.15)';
  ctx.fill();
  ctx.lineWidth = 2;
  ctx.strokeStyle = '#38bdf8';
  ctx.stroke();

  // Pinion Outside Circle
  ctx.beginPath();
  ctx.arc(cx1, cy, r1 + m * scale, 0, 2 * Math.PI);
  ctx.strokeStyle = 'rgba(56, 189, 248, 0.4)';
  ctx.setLineDash([2, 4]);
  ctx.stroke();
  ctx.setLineDash([]);

  // Gear Pitch Circle
  ctx.beginPath();
  ctx.arc(cx2, cy, r2, 0, 2 * Math.PI);
  ctx.fillStyle = 'rgba(147, 51, 234, 0.12)';
  ctx.fill();
  ctx.lineWidth = 2;
  ctx.strokeStyle = '#c084fc';
  ctx.stroke();

  // Gear Outside Circle
  ctx.beginPath();
  ctx.arc(cx2, cy, r2 + m * scale, 0, 2 * Math.PI);
  ctx.strokeStyle = 'rgba(192, 132, 252, 0.4)';
  ctx.setLineDash([2, 4]);
  ctx.stroke();
  ctx.setLineDash([]);

  // Pitch Points & Centers
  [cx1, cx2].forEach((cx, idx) => {
    ctx.beginPath();
    ctx.arc(cx, cy, 3, 0, 2 * Math.PI);
    ctx.fillStyle = idx === 0 ? '#38bdf8' : '#c084fc';
    ctx.fill();
  });

  // Labels
  ctx.font = '11px "JetBrains Mono", monospace';
  ctx.fillStyle = '#94a3b8';
  ctx.textAlign = 'center';
  ctx.fillText(`Pinion d1: ${d1.toFixed(1)} mm`, cx1, cy + r1 + 24);
  ctx.fillText(`Gear d2: ${d2.toFixed(1)} mm`, cx2, cy + r2 + 24);

  // Mesh Point Indicator
  const meshX = cx1 + r1;
  ctx.beginPath();
  ctx.arc(meshX, cy, 4, 0, 2 * Math.PI);
  ctx.fillStyle = '#34d399';
  ctx.fill();
}

function drawSpringSchematic(d, D, Na, Lf) {
  const canvas = document.getElementById('schematic-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  const w = canvas.width;
  const h = canvas.height;

  ctx.clearRect(0, 0, w, h);

  // Grid
  ctx.strokeStyle = 'rgba(255, 255, 255, 0.05)';
  ctx.lineWidth = 1;
  for (let x = 0; x < w; x += 20) {
    ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, h); ctx.stroke();
  }
  for (let y = 0; y < h; y += 20) {
    ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(w, y); ctx.stroke();
  }

  // Scale spring
  const scale = Math.min((w * 0.7) / Lf, (h * 0.5) / D);
  const startX = (w - (Lf * scale)) / 2;
  const cy = h / 2;
  const rCoil = (D / 2) * scale;
  const coils = Math.max(3, Math.min(25, Na));
  const stepX = (Lf * scale) / (coils * 2);

  // Draw helical wave representation
  ctx.beginPath();
  ctx.moveTo(startX, cy);
  for (let i = 0; i <= coils * 2; i++) {
    const x = startX + i * stepX;
    const y = i % 2 === 0 ? cy - rCoil : cy + rCoil;
    ctx.lineTo(x, y);
  }
  ctx.lineWidth = Math.max(2, d * scale * 0.8);
  ctx.strokeStyle = '#38bdf8';
  ctx.lineCap = 'round';
  ctx.lineJoin = 'round';
  ctx.stroke();

  // Dimensions Annotations
  ctx.font = '11px "JetBrains Mono", monospace';
  ctx.fillStyle = '#94a3b8';
  ctx.textAlign = 'center';
  ctx.fillText(`Free Length Lo: ${Lf.toFixed(1)} mm`, w / 2, cy - rCoil - 16);
  ctx.fillText(`Mean Dia D: ${D.toFixed(1)} mm | Wire d: ${d.toFixed(2)} mm`, w / 2, cy + rCoil + 24);
}

// Preset Loader
function applyPreset(type, presetKey) {
  const presets = {
    spur: {
      conveyor: { power: 7.5, speed: 1450, ratio: 2.5, pinion_mat: 'c45_hardened', gear_mat: 'c45_normalised', sf_b: 1.5, sf_c: 1.2, load: 'uniform' },
      automotive: { power: 30.0, speed: 2800, ratio: 3.8, pinion_mat: 'en36_case_hardened', gear_mat: 'c45_hardened', sf_b: 1.8, sf_c: 1.4, load: 'moderate_shock' },
      heavy_mill: { power: 75.0, speed: 980, ratio: 4.5, pinion_mat: '20cr4_alloy', gear_mat: 'en36_case_hardened', sf_b: 2.0, sf_c: 1.5, load: 'heavy_shock' }
    },
    helical: {
      standard: { power: 15.0, speed: 1450, ratio: 4.0, helix: 20.0, pinion_mat: 'c45_hardened', gear_mat: 'c45_normalised' },
      high_speed: { power: 45.0, speed: 3000, ratio: 3.2, helix: 25.0, pinion_mat: 'en36_case_hardened', gear_mat: 'c45_hardened' }
    },
    spring_comp: {
      suspension: { load: 1500, defl: 45, c: 6.0, sf: 1.6, mat: 'chrome_vanadium', end: 'closed_ground' },
      valve: { load: 450, defl: 18, c: 5.5, sf: 1.5, mat: 'music_wire', end: 'closed_ground' },
      general: { load: 250, defl: 25, c: 6.5, sf: 1.4, mat: 'hard_drawn_wire', end: 'closed_ground' }
    },
    spring_tens: {
      standard: { load: 300, defl: 20, c: 6.0, mat: 'chrome_vanadium' },
      precision: { load: 120, defl: 12, c: 5.0, mat: 'music_wire' }
    }
  };

  const p = presets[type]?.[presetKey];
  if (!p) return;

  if (type === 'spur') {
    document.getElementById('spur-power').value = p.power;
    document.getElementById('spur-speed').value = p.speed;
    document.getElementById('spur-ratio').value = p.ratio;
    document.getElementById('spur-mat-pinion').value = p.pinion_mat;
    document.getElementById('spur-mat-gear').value = p.gear_mat;
    document.getElementById('spur-sf-b').value = p.sf_b;
    document.getElementById('spur-sf-c').value = p.sf_c;
    document.getElementById('spur-load').value = p.load;
  } else if (type === 'helical') {
    document.getElementById('hel-power').value = p.power;
    document.getElementById('hel-speed').value = p.speed;
    document.getElementById('hel-ratio').value = p.ratio;
    document.getElementById('hel-helix').value = p.helix;
    document.getElementById('hel-mat-pinion').value = p.pinion_mat;
    document.getElementById('hel-mat-gear').value = p.gear_mat;
  } else if (type === 'spring_comp') {
    document.getElementById('comp-load').value = p.load;
    document.getElementById('comp-defl').value = p.defl;
    document.getElementById('comp-c').value = p.c;
    document.getElementById('comp-sf').value = p.sf;
    document.getElementById('comp-mat').value = p.mat;
    document.getElementById('comp-end').value = p.end;
  } else if (type === 'spring_tens') {
    document.getElementById('tens-load').value = p.load;
    document.getElementById('tens-defl').value = p.defl;
    document.getElementById('tens-c').value = p.c;
    document.getElementById('tens-mat').value = p.mat;
  }
}

// SPUR GEAR CALCULATION
async function calculateSpur(e) {
  e.preventDefault();
  const btn = document.getElementById('btn-spur-submit');
  btn.disabled = true;
  btn.innerHTML = `<svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white inline" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path></svg> Computing AGMA Analysis...`;

  const payload = {
    power_kw: parseFloat(document.getElementById('spur-power').value),
    speed_rpm: parseFloat(document.getElementById('spur-speed').value),
    gear_ratio: parseFloat(document.getElementById('spur-ratio').value),
    min_teeth_pinion: parseInt(document.getElementById('spur-teeth').value),
    pinion_material: document.getElementById('spur-mat-pinion').value,
    gear_material: document.getElementById('spur-mat-gear').value,
    safety_factor_bending: parseFloat(document.getElementById('spur-sf-b').value),
    safety_factor_contact: parseFloat(document.getElementById('spur-sf-c').value),
    load_type: document.getElementById('spur-load').value
  };

  try {
    const res = await fetch('/api/v1/gear/spur', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Calculation failed');

    lastCalculatedData = { type: 'Spur Gear (AGMA 2001-D04)', data };

    document.getElementById('results-placeholder').classList.add('hidden');
    document.getElementById('results-container').classList.remove('hidden');

    const dv = data.design_values;
    const sa = data.stress_analysis;
    const lf = data.loads_and_factors;

    // Status Banner
    const isSafe = data.overall_status === 'PASS';
    const statusBadge = document.getElementById('res-status-badge');
    const statusText = document.getElementById('res-status-text');
    statusText.innerText = isSafe ? 'VERIFIED: SAFE AGMA DESIGN' : 'FAILED SAFETY FACTOR CRITERIA';
    statusBadge.className = isSafe ? 'px-3 py-1 rounded-full text-xs font-bold badge-status-pass' : 'px-3 py-1 rounded-full text-xs font-bold badge-status-fail';
    statusBadge.innerText = data.overall_status;

    // Key Dimension Cards
    document.getElementById('metric-1-label').innerText = 'Standard Module';
    document.getElementById('metric-1-val').innerText = `${dv.module_m} mm`;
    document.getElementById('metric-1-sub').innerText = `Circular Pitch: ${dv.circular_pitch_mm} mm`;

    document.getElementById('metric-2-label').innerText = 'Face Width (F)';
    document.getElementById('metric-2-val').innerText = `${dv.face_width_mm} mm`;
    document.getElementById('metric-2-sub').innerText = `AGMA ratio: ${(dv.face_width_mm / dv.module_m).toFixed(1)}m`;

    document.getElementById('metric-3-label').innerText = 'Pinion Teeth / PCD';
    document.getElementById('metric-3-val').innerText = `${dv.pinion_teeth}T (${dv.pinion_pitch_diameter_mm} mm)`;
    document.getElementById('metric-3-sub').innerText = `Speed: ${data.output_speeds.pinion_speed_rpm} RPM`;

    document.getElementById('metric-4-label').innerText = 'Gear Teeth / PCD';
    document.getElementById('metric-4-val').innerText = `${dv.gear_teeth}T (${dv.gear_pitch_diameter_mm} mm)`;
    document.getElementById('metric-4-sub').innerText = `Center Distance: ${dv.centre_distance_mm} mm`;

    // Stress Meters
    renderStressMeter('bending', sa.bending.pinion_bending_stress_MPa, sa.bending.pinion_allowable_bending_MPa, sa.bending.pinion_bending_SF, 'Bending (Lewis)');
    renderStressMeter('contact', sa.contact.contact_stress_MPa, sa.contact.pinion_allowable_contact_MPa, sa.contact.pinion_contact_SF, 'Surface Contact (Hertz)');

    // Engineering Recommendations
    document.getElementById('res-recommendations').innerText = data.recommendations.join(' ');

    // Detailed Table
    const tableBody = document.getElementById('res-detailed-table');
    tableBody.innerHTML = `
      <tr><td class="py-2 text-slate-400">Tangential Load (Wt)</td><td class="py-2 text-right font-mono font-medium">${lf.tangential_load_Wt_N} N</td></tr>
      <tr><td class="py-2 text-slate-400">Pitch Line Velocity</td><td class="py-2 text-right font-mono font-medium">${lf.pitch_line_velocity_m_s} m/s</td></tr>
      <tr><td class="py-2 text-slate-400">Dynamic Factor (Kv)</td><td class="py-2 text-right font-mono font-medium">${lf.Kv_dynamic_factor}</td></tr>
      <tr><td class="py-2 text-slate-400">Overload Factor (Ko)</td><td class="py-2 text-right font-mono font-medium">${lf.Ko_overload_factor}</td></tr>
      <tr><td class="py-2 text-slate-400">Tooth Addendum / Dedendum</td><td class="py-2 text-right font-mono font-medium">${dv.addendum_mm} mm / ${dv.dedendum_mm} mm</td></tr>
      <tr><td class="py-2 text-slate-400">Outside Diameter (Pinion / Gear)</td><td class="py-2 text-right font-mono font-medium">${dv.outside_dia_pinion_mm} mm / ${dv.outside_dia_gear_mm} mm</td></tr>
    `;

    // Draw Schematic
    drawGearSchematic(dv.pinion_pitch_diameter_mm, dv.gear_pitch_diameter_mm, dv.face_width_mm, dv.module_m);

  } catch (err) {
    alert('Computation Error: ' + err.message);
  } finally {
    btn.disabled = false;
    btn.innerHTML = `Calculate Spur Gear Design`;
  }
}

// HELICAL GEAR CALCULATION
async function calculateHelical(e) {
  e.preventDefault();
  const btn = e.target.querySelector('button[type="submit"]');
  btn.disabled = true;
  btn.innerText = 'Calculating...';

  const payload = {
    power_kw: parseFloat(document.getElementById('hel-power').value),
    speed_rpm: parseFloat(document.getElementById('hel-speed').value),
    gear_ratio: parseFloat(document.getElementById('hel-ratio').value),
    helix_angle_deg: parseFloat(document.getElementById('hel-helix').value),
    pinion_material: document.getElementById('hel-mat-pinion').value,
    gear_material: document.getElementById('hel-mat-gear').value
  };

  try {
    const res = await fetch('/api/v1/gear/helical', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Calculation failed');

    lastCalculatedData = { type: 'Helical Gear (AGMA 2001-D04)', data };

    document.getElementById('results-placeholder').classList.add('hidden');
    document.getElementById('results-container').classList.remove('hidden');

    const dv = data.design_values;
    const sa = data.stress_analysis;

    const isSafe = data.overall_status === 'PASS';
    document.getElementById('res-status-text').innerText = isSafe ? 'VERIFIED: SAFE HELICAL GEAR' : 'FAILED SAFETY LIMITS';
    const statusBadge = document.getElementById('res-status-badge');
    statusBadge.className = isSafe ? 'px-3 py-1 rounded-full text-xs font-bold badge-status-pass' : 'px-3 py-1 rounded-full text-xs font-bold badge-status-fail';
    statusBadge.innerText = data.overall_status;

    document.getElementById('metric-1-label').innerText = 'Normal Module (mn)';
    document.getElementById('metric-1-val').innerText = `${dv.normal_module_mn} mm`;
    document.getElementById('metric-1-sub').innerText = `Transverse mt: ${dv.transverse_module_mt} mm`;

    document.getElementById('metric-2-label').innerText = 'Face Width (F)';
    document.getElementById('metric-2-val').innerText = `${dv.face_width_mm} mm`;
    document.getElementById('metric-2-sub').innerText = `Helix Angle: ${data.inputs.helix_angle_deg}°`;

    document.getElementById('metric-3-label').innerText = 'Pinion Teeth / Virtual';
    document.getElementById('metric-3-val').innerText = `${dv.pinion_teeth}T (Nv: ${dv.virtual_teeth_pinion})`;
    document.getElementById('metric-3-sub').innerText = `PCD: ${dv.pinion_pitch_diameter_mm} mm`;

    document.getElementById('metric-4-label').innerText = 'Gear Teeth / Lead';
    document.getElementById('metric-4-val').innerText = `${dv.gear_teeth}T`;
    document.getElementById('metric-4-sub').innerText = `Lead: ${dv.lead_mm} mm`;

    renderStressMeter('bending', sa.bending.pinion_bending_stress_MPa, 241, sa.bending.pinion_bending_SF, 'Helical Bending');
    renderStressMeter('contact', sa.contact.contact_stress_MPa, 1550, sa.contact.pinion_contact_SF, 'Surface Contact');

    document.getElementById('res-recommendations').innerText = data.recommendations.join(' ');

    const tableBody = document.getElementById('res-detailed-table');
    tableBody.innerHTML = `
      <tr><td class="py-2 text-slate-400">Normal Circular Pitch</td><td class="py-2 text-right font-mono font-medium">${dv.normal_circular_pitch_mm} mm</td></tr>
      <tr><td class="py-2 text-slate-400">Center Distance</td><td class="py-2 text-right font-mono font-medium">${dv.centre_distance_mm} mm</td></tr>
      <tr><td class="py-2 text-slate-400">Outside Diameter (Pinion / Gear)</td><td class="py-2 text-right font-mono font-medium">${dv.outside_dia_pinion_mm} mm / ${dv.outside_dia_gear_mm} mm</td></tr>
    `;

    drawGearSchematic(dv.pinion_pitch_diameter_mm, dv.gear_pitch_diameter_mm, dv.face_width_mm, dv.normal_module_mn);

  } catch (err) {
    alert('Computation Error: ' + err.message);
  } finally {
    btn.disabled = false;
    btn.innerText = 'Calculate Helical Gear Design';
  }
}

// COMPRESSION SPRING CALCULATION
async function calculateCompressionSpring(e) {
  e.preventDefault();
  const btn = e.target.querySelector('button[type="submit"]');
  btn.disabled = true;
  btn.innerText = 'Calculating...';

  const payload = {
    load_N: parseFloat(document.getElementById('comp-load').value),
    deflection_mm: parseFloat(document.getElementById('comp-defl').value),
    spring_index: parseFloat(document.getElementById('comp-c').value),
    safety_factor: parseFloat(document.getElementById('comp-sf').value),
    material: document.getElementById('comp-mat').value,
    end_type: document.getElementById('comp-end').value
  };

  try {
    const res = await fetch('/api/v1/spring/helical-compression', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Calculation failed');

    lastCalculatedData = { type: 'Compression Spring (IS 7907)', data };

    document.getElementById('results-placeholder').classList.add('hidden');
    document.getElementById('results-container').classList.remove('hidden');

    const dv = data.design_values;
    const sa = data.stress_analysis;

    const isSafe = data.overall_status === 'PASS';
    document.getElementById('res-status-text').innerText = isSafe ? 'VERIFIED: SAFE SPRING DESIGN' : 'EXCEEDS ALLOWABLE SHEAR';
    const statusBadge = document.getElementById('res-status-badge');
    statusBadge.className = isSafe ? 'px-3 py-1 rounded-full text-xs font-bold badge-status-pass' : 'px-3 py-1 rounded-full text-xs font-bold badge-status-fail';
    statusBadge.innerText = data.overall_status;

    document.getElementById('metric-1-label').innerText = 'Wire Diameter (d)';
    document.getElementById('metric-1-val').innerText = `${dv.wire_diameter_d_mm} mm`;
    document.getElementById('metric-1-sub').innerText = `IS 4454 Standard Preferred`;

    document.getElementById('metric-2-label').innerText = 'Mean Coil Dia (D)';
    document.getElementById('metric-2-val').innerText = `${dv.mean_coil_diameter_D_mm} mm`;
    document.getElementById('metric-2-sub').innerText = `Outer Dia (OD): ${dv.outer_diameter_OD_mm} mm`;

    document.getElementById('metric-3-label').innerText = 'Active Coils (Na)';
    document.getElementById('metric-3-val').innerText = `${dv.active_coils_Na}`;
    document.getElementById('metric-3-sub').innerText = `Total Coils (Nt): ${dv.total_coils_Nt}`;

    document.getElementById('metric-4-label').innerText = 'Free Length (Lo)';
    document.getElementById('metric-4-val').innerText = `${dv.free_length_Lo_mm} mm`;
    document.getElementById('metric-4-sub').innerText = `Solid Length (Ls): ${dv.solid_length_Ls_mm} mm`;

    renderStressMeter('bending', sa.actual_shear_stress_tau_MPa, sa.allowable_shear_stress_MPa, sa.actual_safety_factor, 'Torsional Shear Stress (Wahl)');
    renderStressMeter('contact', 0, 0, 0, 'N/A (Spring)', true);

    document.getElementById('res-recommendations').innerText = `${data.recommendations.join(' ')} ${data.geometry_checks.buckling_note}`;

    const tableBody = document.getElementById('res-detailed-table');
    tableBody.innerHTML = `
      <tr><td class="py-2 text-slate-400">Spring Stiffness (k)</td><td class="py-2 text-right font-mono font-medium">${dv.spring_rate_k_N_mm} N/mm</td></tr>
      <tr><td class="py-2 text-slate-400">Wahl Correction Factor (K)</td><td class="py-2 text-right font-mono font-medium">${dv.Wahl_correction_K}</td></tr>
      <tr><td class="py-2 text-slate-400">Spring Index (C = D/d)</td><td class="py-2 text-right font-mono font-medium">${dv.spring_index_C}</td></tr>
      <tr><td class="py-2 text-slate-400">Working Length (Lw)</td><td class="py-2 text-right font-mono font-medium">${dv.working_length_Lw_mm} mm</td></tr>
      <tr><td class="py-2 text-slate-400">Clash Allowance</td><td class="py-2 text-right font-mono font-medium">${dv.clash_allowance_mm} mm</td></tr>
      <tr><td class="py-2 text-slate-400">Approximate Weight</td><td class="py-2 text-right font-mono font-medium">${data.misc.approximate_weight_N} N</td></tr>
    `;

    drawSpringSchematic(dv.wire_diameter_d_mm, dv.mean_coil_diameter_D_mm, dv.active_coils_Na, dv.free_length_Lo_mm);

  } catch (err) {
    alert('Computation Error: ' + err.message);
  } finally {
    btn.disabled = false;
    btn.innerText = 'Calculate Spring Parameters';
  }
}

// TENSION SPRING CALCULATION
async function calculateTensionSpring(e) {
  e.preventDefault();
  const btn = e.target.querySelector('button[type="submit"]');
  btn.disabled = true;
  btn.innerText = 'Calculating...';

  const payload = {
    load_N: parseFloat(document.getElementById('tens-load').value),
    deflection_mm: parseFloat(document.getElementById('tens-defl').value),
    spring_index: parseFloat(document.getElementById('tens-c').value),
    material: document.getElementById('tens-mat').value
  };

  try {
    const res = await fetch('/api/v1/spring/helical-tension', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Calculation failed');

    lastCalculatedData = { type: 'Tension Spring (IS 7907)', data };

    document.getElementById('results-placeholder').classList.add('hidden');
    document.getElementById('results-container').classList.remove('hidden');

    const dv = data.design_values;
    const sa = data.stress_analysis;

    const isSafe = data.overall_status === 'PASS';
    document.getElementById('res-status-text').innerText = isSafe ? 'VERIFIED: SAFE TENSION SPRING' : 'FAILED HOOK OR BODY STRESS';
    const statusBadge = document.getElementById('res-status-badge');
    statusBadge.className = isSafe ? 'px-3 py-1 rounded-full text-xs font-bold badge-status-pass' : 'px-3 py-1 rounded-full text-xs font-bold badge-status-fail';
    statusBadge.innerText = data.overall_status;

    document.getElementById('metric-1-label').innerText = 'Wire Diameter (d)';
    document.getElementById('metric-1-val').innerText = `${dv.wire_diameter_d_mm} mm`;
    document.getElementById('metric-1-sub').innerText = `Spring Index C: ${dv.spring_index_C}`;

    document.getElementById('metric-2-label').innerText = 'Mean Coil Dia (D)';
    document.getElementById('metric-2-val').innerText = `${dv.mean_coil_diameter_D_mm} mm`;
    document.getElementById('metric-2-sub').innerText = `Outer Dia: ${dv.outer_diameter_OD_mm} mm`;

    document.getElementById('metric-3-label').innerText = 'Active Coils (Na)';
    document.getElementById('metric-3-val').innerText = `${dv.active_coils_Na}`;
    document.getElementById('metric-3-sub').innerText = `Body Length: ${dv.body_length_Lb_mm} mm`;

    document.getElementById('metric-4-label').innerText = 'Extended Length';
    document.getElementById('metric-4-val').innerText = `${dv.extended_length_mm} mm`;
    document.getElementById('metric-4-sub').innerText = `Hook Status: ${sa.hook_status}`;

    renderStressMeter('bending', sa.body_shear_stress_tau_MPa, sa.allowable_shear_stress_MPa, sa.actual_safety_factor, 'Body Shear Stress');
    renderStressMeter('contact', sa.hook_bending_stress_MPa, sa.hook_allowable_stress_MPa, (sa.hook_allowable_stress_MPa / sa.hook_bending_stress_MPa).toFixed(2), 'Hook Bending (Bergstraesser)');

    document.getElementById('res-recommendations').innerText = data.recommendations.join(' ');

    const tableBody = document.getElementById('res-detailed-table');
    tableBody.innerHTML = `
      <tr><td class="py-2 text-slate-400">Spring Stiffness (k)</td><td class="py-2 text-right font-mono font-medium">${dv.spring_rate_k_N_mm} N/mm</td></tr>
      <tr><td class="py-2 text-slate-400">Wahl Factor (K)</td><td class="py-2 text-right font-mono font-medium">${dv.Wahl_correction_K}</td></tr>
      <tr><td class="py-2 text-slate-400">Hook Shear Allowable</td><td class="py-2 text-right font-mono font-medium">${sa.hook_allowable_stress_MPa} MPa</td></tr>
    `;

    drawSpringSchematic(dv.wire_diameter_d_mm, dv.mean_coil_diameter_D_mm, dv.active_coils_Na, dv.body_length_Lb_mm);

  } catch (err) {
    alert('Computation Error: ' + err.message);
  } finally {
    btn.disabled = false;
    btn.innerText = 'Calculate Tension Spring';
  }
}

// Stress Meter Renderer
function renderStressMeter(id, actual, allow, sf, label, hide = false) {
  const container = document.getElementById(`stress-meter-${id}`);
  if (!container) return;
  if (hide) {
    container.classList.add('hidden');
    return;
  }
  container.classList.remove('hidden');

  const pct = Math.min(100, Math.max(5, (actual / allow) * 100));
  const isOk = actual <= allow;
  const barColor = isOk ? 'bg-emerald-500' : 'bg-red-500';

  container.innerHTML = `
    <div class="flex justify-between items-center mb-1">
      <span class="font-medium text-slate-300">${label}</span>
      <span class="font-mono text-xs ${isOk ? 'text-emerald-400' : 'text-red-400'} font-semibold">SF: ${sf}</span>
    </div>
    <div class="w-full bg-slate-800 rounded-full h-2.5 overflow-hidden border border-slate-700">
      <div class="${barColor} h-2.5 rounded-full transition-all duration-500" style="width: ${pct}%"></div>
    </div>
    <div class="flex justify-between text-[11px] text-slate-400 mt-1 font-mono">
      <span>Induced: ${actual} MPa</span>
      <span>Allowable: ${allow} MPa</span>
    </div>
  `;
}

// Materials Loader
async function loadMaterialsCatalog() {
  try {
    const [resG, resS] = await Promise.all([
      fetch('/api/v1/gear/materials'),
      fetch('/api/v1/spring/materials')
    ]);
    const dataG = await resG.json();
    const dataS = await resS.json();

    const gTable = document.getElementById('mat-gear-table');
    if (gTable) {
      gTable.innerHTML = '';
      for (const [k, v] of Object.entries(dataG.materials)) {
        gTable.innerHTML += `
          <tr class="hover:bg-slate-800/50 border-b border-slate-800 transition">
            <td class="p-3 font-semibold text-sky-400">${v.name}</td>
            <td class="p-3 font-mono">${v.Sut_MPa} MPa</td>
            <td class="p-3 font-mono">${v.Sy_MPa} MPa</td>
            <td class="p-3 font-mono">${v.BHN}</td>
            <td class="p-3 font-mono text-emerald-400">${v.Sat_MPa} MPa</td>
            <td class="p-3 font-mono text-purple-400">${v.Sac_MPa} MPa</td>
            <td class="p-3 text-slate-400 text-xs">${v.description}</td>
          </tr>`;
      }
    }

    const sTable = document.getElementById('mat-spring-table');
    if (sTable) {
      sTable.innerHTML = '';
      for (const [k, v] of Object.entries(dataS.materials)) {
        sTable.innerHTML += `
          <tr class="hover:bg-slate-800/50 border-b border-slate-800 transition">
            <td class="p-3 font-semibold text-sky-400">${v.name}</td>
            <td class="p-3 font-mono">${v.shear_modulus_G_GPa} GPa</td>
            <td class="p-3 font-mono">${v.elastic_modulus_E_GPa} GPa</td>
            <td class="p-3 font-mono">${v.max_service_temp_C} °C</td>
            <td class="p-3 text-slate-400 text-xs">${v.description}</td>
          </tr>`;
      }
    }
  } catch (err) {
    console.error('Failed loading materials:', err);
  }
}

// Copy JSON Result
function copyResultsJSON() {
  if (!lastCalculatedData) {
    alert('Please calculate a component first.');
    return;
  }
  navigator.clipboard.writeText(JSON.stringify(lastCalculatedData, null, 2))
    .then(() => alert('Results JSON copied to clipboard!'))
    .catch(() => alert('Could not copy to clipboard.'));
}
