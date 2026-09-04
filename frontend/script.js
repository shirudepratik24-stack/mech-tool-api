// MechEngine — Professional Light Theme JavaScript Engine
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

  // Show/hide materials view
  const matView = document.getElementById('materials-view');
  const resPlaceholder = document.getElementById('results-placeholder');
  const resContainer = document.getElementById('results-container');

  if (tabId === 'materials') {
    if (matView) matView.classList.remove('hidden');
    if (resPlaceholder) resPlaceholder.classList.add('hidden');
    if (resContainer) resContainer.classList.add('hidden');
    loadMaterialsCatalog();
  } else {
    if (matView) matView.classList.add('hidden');
    if (!lastCalculatedData) {
      if (resPlaceholder) resPlaceholder.classList.remove('hidden');
      if (resContainer) resContainer.classList.add('hidden');
    }
  }
}

// 2D Gear Schematic — Light Theme
function drawGearSchematic(d1, d2, F, m) {
  const canvas = document.getElementById('schematic-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  const w = canvas.width, h = canvas.height;

  ctx.clearRect(0, 0, w, h);

  // Light grid
  ctx.strokeStyle = '#e2e8f0';
  ctx.lineWidth = 0.5;
  for (let x = 0; x < w; x += 20) { ctx.beginPath(); ctx.moveTo(x,0); ctx.lineTo(x,h); ctx.stroke(); }
  for (let y = 0; y < h; y += 20) { ctx.beginPath(); ctx.moveTo(0,y); ctx.lineTo(w,y); ctx.stroke(); }

  const totalD = d1 + d2;
  const maxW = w * 0.75;
  const scale = Math.min(maxW / totalD, (h * 0.7) / Math.max(d1, d2));
  const r1 = (d1 / 2) * scale, r2 = (d2 / 2) * scale;
  const cy = h / 2;
  const cx1 = (w / 2) - ((r1 + r2) / 2) + (r1 * 0.3);
  const cx2 = cx1 + r1 + r2;

  // Centerline
  ctx.strokeStyle = '#94a3b8';
  ctx.setLineDash([6, 4]);
  ctx.lineWidth = 1;
  ctx.beginPath(); ctx.moveTo(cx1 - r1 - 20, cy); ctx.lineTo(cx2 + r2 + 20, cy); ctx.stroke();
  ctx.setLineDash([]);

  // Pinion pitch circle
  ctx.beginPath(); ctx.arc(cx1, cy, r1, 0, 2 * Math.PI);
  ctx.fillStyle = 'rgba(37, 99, 235, 0.08)';
  ctx.fill();
  ctx.lineWidth = 2; ctx.strokeStyle = '#2563eb'; ctx.stroke();

  // Pinion outside circle
  ctx.beginPath(); ctx.arc(cx1, cy, r1 + m * scale, 0, 2 * Math.PI);
  ctx.strokeStyle = 'rgba(37, 99, 235, 0.3)'; ctx.setLineDash([3, 4]); ctx.lineWidth = 1; ctx.stroke();
  ctx.setLineDash([]);

  // Gear pitch circle
  ctx.beginPath(); ctx.arc(cx2, cy, r2, 0, 2 * Math.PI);
  ctx.fillStyle = 'rgba(124, 58, 237, 0.06)';
  ctx.fill();
  ctx.lineWidth = 2; ctx.strokeStyle = '#7c3aed'; ctx.stroke();

  // Gear outside circle
  ctx.beginPath(); ctx.arc(cx2, cy, r2 + m * scale, 0, 2 * Math.PI);
  ctx.strokeStyle = 'rgba(124, 58, 237, 0.3)'; ctx.setLineDash([3, 4]); ctx.lineWidth = 1; ctx.stroke();
  ctx.setLineDash([]);

  // Centers
  [cx1, cx2].forEach((cx, i) => {
    ctx.beginPath(); ctx.arc(cx, cy, 3, 0, 2 * Math.PI);
    ctx.fillStyle = i === 0 ? '#2563eb' : '#7c3aed'; ctx.fill();
  });

  // Labels
  ctx.font = '11px "JetBrains Mono", monospace';
  ctx.fillStyle = '#64748b'; ctx.textAlign = 'center';
  ctx.fillText(`Pinion: ${d1.toFixed(1)} mm`, cx1, cy + r1 + 22);
  ctx.fillText(`Gear: ${d2.toFixed(1)} mm`, cx2, cy + r2 + 22);

  // Mesh point
  ctx.beginPath(); ctx.arc(cx1 + r1, cy, 4, 0, 2 * Math.PI);
  ctx.fillStyle = '#059669'; ctx.fill();
}

// 2D Spring Schematic — Light Theme
function drawSpringSchematic(d, D, Na, Lf) {
  const canvas = document.getElementById('schematic-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  const w = canvas.width, h = canvas.height;

  ctx.clearRect(0, 0, w, h);

  ctx.strokeStyle = '#e2e8f0'; ctx.lineWidth = 0.5;
  for (let x = 0; x < w; x += 20) { ctx.beginPath(); ctx.moveTo(x,0); ctx.lineTo(x,h); ctx.stroke(); }
  for (let y = 0; y < h; y += 20) { ctx.beginPath(); ctx.moveTo(0,y); ctx.lineTo(w,y); ctx.stroke(); }

  const scale = Math.min((w * 0.7) / Lf, (h * 0.5) / D);
  const startX = (w - (Lf * scale)) / 2;
  const cy = h / 2;
  const rCoil = (D / 2) * scale;
  const coils = Math.max(3, Math.min(25, Na));
  const stepX = (Lf * scale) / (coils * 2);

  ctx.beginPath(); ctx.moveTo(startX, cy);
  for (let i = 0; i <= coils * 2; i++) {
    const x = startX + i * stepX;
    const y = i % 2 === 0 ? cy - rCoil : cy + rCoil;
    ctx.lineTo(x, y);
  }
  ctx.lineWidth = Math.max(2, d * scale * 0.8);
  ctx.strokeStyle = '#2563eb'; ctx.lineCap = 'round'; ctx.lineJoin = 'round'; ctx.stroke();

  ctx.font = '11px "JetBrains Mono", monospace';
  ctx.fillStyle = '#64748b'; ctx.textAlign = 'center';
  ctx.fillText(`Free Length: ${Lf.toFixed(1)} mm`, w / 2, cy - rCoil - 14);
  ctx.fillText(`Mean Dia: ${D.toFixed(1)} mm | Wire: ${d.toFixed(2)} mm`, w / 2, cy + rCoil + 22);
}

// Preset Loader
function applyPreset(type, presetKey) {
  const presets = {
    spur: {
      conveyor: { power: 7.5, speed: 1450, ratio: 2.5, pinion_mat: 'c45_hardened', gear_mat: 'c45_normalised', sf_b: 1.5, sf_c: 1.2, load: 'uniform' },
      automotive: { power: 30.0, speed: 2800, ratio: 3.8, pinion_mat: 'en36_case_hardened', gear_mat: 'c45_hardened', sf_b: 1.8, sf_c: 1.4, load: 'moderate_shock' }
    },
    helical: {
      standard: { power: 15.0, speed: 1450, ratio: 4.0, helix: 20.0, pinion_mat: 'c45_hardened', gear_mat: 'c45_normalised' },
      high_speed: { power: 45.0, speed: 3000, ratio: 3.2, helix: 25.0, pinion_mat: 'en36_case_hardened', gear_mat: 'c45_hardened' }
    },
    spring_comp: {
      suspension: { load: 1500, defl: 45, c: 6.0, sf: 1.6, mat: 'chrome_vanadium', end: 'closed_ground' },
      general: { load: 250, defl: 25, c: 6.5, sf: 1.4, mat: 'hard_drawn_wire', end: 'closed_ground' }
    },
    spring_tens: {
      standard: { load: 300, defl: 20, c: 6.0, mat: 'chrome_vanadium' }
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

// SPUR GEAR
async function calculateSpur(e) {
  e.preventDefault();
  const btn = document.getElementById('btn-spur-submit');
  btn.disabled = true;
  btn.innerHTML = '<svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white inline" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path></svg>Computing...';

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
    const res = await fetch('/api/v1/gear/spur', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(payload) });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Calculation failed');
    lastCalculatedData = { type: 'Spur Gear (AGMA)', data };

    document.getElementById('results-placeholder').classList.add('hidden');
    document.getElementById('results-container').classList.remove('hidden');

    const dv = data.design_values, sa = data.stress_analysis, lf = data.loads_and_factors;
    const isSafe = data.overall_status === 'PASS';
    document.getElementById('res-status-text').innerText = isSafe ? 'VERIFIED: SAFE AGMA DESIGN' : 'FAILED SAFETY CRITERIA';
    const badge = document.getElementById('res-status-badge');
    badge.className = 'px-3.5 py-1.5 rounded-full text-xs font-bold uppercase tracking-wider ' + (isSafe ? 'badge-pass' : 'badge-fail');
    badge.innerText = data.overall_status;

    setMetric(1, 'Standard Module', `${dv.module_m} mm`, `Pitch: ${dv.circular_pitch_mm} mm`);
    setMetric(2, 'Face Width', `${dv.face_width_mm} mm`, `Ratio: ${(dv.face_width_mm/dv.module_m).toFixed(1)}m`);
    setMetric(3, 'Pinion', `${dv.pinion_teeth}T · ${dv.pinion_pitch_diameter_mm} mm`, `${data.output_speeds.pinion_speed_rpm} RPM`);
    setMetric(4, 'Gear', `${dv.gear_teeth}T · ${dv.gear_pitch_diameter_mm} mm`, `Center: ${dv.centre_distance_mm} mm`);

    renderStressMeter('bending', sa.bending.pinion_bending_stress_MPa, sa.bending.pinion_allowable_bending_MPa, sa.bending.pinion_bending_SF, 'Bending (Lewis)');
    renderStressMeter('contact', sa.contact.contact_stress_MPa, sa.contact.pinion_allowable_contact_MPa, sa.contact.pinion_contact_SF, 'Contact (Hertz)');

    document.getElementById('res-recommendations').innerText = data.recommendations.join(' ');
    document.getElementById('res-detailed-table').innerHTML = detailRow('Tangential Load', `${lf.tangential_load_Wt_N} N`) + detailRow('Pitch Velocity', `${lf.pitch_line_velocity_m_s} m/s`) + detailRow('Dynamic Factor Kv', lf.Kv_dynamic_factor) + detailRow('Overload Factor Ko', lf.Ko_overload_factor) + detailRow('Addendum / Dedendum', `${dv.addendum_mm} / ${dv.dedendum_mm} mm`) + detailRow('Outside Dia (P/G)', `${dv.outside_dia_pinion_mm} / ${dv.outside_dia_gear_mm} mm`);

    drawGearSchematic(dv.pinion_pitch_diameter_mm, dv.gear_pitch_diameter_mm, dv.face_width_mm, dv.module_m);
  } catch (err) { alert('Error: ' + err.message); }
  finally { btn.disabled = false; btn.innerHTML = 'Calculate Spur Gear Design'; }
}

// HELICAL GEAR
async function calculateHelical(e) {
  e.preventDefault();
  const btn = e.target.querySelector('button[type="submit"]');
  btn.disabled = true; btn.innerText = 'Calculating...';

  const payload = {
    power_kw: parseFloat(document.getElementById('hel-power').value),
    speed_rpm: parseFloat(document.getElementById('hel-speed').value),
    gear_ratio: parseFloat(document.getElementById('hel-ratio').value),
    helix_angle_deg: parseFloat(document.getElementById('hel-helix').value),
    pinion_material: document.getElementById('hel-mat-pinion').value,
    gear_material: document.getElementById('hel-mat-gear').value
  };

  try {
    const res = await fetch('/api/v1/gear/helical', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(payload) });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Calculation failed');
    lastCalculatedData = { type: 'Helical Gear (AGMA)', data };

    document.getElementById('results-placeholder').classList.add('hidden');
    document.getElementById('results-container').classList.remove('hidden');

    const dv = data.design_values, sa = data.stress_analysis;
    const isSafe = data.overall_status === 'PASS';
    document.getElementById('res-status-text').innerText = isSafe ? 'VERIFIED: SAFE HELICAL DESIGN' : 'FAILED SAFETY LIMITS';
    const badge = document.getElementById('res-status-badge');
    badge.className = 'px-3.5 py-1.5 rounded-full text-xs font-bold uppercase tracking-wider ' + (isSafe ? 'badge-pass' : 'badge-fail');
    badge.innerText = data.overall_status;

    setMetric(1, 'Normal Module', `${dv.normal_module_mn} mm`, `mt: ${dv.transverse_module_mt} mm`);
    setMetric(2, 'Face Width', `${dv.face_width_mm} mm`, `Helix: ${data.inputs.helix_angle_deg}°`);
    setMetric(3, 'Pinion', `${dv.pinion_teeth}T (Nv:${dv.virtual_teeth_pinion})`, `PCD: ${dv.pinion_pitch_diameter_mm} mm`);
    setMetric(4, 'Gear / Lead', `${dv.gear_teeth}T`, `Lead: ${dv.lead_mm} mm`);

    renderStressMeter('bending', sa.bending.pinion_bending_stress_MPa, 241, sa.bending.pinion_bending_SF, 'Helical Bending');
    renderStressMeter('contact', sa.contact.contact_stress_MPa, 1550, sa.contact.pinion_contact_SF, 'Surface Contact');

    document.getElementById('res-recommendations').innerText = data.recommendations.join(' ');
    document.getElementById('res-detailed-table').innerHTML = detailRow('Normal Pitch', `${dv.normal_circular_pitch_mm} mm`) + detailRow('Center Distance', `${dv.centre_distance_mm} mm`) + detailRow('Outside Dia (P/G)', `${dv.outside_dia_pinion_mm} / ${dv.outside_dia_gear_mm} mm`);

    drawGearSchematic(dv.pinion_pitch_diameter_mm, dv.gear_pitch_diameter_mm, dv.face_width_mm, dv.normal_module_mn);
  } catch (err) { alert('Error: ' + err.message); }
  finally { btn.disabled = false; btn.innerText = 'Calculate Helical Gear Design'; }
}

// COMPRESSION SPRING
async function calculateCompressionSpring(e) {
  e.preventDefault();
  const btn = e.target.querySelector('button[type="submit"]');
  btn.disabled = true; btn.innerText = 'Calculating...';

  const payload = {
    load_N: parseFloat(document.getElementById('comp-load').value),
    deflection_mm: parseFloat(document.getElementById('comp-defl').value),
    spring_index: parseFloat(document.getElementById('comp-c').value),
    safety_factor: parseFloat(document.getElementById('comp-sf').value),
    material: document.getElementById('comp-mat').value,
    end_type: document.getElementById('comp-end').value
  };

  try {
    const res = await fetch('/api/v1/spring/helical-compression', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(payload) });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Calculation failed');
    lastCalculatedData = { type: 'Compression Spring (IS 7907)', data };

    document.getElementById('results-placeholder').classList.add('hidden');
    document.getElementById('results-container').classList.remove('hidden');

    const dv = data.design_values, sa = data.stress_analysis;
    const isSafe = data.overall_status === 'PASS';
    document.getElementById('res-status-text').innerText = isSafe ? 'VERIFIED: SAFE SPRING DESIGN' : 'EXCEEDS ALLOWABLE SHEAR';
    const badge = document.getElementById('res-status-badge');
    badge.className = 'px-3.5 py-1.5 rounded-full text-xs font-bold uppercase tracking-wider ' + (isSafe ? 'badge-pass' : 'badge-fail');
    badge.innerText = data.overall_status;

    setMetric(1, 'Wire Dia (d)', `${dv.wire_diameter_d_mm} mm`, 'IS 4454 Standard');
    setMetric(2, 'Mean Coil (D)', `${dv.mean_coil_diameter_D_mm} mm`, `OD: ${dv.outer_diameter_OD_mm} mm`);
    setMetric(3, 'Active Coils', `${dv.active_coils_Na}`, `Total: ${dv.total_coils_Nt}`);
    setMetric(4, 'Free Length', `${dv.free_length_Lo_mm} mm`, `Solid: ${dv.solid_length_Ls_mm} mm`);

    renderStressMeter('bending', sa.actual_shear_stress_tau_MPa, sa.allowable_shear_stress_MPa, sa.actual_safety_factor, 'Shear Stress (Wahl)');
    renderStressMeter('contact', 0, 0, 0, 'N/A', true);

    document.getElementById('res-recommendations').innerText = `${data.recommendations.join(' ')} ${data.geometry_checks.buckling_note}`;
    document.getElementById('res-detailed-table').innerHTML = detailRow('Spring Rate (k)', `${dv.spring_rate_k_N_mm} N/mm`) + detailRow('Wahl Factor (K)', dv.Wahl_correction_K) + detailRow('Spring Index (C)', dv.spring_index_C) + detailRow('Working Length', `${dv.working_length_Lw_mm} mm`) + detailRow('Clash Allowance', `${dv.clash_allowance_mm} mm`) + detailRow('Approx Weight', `${data.misc.approximate_weight_N} N`);

    drawSpringSchematic(dv.wire_diameter_d_mm, dv.mean_coil_diameter_D_mm, dv.active_coils_Na, dv.free_length_Lo_mm);
  } catch (err) { alert('Error: ' + err.message); }
  finally { btn.disabled = false; btn.innerText = 'Calculate Spring Parameters'; }
}

// TENSION SPRING
async function calculateTensionSpring(e) {
  e.preventDefault();
  const btn = e.target.querySelector('button[type="submit"]');
  btn.disabled = true; btn.innerText = 'Calculating...';

  const payload = {
    load_N: parseFloat(document.getElementById('tens-load').value),
    deflection_mm: parseFloat(document.getElementById('tens-defl').value),
    spring_index: parseFloat(document.getElementById('tens-c').value),
    material: document.getElementById('tens-mat').value
  };

  try {
    const res = await fetch('/api/v1/spring/helical-tension', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(payload) });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Calculation failed');
    lastCalculatedData = { type: 'Tension Spring (IS 7907)', data };

    document.getElementById('results-placeholder').classList.add('hidden');
    document.getElementById('results-container').classList.remove('hidden');

    const dv = data.design_values, sa = data.stress_analysis;
    const isSafe = data.overall_status === 'PASS';
    document.getElementById('res-status-text').innerText = isSafe ? 'VERIFIED: SAFE TENSION SPRING' : 'FAILED HOOK/BODY STRESS';
    const badge = document.getElementById('res-status-badge');
    badge.className = 'px-3.5 py-1.5 rounded-full text-xs font-bold uppercase tracking-wider ' + (isSafe ? 'badge-pass' : 'badge-fail');
    badge.innerText = data.overall_status;

    setMetric(1, 'Wire Dia (d)', `${dv.wire_diameter_d_mm} mm`, `Index C: ${dv.spring_index_C}`);
    setMetric(2, 'Mean Coil (D)', `${dv.mean_coil_diameter_D_mm} mm`, `OD: ${dv.outer_diameter_OD_mm} mm`);
    setMetric(3, 'Active Coils', `${dv.active_coils_Na}`, `Body: ${dv.body_length_Lb_mm} mm`);
    setMetric(4, 'Extended Len', `${dv.extended_length_mm} mm`, `Hook: ${sa.hook_status}`);

    renderStressMeter('bending', sa.body_shear_stress_tau_MPa, sa.allowable_shear_stress_MPa, sa.actual_safety_factor, 'Body Shear');
    renderStressMeter('contact', sa.hook_bending_stress_MPa, sa.hook_allowable_stress_MPa, (sa.hook_allowable_stress_MPa / sa.hook_bending_stress_MPa).toFixed(2), 'Hook Bending');

    document.getElementById('res-recommendations').innerText = data.recommendations.join(' ');
    document.getElementById('res-detailed-table').innerHTML = detailRow('Spring Rate (k)', `${dv.spring_rate_k_N_mm} N/mm`) + detailRow('Wahl Factor (K)', dv.Wahl_correction_K) + detailRow('Hook Allowable', `${sa.hook_allowable_stress_MPa} MPa`);

    drawSpringSchematic(dv.wire_diameter_d_mm, dv.mean_coil_diameter_D_mm, dv.active_coils_Na, dv.body_length_Lb_mm);
  } catch (err) { alert('Error: ' + err.message); }
  finally { btn.disabled = false; btn.innerText = 'Calculate Tension Spring'; }
}

