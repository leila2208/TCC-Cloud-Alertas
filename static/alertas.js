function actualizarAlertas() {
    fetch(window.location.origin + '/datos')
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
                let tachado = localStorage.getItem(id) === 'true';

                html += `
                    <div class="alerta ${urgenciaClase} ${tachado ? 'tachado' : ''}"
                         onclick="toggleTachado('${id}', this)">
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

function toggleTachado(id, element) {
    const estado = localStorage.getItem(id) === 'true';
    if (estado) {
        localStorage.setItem(id, 'false');
        element.classList.remove('tachado');
    } else {
        localStorage.setItem(id, 'true');
        element.classList.add('tachado');
    }
}

setInterval(actualizarAlertas, 2000);
window.onload = actualizarAlertas;
