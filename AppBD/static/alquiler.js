function calcular_tarifa(event) {
    var elementoSeleccionado = event.target;

    // Obtener el ID del elemento seleccionado
    var tarifa = elementoSeleccionado.options[elementoSeleccionado.selectedIndex].id;
    var tiempo = document.getElementById("tiempo").value;
    var resultado = tarifa * tiempo;

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

function activarHoras(event) {
    const horaInicio = document.getElementById('horaInicio');
    const horaFin = document.getElementById('horaFin');
    horaInicio.disabled = false;
    horaFin.disabled = false;
}


function desactivar_horasReservadas(event, id_alquiler) {

    const fechaInput = document.getElementById('fecha');
    const horaInicioInput = document.getElementById('horaInicio');
    const horaFinInput = document.getElementById('horaFin');
    const pisoInput = document.getElementById('tipoAlquiler');
    const msg_horarios = document.getElementById('horariosReservados');
    const btn_save = document.getElementById("guardarAlquiler");
    msg_horarios.innerHTML = "Reservaciones para esta fecha en este piso: <br>";
    console.log("FECHA SELECCIONADA: "+fechaInput.value+" TIPO DE ALQUILER: "+pisoInput.value);
    if (fechaInput.value && pisoInput.value) {
        axios.get(horasOcupadasURL, {
            params: {
                'fecha': fechaInput.value,
                'piso': pisoInput.value,
                'id_alquiler': id_alquiler
            }
        })
            .then(function (response) {
                if (response.data) {
                    const horasOcupadas = response.data.horas_ocupadas;
                    // Reiniciar los selectores de hora
                    horaInicioInput.disabled = false;
                    horaFinInput.disabled = false;

                    // Habilitar todas las opciones inicialmente
                    horaInicioInput.innerHTML = '';
                    horaFinInput.innerHTML = '';

                    if (horasOcupadas.length != 0) {
                        // Deshabilitar las horas ocupadas
                        horasOcupadas.forEach(function (hora) {
                            const horaInicio = hora.horaInicio;
                            const horaFin = hora.horaFin;
                            const id_tipoAlq = hora.id_tipoAlquiler;
                            if (id_tipoAlq == 1 ){
                                msg_horarios.innerHTML += "<b>Primera Planta: </b> <b>Hora inicio: </b>" + horaInicio + " <b>Hora de fin: </b>" + horaFin + "<br>";

                            }
                            if (id_tipoAlq == 2 ){
                                msg_horarios.innerHTML += "<b>Segunda Planta: </b> <b>Hora inicio: </b>" + horaInicio + " <b>Hora de fin: </b>" + horaFin + "<br>";

                            }
                            if (id_tipoAlq == 3) {
                                msg_horarios.innerHTML = "Esta fecha ya está ocupada para una reservación de ambos pisos, por favor escoge otra fecha";
                                btn_save.disabled = true;
                            }
                            else if (id_tipoAlq != 3) {
                                for (let i = 0; i < 24; i++) {
                                    for (let j = 0; j < 60; j += 1) { // Incrementos de 1 minuto
                                        const hourString = i.toString().padStart(2, '0');

                                        if (hourString >= horaInicio && hourString < horaFin) {

                                            /*console.log(`HORAS DESHABILITADAS: ` + `${hourString}`);*/
                                            ajustarHora(hourString, horaFin, horaInicio, id_tipoAlq);

                                        }
                                    }
                                }
                            }
                        })
                    }
                    else {
                        console.log("Entra a else de Axios");
                        btn_save.disabled = false;
                    }
                }
            }
            )
            .catch(function (error) {
                console.error(error);
            });
    }

};

function serv_extras(event) {
    div_extras = document.getElementById("div_extras");
    tipoAlquiler = document.getElementById("tipoAlquiler");

    if (parseInt(tipoAlquiler.value) == 1 || parseInt(tipoAlquiler.value == 2)) {
        div_extras.innerHTML = `<p>¿Desea agregar servicios de comida y bebida? Por un costo extra de $50</p>
            <div class="form-check form-check-inline">
                <input class="form-check-input" type="radio" name="agregar_servicios" id="inlineRadio1" value="si">
                <label class="form-check-label" for="inlineRadio1">Sí</label>
            </div>
            <div class="form-check form-check-inline">
                <input class="form-check-input" type="radio" name="agregar_servicios" id="inlineRadio2" value="no">
                <label class="form-check-label" for="inlineRadio2">No</label>
            </div>`;

    }
    else if (parseInt(tipoAlquiler.value) == 3) {
        console.log("ESTAS ENTRANDO AQUI PIPI SEGUNDO IF?" + tipoAlquiler.value);
        div_extras.innerHTML = `Los servicios de comida y bebida vienen incluidos sin costo extra. <div class="invisible form-check form-check-inline">
                <input class="form-check-input" type="radio" name="agregar_servicios" id="inlineRadio1" value="si" checked>
                <label class="form-check-label" for="inlineRadio1">Sí</label>
            </div>`

    }
}
function ajustarHora(horaOcupada, horaFin, horaInicio, id_tipoAlquiler) {
    div_horarioOcupado = document.getElementById("horarioOcupado");
    btn_save = document.getElementById("guardarAlquiler");
    console.log("Entra a ajustarHora");
    document.getElementById('horaInicio').addEventListener('input', function (e) {
        var timeValue = e.target.value;
        if (timeValue) {
            var [hours, minutes] = timeValue.split(':');
            if (minutes !== '00') {
                e.target.value = `${hours}:00`;
            }
            if (horaInicio) {
                if (hours == horaOcupada) {
                    div_horarioOcupado.style.display = 'block';
                    div_horarioOcupado.innerHTML = "Ya existe una reservación en este piso dentro de este horario, por favor escoge otra hora o fecha.";
                    btn_save.disabled = true;
                }
                if (hours > horaFin || hours < horaInicio) {
                    div_horarioOcupado.style.display = 'hidden';
                    div_horarioOcupado.innerHTML = "";
                    btn_save.disabled = false;
                }
            }
            else {
                btn_save.disabled = false;
            }

        }
    });

    document.getElementById('horaFin').addEventListener('input', function (e) {
        var timeValue = e.target.value;
        if (timeValue) {
            console.log("entra a primer if(timeValue)");
            var [hours, minutes] = timeValue.split(':');
            if (minutes !== '00') {
                e.target.value = `${hours}:00`;
            }
            if (horaFin) {
                console.log("entra a segundo if(horA FIN)");
                if (hours == horaOcupada) {
                    div_horarioOcupado.style.display = 'block';
                    div_horarioOcupado.innerHTML = "Ya existe una reservación en este piso dentro de este horario, por favor escoge otra hora o fecha.";
                    btn_save.disabled = true;
                }
                if (hours > horaFin || hours < horaInicio) {
                    div_horarioOcupado.style.display = 'hidden';
                    div_horarioOcupado.innerHTML = "";
                    btn_save.disabled = false;
                }
            }
            else {
                console.log("entra a else final(timeValue)");
                btn_save.disabled = false;
            }

        }
    });
}

function obtener_fechaFactura() {
    document.addEventListener('DOMContentLoaded', function() {
        var inputFecha = document.getElementById('fecha_factura');
        
        // Obtener la fecha actual en UTC-6 (Nicaragua)
        var hoy = new Date(new Date().toLocaleString('en-US', { timeZone: 'America/Managua' }));
        
        // Formatear la fecha en formato ISO (YYYY-MM-DD)
        var fechaFormateada = hoy.toISOString().split('T')[0];
        
        // Asignar la fecha formateada al input
        inputFecha.value = fechaFormateada;
      });
}

function obtener_descuento(){
    const descuento_porcentaje = document.getElementById("descuento_factura");
    const total_pagar = document.getElementById("total_pagar");
    const costo_final = document.getElementById("total_pagar_descuento");
    let descuento = 1-((descuento_porcentaje.value)/100)
    let temp = parseFloat(total_pagar.value)*parseFloat(descuento);
    costo_final.value = temp;
    return descuento;
}
    
async function convertir_dolares(abono) {
    const url = `https://v6.exchangerate-api.com/v6/18e360030a5606d63bc549d6/pair/NIO/USD`;

    try {
        const response = await fetch(url);
        const data = await response.json();
        const tipoCambio = data.conversion_rate;
        let cantidadDolares = abono * tipoCambio;
        return cantidadDolares;
    } catch (error) {
        console.error('Error al obtener el tipo de cambio:', error);
    }
}
async function convertir_aCordobas(abono) {
    const url = `https://v6.exchangerate-api.com/v6/18e360030a5606d63bc549d6/pair/USD/NIO`;

    try {
        const response = await fetch(url);
        const data = await response.json();
        const tipoCambio = data.conversion_rate;
        let cantidadDolares = abono * tipoCambio;
        return cantidadDolares;
    } catch (error) {
        console.error('Error al obtener el tipo de cambio:', error);
    }
}
async function calcular_cambio(e, totalPagar, tipoAlquiler) {
    e.preventDefault();

    const abono = document.getElementById("abono").value;
    const tipoCambio = document.getElementById("tipo_cambio").value;
    const mostrarCambio = document.getElementById("cambio");
    const errorAbono = document.getElementById("error_abono");
    errorAbono.style.display = "hidden";
    errorAbono.innerText = "";
    let cambio = 0;
    let abonoDolares = 0;
    let descuento = obtener_descuento();

    if (tipoCambio == 2) {
        abonoDolares = await convertir_dolares(abono);
        cambio = await convertir_aCordobas(abonoDolares - (totalPagar*descuento));
        console.log(abonoDolares)
    } else {
        abonoDolares = abono;
        cambio = abonoDolares - (totalPagar*descuento);
    }


    if (abonoDolares >= (totalPagar*descuento)) {
        mostrarCambio.value = cambio;
        errorAbono.style.display = "none";
    } else {
        mostrarCambio.value = 0;
        errorAbono.style.display = "block";
        errorAbono.innerText = "El abono no puede ser menor al total a pagar.";
    }
}

function calcularCostoReservacion(tiempo, tipoAlquiler) {
    const [horas, minutos] = tiempo.split(':').map(Number);
    const totalHoras = horas + minutos / 60;
    const tarifaAdicionalPorHora = 50;
    const horasBase = 4;
    let tarifaBase;

    if (tipoAlquiler === "Primera planta" || tipoAlquiler === "Segunda planta") {
        tarifaBase = 250;
    } else {
        tarifaBase = 400;
    }

    if (totalHoras <= horasBase) {
        return tarifaBase;
    } else {
        const horasAdicionales = totalHoras - horasBase;
        const costoAdicional = Math.ceil(horasAdicionales) * tarifaAdicionalPorHora;
        return tarifaBase + costoAdicional;
    }
}

function calcularDiferencia(horaInicio, horaFin) {
    const [horaInicioHoras, horaInicioMinutos] = horaInicio.split(":").map(Number);
    const [horaFinHoras, horaFinMinutos] = horaFin.split(":").map(Number);
    const fechaInicio = new Date();
    fechaInicio.setHours(horaInicioHoras, horaInicioMinutos, 0, 0);
    const fechaFin = new Date();
    fechaFin.setHours(horaFinHoras, horaFinMinutos, 0, 0);
    const diferenciaMs = fechaFin - fechaInicio;
    const diferenciaMinutos = Math.floor(diferenciaMs / (1000 * 60));
    const horas = Math.floor(diferenciaMinutos / 60);
    const minutos = diferenciaMinutos % 60;
    return `${String(horas).padStart(2, '0')}:${String(minutos).padStart(2, '0')}`;
}
function facturar(event) {
    // Seleccionar el div que queremos imprimir
    const facturaDiv = document.getElementById("factura_alquiler");
    
    // Clonar el div para manipularlo sin afectar el DOM original
    const facturaClone = facturaDiv.cloneNode(true);
    
    // Obtener todos los inputs dentro del div clonado
    const inputs = facturaClone.getElementsByTagName('input');
    
    // Copiar los valores de los inputs originales a los inputs clonados
    for (let i = 0; i < inputs.length; i++) {
        const originalInput = document.getElementById(inputs[i].id);
        if (originalInput) {
            inputs[i].setAttribute('value', originalInput.value);
        }
    }
    
    // Convertir el div clonado a HTML
    const facturaHTML = facturaClone.innerHTML;

    // Crear una nueva ventana
    var ventana = window.open('', '', 'height=700,width=400');

    // Insertar todo lo que queremos que esté en el HTML de la nueva ventana
    ventana.document.write('<html><head><title>Factura</title>');
    ventana.document.write('<link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">');
    ventana.document.write('<style>body{ margin: 20px; }</style>'); // Puedes añadir más estilos personalizados aquí
    ventana.document.write('</head><body>');
    ventana.document.write(facturaHTML);
    ventana.document.write('</body></html>');

    ventana.document.close();

    ventana.onload = function() {
        // Esto hace que se abra automáticamente la función de imprimir y luego de elegir una opción, cerrar la ventana automáticamente
        ventana.print();
        ventana.close();
    };
}
