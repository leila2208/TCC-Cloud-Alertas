function actualizarAlertas() {
    const contenedor = document.getElementById('contenedor-alertas');
    if(!contenedor) return;
    fetch(window.location.pathname.replace('/alertas','/api/alerta'))
    .then(r=>r.json())
    .then(alertas=>{
        contenedor.innerHTML='';
        alertas.forEach(a=>{
            let div=document.createElement('div');
            div.className=alerta ${a.urgencia} ${a.tachado?'tachado':''};
            div.innerHTML=`<p><strong>Camilla:</strong> ${a.camilla}</p>
                           <p><strong>Hora:</strong> ${a.hora}</p>
                           <p><strong>Necesidad:</strong> ${a.necesidad}</p>`;
            div.onclick=()=>fetch(/api/tachar/${a.id},{method:'POST'}).then(()=>actualizarAlertas());
            contenedor.appendChild(div);
        });
    });
}

setInterval(actualizarAlertas,2000);
window.onload=actualizarAlertas;