// Helpers
function setMetric(n, label, val, sub) {
  document.getElementById(`metric-${n}-label`).innerText = label;
  document.getElementById(`metric-${n}-val`).innerText = val;
  document.getElementById(`metric-${n}-sub`).innerText = sub;
}

function detailRow(label, value) {
  return `<tr><td class="py-2.5 text-gray-500 font-medium">${label}</td><td class="py-2.5 text-right font-mono font-semibold text-gray-800">${value}</td></tr>`;
}

// Stress Meter — Light Theme
function renderStressMeter(id, actual, allow, sf, label, hide = false) {
  const container = document.getElementById(`stress-meter-${id}`);
  if (!container) return;
  if (hide) { container.classList.add('hidden'); return; }
  container.classList.remove('hidden');

  const pct = Math.min(100, Math.max(5, (actual / allow) * 100));
  const isOk = actual <= allow;
  const fillClass = isOk ? 'meter-bar-fill-ok' : 'meter-bar-fill-fail';

  container.innerHTML = `
    <div class="flex justify-between items-center mb-1.5">
      <span class="font-semibold text-gray-700 text-xs">${label}</span>
      <span class="font-mono text-xs ${isOk ? 'text-emerald-600' : 'text-red-600'} font-bold">SF: ${sf}</span>
    </div>
    <div class="meter-bar-bg">
      <div class="${fillClass}" style="width: ${pct}%"></div>
    </div>
    <div class="flex justify-between text-[11px] text-gray-400 mt-1.5 font-mono">
      <span>Induced: ${actual} MPa</span>
      <span>Allowable: ${allow} MPa</span>
    </div>
  `;
}

