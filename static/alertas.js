function attendAlert(alertId) {
    fetch(/api/alert/${alertId}/attend, { method: 'POST' })
        .then(res => res.json())
        .then(data => {
            if(data.success){
                document.getElementById(alert-${alertId}).remove();
            }
        });
}
