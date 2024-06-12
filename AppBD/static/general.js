function obtenerCliente(nombre_cliente, id_modal,tipo_busq) {
    const nombre = document.getElementById(nombre_cliente).value;
    const modal = document.getElementById(id_modal);
    let id =0;
    let url_editar = "";
    let url_eliminar = "";
    
    axios.get(obtenerClienteUrl, {
        params: {
            nombre: nombre,
            tipo: tipo_busq
        }
    })
        .then(function (response) {
            const catalogo_clientes = response.data;

            // Limpiar el contenedor antes de imprimir el modal
            modal.innerHTML = "";
            // Iterar sobre cada objeto en el array recibido
            catalogo_clientes.forEach(function (info) {
                if (tipo_busq == "cliente"){
                    id = info.id_cliente;
                    url_editar= "/cliente/"+id+"/";
                    url_eliminar= "/eliminar_cliente/"+id+"/";
                }
                else{
                    id = info.id_empleado;
                    url_editar= "/empleado/"+id+"/";
                    url_eliminar= "/eliminar_empleado/"+id+"/";
                }

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
                            <a href="`+url_editar+`"> <button type="button" class="btn btn-outline-dark"> <i class="bi bi-pencil-square"></i> Editar </button></a>
                            <a href="`+url_eliminar+`"> <button type="button" class="btn btn-outline-danger"><i class="bi bi-dash-square"></i> Eliminar
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