// Materials Loader
async function loadMaterialsCatalog() {
  try {
    const [resG, resS] = await Promise.all([fetch('/api/v1/gear/materials'), fetch('/api/v1/spring/materials')]);
    const dataG = await resG.json(), dataS = await resS.json();

    const gTable = document.getElementById('mat-gear-table');
    if (gTable) {
      gTable.innerHTML = '';
      for (const [k, v] of Object.entries(dataG.materials)) {
        gTable.innerHTML += `<tr class="hover:bg-blue-50/50 border-b border-gray-100 transition">
          <td class="p-3 font-semibold text-gray-800">${v.name}</td>
          <td class="p-3 font-mono text-gray-600">${v.Sut_MPa}</td>
          <td class="p-3 font-mono text-gray-600">${v.Sy_MPa}</td>
          <td class="p-3 font-mono text-gray-600">${v.BHN}</td>
          <td class="p-3 font-mono text-emerald-600 font-semibold">${v.Sat_MPa}</td>
          <td class="p-3 font-mono text-violet-600 font-semibold">${v.Sac_MPa}</td>
          <td class="p-3 text-gray-400 text-[11px]">${v.description}</td>
        </tr>`;
      }
    }

    const sTable = document.getElementById('mat-spring-table');
    if (sTable) {
      sTable.innerHTML = '';
      for (const [k, v] of Object.entries(dataS.materials)) {
        sTable.innerHTML += `<tr class="hover:bg-blue-50/50 border-b border-gray-100 transition">
          <td class="p-3 font-semibold text-gray-800">${v.name}</td>
          <td class="p-3 font-mono text-gray-600">${v.shear_modulus_G_GPa} GPa</td>
          <td class="p-3 font-mono text-gray-600">${v.elastic_modulus_E_GPa} GPa</td>
          <td class="p-3 font-mono text-gray-600">${v.max_service_temp_C} °C</td>
          <td class="p-3 text-gray-400 text-[11px]">${v.description}</td>
        </tr>`;
      }
    }
  } catch (err) { console.error('Materials load error:', err); }
}

