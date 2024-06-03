function ItemsMasVendidos() {
    let ctx = document.getElementById("items_chart").getContext("2d");
    var cantidades = [];
    var items = [];
    axios.get(items_url)
        .then(function (response) {
            const lista_items = response.data;
            console.log(lista_items);

            lista_items.forEach(function (item) {
                cantidades.push(item.CantidadVendida);
                items.push(item.nombre);
            });

            // Llama a la función para crear la gráfica después de que los datos hayan sido cargados
            GraficaItemsMasVendidos(items, cantidades, ctx);
        })
        .catch(function (error) {
            console.log('Error:', error);
        });
}

function PlatillosMasVendidos() {
    let ctx = document.getElementById("platillos_chart").getContext("2d");
    var cantidades = [];
    var platillos = [];

    axios.get(platillos_url)
        .then(function (response) {
            const lista_platillos = response.data;
            console.log("LISTA DE PLATILLOS: "+lista_platillos);

            lista_platillos.forEach(function (item) {
                cantidades.push(item.CantidadVendida);
                platillos.push(item.nombre);
            });

            // Llama a la función para crear la gráfica después de que los datos hayan sido cargados
            GraficaItemsMasVendidos(platillos, cantidades, ctx);
        })
        .catch(function (error) {
            console.log('Error:', error);
        });
}
function GraficaItemsMasVendidos(x_label, y_label, ctx) {
    const chart = new Chart(ctx, {
        type: "bar",
        data: {
            labels: x_label,
            datasets: [
                {
                    label: "Cantidad vendida",
                    backgroundColor: escogerColor(),
                    borderColor: "#0077b6",
                    data: y_label
                }
            ]
        },
        options: {
            responsive: true, // Asegúrate de que esto esté configurado
            
            title: {
                text: "Productos más vendidos",
                display: true
            }
        }
    });
}
function escogerColor() {
    var colorList = ["#a2d2ff", "#d62828", "#0077b6", "#83c5be", "#e76f51"];

    
    if (colorList && colorList.length > 0) {
        // Generar un número aleatorio entre 0 y la longitud de la lista de colores
        var randomIndex = Math.floor(Math.random() * colorList.length);
        // Devolver el color seleccionado aleatoriamente
        return colorList[randomIndex];
    } else {
        // Si la lista de colores está vacía, devolver un mensaje de error
        return "Error: La lista de colores está vacía";
    }
}

