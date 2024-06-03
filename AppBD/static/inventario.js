function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
const csrftoken = getCookie('csrftoken');


var url_imagen = document.getElementById("icon_original").src;

function usuario_elimina_imagen(event){
    id_item = document.getElementById("id_item");
    imagen = document.getElementById("icon_original");
    btn_eliminar = document.getElementById("btn_eliminar_icon");

    btn_eliminar.style.display = "none";
    imagen.src= "https://cdn3.iconfinder.com/data/icons/online-states/150/Photos-512.png";

    eliminar_icon_bd(id_item.value, "");
}

function eliminar_icon_bd(id, nuevoValor) {

    console.log(csrftoken, id, nuevoValor);
    axios.post(url_delete, {
        id: id,
        nuevo_valor: nuevoValor
    }, {
        headers: {
            'X-CSRFToken': csrftoken,
            'Content-Type': 'application/json'
        }
    })
    .then(response => {
        if (response.data.status === 'success') {
            console.log('Campo actualizado correctamente');
        } else {
            console.error('Error al actualizar el campo:', response.data.message);
        }
    })
    .catch(error => {
        console.error('Error en la solicitud:', error);
    });
}

function mostrar_imagen(){
    imagen = document.getElementById("icon_original");
    btn_eliminar = document.getElementById("btn_eliminar_icon");
    console.log(imagen.src)
    if( imagen.src == "http://127.0.0.1:8000/media/"){
        btn_eliminar.style.display = "none";
        imagen.src= "https://cdn3.iconfinder.com/data/icons/online-states/150/Photos-512.png";
    }
}