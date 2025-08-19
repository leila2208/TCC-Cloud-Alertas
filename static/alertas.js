function claseUrg(u){
  const x=(u||"").toLowerCase();
  if(x==="alta") return "alert-alta";
  if(x==="media") return "alert-media";
  return "alert-baja";
}

function pintar(alertas){
  const c = document.getElementById('alerts');
  if(!c) return;
  c.innerHTML = alertas.map(a => `
    <div class="alert-card ${claseUrg(a.urgency)} ${a.done?'done':''}" data-id="${a.id}">
      <div><b>Cama:</b> ${a.bed || '—'} ${a.patient?` • <b>Paciente:</b> ${a.patient}`:''}</div>
      <div><b>Hora:</b> ${new Date(a.timestamp).toLocaleTimeString()}</div>
      ${a.pathology?<div><b>Patología:</b> ${a.pathology}</div>:''}
      <div><b>Urgencia:</b> ${a.urgency}</div>
      <div><b>Necesidad:</b> ${a.need}</div>
    </div>
  `).join('');
}

function fetchAlerts(){
  if(!window.HOSPITAL_ID) return;
  fetch(/api/alerts?hospital_id=${HOSPITAL_ID})
    .then(r=>r.json()).then(pintar)
    .catch(_=>{});
}

setInterval(fetchAlerts, 2000);
window.addEventListener('load', ()=>{
  fetchAlerts();
  document.addEventListener('click', (e)=>{
    const card = e.target.closest('.alert-card');
    if(!card) return;
    if(!window.CAN_TOGGLE) return; // solo enfermería
    const id = card.dataset.id;
    fetch(/api/alerts/${id}/toggle-done, {method:'POST'})
      .then(_=>fetchAlerts());
  });
});
