function obtenerCliente(nombre_cliente, id_modal) {
    const nombre = document.getElementById(nombre_cliente).value;
    const modal = document.getElementById(id_modal);

    axios.get(obtenerClienteUrl, {
        params: {
            nombre: nombre
        }
    })
        .then(function (response) {
            const catalogo_clientes = response.data;

            // Limpiar el contenedor antes de imprimir el modal
            modal.innerHTML = "";
            // Iterar sobre cada objeto en el array recibido
            catalogo_clientes.forEach(function (info) {
                console.log(info);
                modal.innerHTML += `<div class="col-md">

                <div class="card" style="margin: 1% !important; height: 90% !important;">
                    <div class="card-body">
                    <div class="row">
                        <div class="col-sm">
                        <i class="bi bi-person-fill"></i>
                        <h4> `+info.nombre+` `+info.apellido+`</h4>
                        </div>
                        <div class="col-sm">
                        <div class="btn-group me-2 gap-2" role="group" aria-label="First group">
                            <a href="/cliente/`+info.id_cliente+`/"> <button type="button" class="btn btn-outline-dark"> <i class="bi bi-pencil-square"></i> Editar </button></a>
                            <a href="/eliminar_cliente/`+info.id_cliente+`/"> <button type="button" class="btn btn-outline-danger"><i class="bi bi-dash-square"></i> Eliminar
                            </button></a>
                        </div>
                        </div>
                    </div>
                    </div>
                </div>
                </div>`

   
            });

            return modal.value;
        })
        .catch(function (error) {
            console.log('Error:', error);
        });
}