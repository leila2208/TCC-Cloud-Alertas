function claseUrg(u){
  if(!u) return 'bajo';
  u = u.toLowerCase();
  if(u === 'alta') return 'alto';
  if(u === 'media') return 'medio';
  return 'bajo';
}

function itemAlertaHTML(a){
  return `
    <div class="alerta ${claseUrg(a.urgencia)} ${a.tachado ? 'tachado':''}" data-id="${a.id}">
      <div class="row">
        <div><strong>Camilla:</strong> ${a.camilla}</div>
        <div><strong>Hora:</strong> ${a.hora}</div>
        <div class="badge">Prio: ${a.prioridad}</div>
      </div>
      ${a.paciente ? <div><strong>Paciente:</strong> ${a.paciente}</div> : ''}
      ${a.patologia ? <div><strong>Patología:</strong> ${a.patologia}</div> : ''}
      <div><strong>Urgencia:</strong> ${a.urgencia || '-'}</div>
      <div><strong>Necesidad:</strong> ${a.necesidad || '-'}</div>
      <div class="small">ID: ${a.id}</div>
    </div>
  `;
}

function actualizarAlertas(){
  fetch('/datos')
    .then(r=>r.json())
    .then(arr=>{
      const html = arr.map(itemAlertaHTML).join('');
      const cont = document.getElementById('contenedor-alertas');
      if(cont) cont.innerHTML = html;
    });
}

setInterval(actualizarAlertas, 2000);
window.addEventListener('load', actualizarAlertas);

// Solo admin: click para tachar
document.addEventListener('click', (e)=>{
  const card = e.target.closest('.alerta');
  if(!card) return;
  if(!location.pathname.includes('/admin')) return;

  const id = card.dataset.id;
  fetch('/tachar', {
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body: JSON.stringify({id})
  }).then(()=>actualizarAlertas());
});