// Copy JSON
function copyResultsJSON() {
  if (!lastCalculatedData) { alert('Calculate a component first.'); return; }
  navigator.clipboard.writeText(JSON.stringify(lastCalculatedData, null, 2))
    .then(() => alert('JSON copied to clipboard!'))
    .catch(() => alert('Copy failed.'));
}

// PDF Report Generator (Interactive jsPDF)
function downloadPDF() {
  if (!lastCalculatedData || !lastCalculatedData.data) {
    alert('Please calculate a component first before downloading the PDF report.');
    return;
  }

  if (!window.jspdf || !window.jspdf.jsPDF) {
    alert('PDF library is loading. Please check your internet connection and try again in a few seconds.');
    return;
  }

  try {
    const { jsPDF } = window.jspdf;
    const doc = new jsPDF({ orientation: 'p', unit: 'mm', format: 'a4' });
    const pageWidth = doc.internal.pageSize.getWidth();
    const margin = 14;
    let y = 16;

    const compType = lastCalculatedData.type || 'Mechanical Component';
    const data = lastCalculatedData.data;
    const isPass = data.overall_status === 'PASS';

    // 1. Header Banner
    doc.setFillColor(37, 99, 235);
    doc.rect(0, 0, pageWidth, 24, 'F');

    doc.setFont('helvetica', 'bold');
    doc.setFontSize(14);
    doc.setTextColor(255, 255, 255);
    doc.text('MechEngine CAD — Mechanical Design Report', margin, 11);

    doc.setFont('helvetica', 'normal');
    doc.setFontSize(8.5);
    doc.setTextColor(220, 235, 255);
    doc.text(`Standard: ${data.standard || 'AGMA / IS 7907'} | Generated: ${new Date().toLocaleString()}`, margin, 18);

    y = 32;

    // 2. Component Title & Status Badge
    doc.setFont('helvetica', 'bold');
    doc.setFontSize(13);
    doc.setTextColor(15, 23, 42);
    doc.text(compType.toUpperCase(), margin, y);

    const statusText = isPass ? 'STATUS: PASS (SAFE)' : 'STATUS: FAIL (EXCEEDED)';
    doc.setFontSize(9.5);
    const badgeWidth = doc.getTextWidth(statusText) + 8;
    const badgeX = pageWidth - margin - badgeWidth;
    if (isPass) {
      doc.setFillColor(236, 253, 245);
      doc.setDrawColor(5, 150, 105);
      doc.setTextColor(5, 150, 105);
    } else {
      doc.setFillColor(254, 242, 242);
      doc.setDrawColor(220, 38, 38);
      doc.setTextColor(220, 38, 38);
    }
    doc.roundedRect(badgeX, y - 5.5, badgeWidth, 7.5, 1.5, 1.5, 'FD');
    doc.text(statusText, badgeX + 4, y - 0.5);

    y += 8;

    // 3. 2D Canvas Schematic Image
    const canvas = document.getElementById('schematic-canvas');
    if (canvas) {
      try {
        const canvasImg = canvas.toDataURL('image/png');
        const imgWidth = pageWidth - (margin * 2);
        const imgHeight = (canvas.height / canvas.width) * imgWidth;
        doc.setDrawColor(226, 232, 240);
        doc.setFillColor(248, 250, 252);
        doc.roundedRect(margin, y, imgWidth, imgHeight, 2, 2, 'FD');
        doc.addImage(canvasImg, 'PNG', margin, y, imgWidth, imgHeight);
        y += imgHeight + 8;
      } catch (err) {
        console.warn('Canvas image embed note:', err);
      }
    }

    function printSectionTitle(title) {
      if (y > 265) { doc.addPage(); y = 16; }
      doc.setFont('helvetica', 'bold');
      doc.setFontSize(10.5);
      doc.setTextColor(37, 99, 235);
      doc.text(title, margin, y);
      y += 2;
      doc.setDrawColor(226, 232, 240);
      doc.setLineWidth(0.4);
      doc.line(margin, y, pageWidth - margin, y);
      y += 5;
    }

    function printKeyValueGrid(items) {
      doc.setFontSize(8);
      const colWidth = (pageWidth - (margin * 2) - 6) / 2;
      for (let i = 0; i < items.length; i += 2) {
        const item1 = items[i];
        const item2 = items[i + 1];

        if (item1) {
          doc.setFont('helvetica', 'normal');
          doc.setTextColor(100, 116, 139);
          doc.text(String(item1[0]), margin, y);
          doc.setFont('helvetica', 'bold');
          doc.setTextColor(15, 23, 42);
          doc.text(String(item1[1]), margin + 50, y);
        }

        if (item2) {
          const col2X = margin + colWidth + 6;
          doc.setFont('helvetica', 'normal');
          doc.setTextColor(100, 116, 139);
          doc.text(String(item2[0]), col2X, y);
          doc.setFont('helvetica', 'bold');
          doc.setTextColor(15, 23, 42);
          doc.text(String(item2[1]), col2X + 50, y);
        }

        y += 4.8;
        if (y > 275) { doc.addPage(); y = 16; }
      }
      y += 3;
    }

    // 4. Design Values
    if (data.design_values) {
      printSectionTitle('1. COMPUTED DESIGN VALUES & GEOMETRY');
      const dvItems = [];
      for (const [k, v] of Object.entries(data.design_values)) {
        const label = k.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
        dvItems.push([label, v]);
      }
      printKeyValueGrid(dvItems);
    }

    // 5. Stress Analysis
    if (data.stress_analysis) {
      printSectionTitle('2. STRESS ANALYSIS & VERIFICATION');
      const saItems = [];
      const sa = data.stress_analysis;
      if (sa.bending && sa.bending.pinion_bending_stress_MPa !== undefined) {
        saItems.push(['Pinion Bending Stress', `${sa.bending.pinion_bending_stress_MPa} MPa`]);
        saItems.push(['Allowable Bending Sat', `${sa.bending.pinion_allowable_bending_MPa} MPa`]);
        saItems.push(['Bending Safety Factor', sa.bending.pinion_bending_SF]);
        saItems.push(['Bending Status', sa.bending.status]);
      }
      if (sa.contact && sa.contact.contact_stress_MPa !== undefined) {
        saItems.push(['Contact Stress (Hertz)', `${sa.contact.contact_stress_MPa} MPa`]);
        saItems.push(['Allowable Contact Sac', `${sa.contact.pinion_allowable_contact_MPa} MPa`]);
        saItems.push(['Contact Safety Factor', sa.contact.pinion_contact_SF]);
        saItems.push(['Contact Status', sa.contact.status]);
      }
      if (sa.actual_shear_stress_tau_MPa !== undefined) {
        saItems.push(['Actual Shear Stress', `${sa.actual_shear_stress_tau_MPa} MPa`]);
        saItems.push(['Allowable Shear Stress', `${sa.allowable_shear_stress_MPa} MPa`]);
        saItems.push(['Actual Safety Factor', sa.actual_safety_factor]);
        saItems.push(['Stress Status', sa.status]);
      }
      if (sa.body_shear_stress_tau_MPa !== undefined) {
        saItems.push(['Body Shear Stress', `${sa.body_shear_stress_tau_MPa} MPa`]);
        saItems.push(['Allowable Shear Stress', `${sa.allowable_shear_stress_MPa} MPa`]);
        saItems.push(['Hook Bending Stress', `${sa.hook_bending_stress_MPa} MPa`]);
        saItems.push(['Hook Status', sa.hook_status]);
      }
      printKeyValueGrid(saItems);
    }

    // 6. Inputs
    if (data.inputs) {
      printSectionTitle('3. INPUT SPECIFICATIONS');
      const inpItems = [];
      for (const [k, v] of Object.entries(data.inputs)) {
        const label = k.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
        inpItems.push([label, v]);
      }
      printKeyValueGrid(inpItems);
    }

    // 7. Recommendations
    if (data.recommendations && data.recommendations.length > 0) {
      printSectionTitle('4. ENGINEERING RECOMMENDATIONS');
      doc.setFont('helvetica', 'normal');
      doc.setFontSize(8);
      doc.setTextColor(51, 65, 85);
      const recText = data.recommendations.join('\n• ');
      const splitText = doc.splitTextToSize('• ' + recText, pageWidth - (margin * 2));
      doc.text(splitText, margin, y);
      y += (splitText.length * 4.2) + 4;
    }

    // Footer on all pages
    const pageCount = doc.internal.getNumberOfPages();
    for (let p = 1; p <= pageCount; p++) {
      doc.setPage(p);
      doc.setFontSize(7.5);
      doc.setFont('helvetica', 'normal');
      doc.setTextColor(148, 163, 184);
      doc.setDrawColor(226, 232, 240);
      doc.line(margin, 287, pageWidth - margin, 287);
      doc.text('MechEngine CAD Studio — Certified Mechanical Design Suite', margin, 291);
      doc.text(`Page ${p} of ${pageCount}`, pageWidth - margin, 291, { align: 'right' });
    }

    const cleanFilename = compType.toLowerCase().replace(/[^a-z0-9]/g, '_') + '_report.pdf';
    doc.save(cleanFilename);

  } catch (err) {
    console.error('PDF Generation Error:', err);
    alert('Failed to generate PDF: ' + err.message);
  }
}