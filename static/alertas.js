function actualizarAlertas() {
    fetch('/datos')
        .then(response => response.json())
        .then(alertas => {
            let html = '';
            alertas.forEach(data => {
                let urgenciaClase = '';
                if (data.urgencia) {
                    const u = data.urgencia.toLowerCase();
                    if (u === 'baja') urgenciaClase = 'bajo';
                    else if (u === 'media') urgenciaClase = 'medio';
                    else if (u === 'alta') urgenciaClase = 'alto';
                }

                let id = data.camilla + '-' + data.hora + '-' + data.necesidad;
                let tachado = data.tachado ? true : false;

                html += `
                    <div class="alerta ${urgenciaClase} ${tachado ? 'tachado' : ''}">
                        <p><strong>Camilla:</strong> ${data.camilla}</p>
                        <p><strong>Hora:</strong> ${data.hora}</p>
                        ${data.patologia ? `<p><strong>Patología:</strong> ${data.patologia}</p>` : ''}
                        <p><strong>Urgencia:</strong> ${data.urgencia}</p>
                        <p><strong>Necesidad:</strong> ${data.necesidad}</p>
                    </div>
                `;
            });
            document.getElementById('contenedor-alertas').innerHTML = html;
        })
        .catch(error => {
            document.getElementById('contenedor-alertas').innerHTML = `
                <div class="alerta alto">
                    <p>Error al obtener datos</p>
                </div>
            `;
        });
}

setInterval(actualizarAlertas, 2000);
window.onload = actualizarAlertas;
