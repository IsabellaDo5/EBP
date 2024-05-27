function calcular_tarifa(event){
    var elementoSeleccionado = event.target;
        
    // Obtener el ID del elemento seleccionado
    var tarifa = elementoSeleccionado.options[elementoSeleccionado.selectedIndex].id;
    var tiempo = document.getElementById("tiempo").value;
    var resultado = tarifa*tiempo;

    console.log(tiempo);

};