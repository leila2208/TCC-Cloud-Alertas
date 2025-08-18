const urgencias = ['baja','media','alta'];
let currentDevice = 'default';
let settingsCache = null;

function sel(id){ return document.getElementById(id); }

function llenarDeviceIds(){
  const s = sel('deviceId');
  s.innerHTML = '';
  (deviceIds || ['default']).forEach(d=>{
    const opt = document.createElement('option');
    opt.value = d; opt.textContent = d;
    s.appendChild(opt);
  });
  s.value = currentDevice;
  s.onchange = ()=>{ currentDevice = s.value; cargar(); };
}

function renderBotones(botones){
  const cont = sel('botones');
  cont.innerHTML = '';
  botones.forEach((b,i)=>{
    const wrap = document.createElement('div');
    wrap.className = 'fila';
    wrap.innerHTML = `
      <div style="flex:2">
        <label>Botón ${i+1} - Nombre</label>
        <input id="b_label_${i}" value="${b.label}">
      </div>
      <div style="flex:1">
        <label>Urgencia</label>
        <select id="b_urg_${i}">
          ${urgencias.map(u=><option ${u===b.urgencia?'selected':''}>${u}</option>).join('')}
        </select>
      </div>
    `;
    cont.appendChild(wrap);
  });
}

function renderPrioPat(map){
  const cont = sel('prioPat');
  cont.innerHTML = '';
  // mostramos 3 filas por comodidad (editable)
  const keys = Object.keys(map || {});
  const filas = Math.max(keys.length, 3);
  for(let i=0;i<filas;i++){
    const k = keys[i] || '';
    const v = k ? map[k] : 0;
    const row = document.createElement('div');
    row.className = 'fila';
    row.innerHTML = `
      <div style="flex:2">
        <label>Patología</label>
        <input id="pp_key_${i}" value="${k}">
      </div>
      <div style="flex:1">
        <label>Extra</label>
        <input id="pp_val_${i}" type="number" value="${v}">
      </div>
    `;
    cont.appendChild(row);
  }
}

function cargar(){
  fetch(/api/settings?device_id=${currentDevice})
    .then(r=>r.json())
    .then(s=>{
      settingsCache = s;
      sel('paciente').value = s.paciente || '';
      sel('camilla').value  = s.camilla || 1;
      sel('patologia').value = s.patologia || '';
      renderBotones(s.botones || []);
      renderPrioPat(s.prioridad_patologia || {});
      actualizarAlertas();
    });
}

function recogerPrioPat(){
  const res = {};
  for(let i=0;i<10;i++){
    const k = sel(pp_key_${i}); const v = sel(pp_val_${i});
    if(!k || !v) continue;
    const key = (k.value||'').trim().toLowerCase();
    if(!key) continue;
    res[key] = parseInt(v.value||'0');
  }
  return res;
}

function guardar(){
  const payload = {
    paciente: sel('paciente').value,
    camilla: parseInt(sel('camilla').value||'1'),
    patologia: sel('patologia').value,
    botones: [],
    prioridad_patologia: recogerPrioPat()
  };

  for(let i=0;i<4;i++){
    payload.botones.push({
      label: sel(b_label_${i}).value || BTN${i+1},
      urgencia: sel(b_urg_${i}).value || 'baja'
    });
  }

  fetch(/api/settings?device_id=${currentDevice}, {
    method:'PUT',
    headers:{'Content-Type':'application/json'},
    body: JSON.stringify(payload)
  }).then(r=>r.json())
    .then(()=>cargar());
}

function limpiarAlertas(){
  fetch('/limpiar',{method:'POST'}).then(()=>actualizarAlertas());
}

window.addEventListener('load', ()=>{
  llenarDeviceIds();
  cargar();
});
