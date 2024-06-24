function calcular_tarifa(event){
    var elementoSeleccionado = event.target;
        
    // Obtener el ID del elemento seleccionado
    var tarifa = elementoSeleccionado.options[elementoSeleccionado.selectedIndex].id;
    var tiempo = document.getElementById("tiempo").value;
    var resultado = tarifa*tiempo;

    console.log(tiempo);

};
async function buscar_clientes_cedula(event) {
    let cedula = document.getElementById("cedula").value;
    let cliente_html = document.getElementById("cliente");

    try {
        let resp = await cliente_cedula(cedula);
        cliente_html.value = resp;
    } catch (error) {
        console.error('Error al obtener clientes:', error);
        cliente_html.value = "Error al obtener clientes.";
    }
}

async function cliente_cedula(no_cedula) {
    try {
        const response = await axios.get(obtenerCedula, {
            params: {
                cedula: no_cedula
            }
        });

        const cliente = response.data;

        if (cliente.length > 0) {
            let resp = "";
            cliente.forEach(function (info) {
                resp += " " + info.nombre + " " + info.apellido;
            });
            return resp.trim();
        } else {
            return "No se encontraron coincidencias.";
        }
    } catch (error) {
        console.error('Error en la solicitud HTTP:', error);
        throw error; // Propagar el error para que pueda ser manejado por el llamador
    }
}
