import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.forms import *
from django.contrib.auth import login, logout
from django.db import connection
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import JsonResponse
import time
import hashlib
import datetime
from datetime import datetime, time

# Create your views here.
def login(request):
    if request.method=='POST':

        username= request.POST['username']
        password = request.POST['password']

        h = hashlib.new("SHA256")
        password = request.POST['password']
        h.update(password.encode())
        password_hash = h.hexdigest()


        with connection.cursor() as cursor:
            # Busca la cuenta en la db
            query="EXEC buscar_cuenta %s"
            filtro = (username,)
            cursor.execute(query, filtro)
            user = cursor.fetchall()


            
            # Obtiene los resultados
            
        connection.commit()

        print("CONTRASEÑA BD:"+str(user[0][2]))
        print("CONTRASEÑA hash:"+str(password_hash))
        if len(user)==0:

            messages.error(request, "ERROR:Credenciales no válidas.")
            return render(request, 'login.html')
        
        if password_hash == user[0][2]:#--->esto es la contraseña
            with connection.cursor() as cursor:
                query= "select id_empleado from empleados where id_cuenta = %s"
                filtro = (user[0][0],)
                cursor.execute(query, filtro)
                id_empleado_actual= cursor.fetchall()
                

                print("ID EMPLEADO LOGEADO"+str(id_empleado_actual[0][0]))
                user_info={ 'empleado_id': id_empleado_actual[0][0]
                }       

            request.session['empleado_id'] = user_info
            return redirect('/')
        else:
            messages.error(request, "ERROR:Credenciales no válidas.")
            return render(request, 'login.html')
    else:
        return render(request, 'login.html')
# Cerrar sesión    
def cerrar_sesion(request):
    
    del request.session['empleado_id']
    return redirect('/')

# Pagina de inicio
def inicio(request):
    if 'empleado_id' not in request.session:
        return redirect('/login')
    else:
        with connection.cursor() as cursor:
            productos=cursor.execute("select * from inventario where cantidad<10").fetchall()
        return render(request, 'index.html', context={
            'productos': productos,
        })

# Muestra la lista de empleados
def empleados(request):
    if 'empleado_id' not in request.session:
        return redirect('/login')
    else:
        with connection.cursor() as cursor:
            resultados=cursor.execute("SELECT * FROM empleados").fetchall()
            
        print(resultados)    
        return render(request, 'empleados.html', context={
            'trab': resultados,
        })

# Editar la información de los empleados
def edit_empleados(request, id_emp):
    if 'empleado_id' not in request.session:
        return redirect('/login')
    else:
        if request.method == 'GET':
            with connection.cursor() as cursor:
                query="exec buscar_empleado %s"
                filtro = (id_emp,)
                cursor.execute(query, filtro)
                # Obtiene los resultados
                info = cursor.fetchall()

            with connection.cursor() as cursor:
                catalogo_roles = cursor.execute("SELECT * FROM roles").fetchall()

                
                print("Info del usuario:"+str(info))

            #info = Empleado.objects.filter(id_empleado=id_emp)
            return render(request, 'editar_empleados.html', context={
                'info': info,
                'catalogo_roles': catalogo_roles,
            })
        else:
            with connection.cursor() as cursor:
                sql_query = "exec modificar_empleado %s,%s,%s,%s,%s,%s,%s,%s"
                nuevos_valores = (id_emp, request.POST['nombre'], request.POST['apellido'], request.POST['direccion'], request.POST['cedula'], request.POST['telefono'], request.POST['sexo'], request.POST['rol'])
                cursor.execute(sql_query, nuevos_valores)

       
            connection.commit()
            
            return redirect('/empleados/')
        
# Agregar un empleado   
def agregar_empleado(request):
    #if 'empleado_id' not in request.session:
        #return redirect('/login')
    #else:
        if request.method == 'GET':

            with connection.cursor() as cursor:
                roles= cursor.execute("SELECT * FROM roles").fetchall()

            return render(request, 'add_empleados.html', context={
                'lista_roles':roles,
            })
        else:
            # encripta la contraseña
            h = hashlib.new("SHA256")
            password_flat = request.POST['password']
            h.update(password_flat.encode())
            password = h.hexdigest()

            with connection.cursor() as cursor:
                sql_query = "exec registrar_empleado %s,%s,%s,%s,%s,%s,%s,%s,%s"
                valores = (request.POST['nombre'], request.POST['apellido'], request.POST['direccion'], request.POST['cedula'], request.POST['telefono'], request.POST['sexo'], request.POST['rol'], request.POST['username'], password)
                cursor.execute(sql_query, valores)

            connection.commit()

            return redirect('/empleados/')

def eliminar_empleado(request, id_emp):
    with connection.cursor() as cursor:
        sql_query = "DELETE FROM empleados WHERE id_empleado = %s"
        valores = (id_emp,)
        cursor.execute(sql_query, valores)

    connection.commit()

    return redirect('/empleados/')

#----------------------------inventario-------------------------------------
def inventario(request):
    if 'empleado_id' not in request.session:
        return redirect('/login')
    else:
        if request.method == 'GET':
            with connection.cursor() as cursor:
                resultados=cursor.execute("EXEC ver_inventario").fetchall()
            
                print(resultados)    
                return render(request, 'inventario.html', context={
                    'trab': resultados,
                })

def agregar_inventario(request):
    if 'empleado_id' not in request.session:
        return redirect('/login')
    else:
        if request.method == 'GET':
            with connection.cursor() as cursor:
                tipos_item= cursor.execute("SELECT nombre FROM tipoItem").fetchall()
            connection.commit()

            with connection.cursor() as cursor:
                medidas= cursor.execute("SELECT nombre FROM medidas").fetchall()
            connection.commit()
            return render(request, 'add_inventario.html', context={
                'tiposdeItem': tipos_item,
                'unidadesdeMedida': medidas,
            })
        else:
            UnidadMedida=""
            
            try:
                UnidadMedida= request.POST['unidad_medida']
            except:
                UnidadMedida=" "

            with connection.cursor() as cursor:
                sql_query = "EXEC agregar_inventario %s, %s, %s, %s, %s"
                valores = (request.POST['nombre'], request.POST['precio'], request.POST['id_tipoItem'], request.POST['cantidad'],UnidadMedida)
                cursor.execute(sql_query, valores)

            connection.commit()

            return redirect('/inventario/')
    
def eliminar_item(request,id_item):
    with connection.cursor() as cursor:
        sql_query = "DELETE FROM inventario WHERE id_item = %s"
        valores = (id_item,)
        cursor.execute(sql_query, valores)

    connection.commit()

    return redirect('/inventario/')
    
def edit_inventario(request, id_item):
    if 'empleado_id' not in request.session:
        return redirect('/login')
    else:
        if request.method == 'GET':

            print("MI ID ITEM ES: "+str(id_item))
            with connection.cursor() as cursor:
                query="EXEC obtener_info_item %s"
                filtro = (id_item,)
                cursor.execute(query, filtro)

                # Obtiene los resultados
                info = cursor.fetchall()

                print("Obtener info item: "+str(info))
            with connection.cursor() as cursor:
                catalogo_tipoItem = cursor.execute("SELECT nombre FROM tipoItem").fetchall()
                catalogo_medidas = cursor.execute("SELECT id_medida, nombre FROM medidas").fetchall()

            #info = Empleado.objects.filter(id_empleado=id_emp)
            return render(request, 'editar_item.html', context={
                'info': info,
                'catalogo_tipoItem': catalogo_tipoItem,
                'catalogo_medidas':catalogo_medidas
            })
        else:
            try:
                unidad_medida= request.POST['unidad_medida']
            except:
                unidad_medida=""

            with connection.cursor() as cursor:

                print("UNIDAD DE MEDIDA: "+unidad_medida)
                sql_query = "EXEC editar_info_item %s, %s, %s, %s, %s, %s"
                nuevos_valores = (request.POST['nombre'], request.POST['precio'],request.POST['cantidad'],unidad_medida, request.POST['id_tipoItem'],  id_item)
                cursor.execute(sql_query, nuevos_valores)
            connection.commit()
            
            return redirect('/inventario/')
#-----------------------------platillos----------------------------------



def platillos(request):
    if 'empleado_id' not in request.session:
        return redirect('/login')
    else:
        if request.method=='GET':
            with connection.cursor() as cursor:
                platillos= cursor.execute("EXEC info_platillos").fetchall()
            


            print("PLATILLOS:"+str(platillos))
            return render(request, 'platillos.html', context={
                'platillos': platillos,
            })


def add_platillo(request):
    #if 'empleado_id' not in request.session:
    #    return redirect('/login')
    #else:
        if request.method=='GET':
            with connection.cursor() as cursor:
                lista_ingredientes= cursor.execute("SELECT * FROM inventario WHERE id_tipoItem=1").fetchall()
            print("INGREDIENTES: "+str(lista_ingredientes))
            return render(request, 'add_platillo.html', context={
                'ingredientes': lista_ingredientes,
            })
        
        else:
            nombre_platillo= request.POST['nombre']
            desc= request.POST['desc']
            precio=request.POST['precio']
            ingrediente= request.POST.getlist('nombre_ingredientes')
            cantidad = request.POST.getlist('cantidad')
            print("PRECIO PLATILLO:"+str(precio))
        
            for j,y in zip(ingrediente,cantidad):
                with connection.cursor() as cursor:
                    query="EXEC agregar_platillo %s, %s, %s,%s, %s"
                    filtro = (nombre_platillo, desc, precio, j,y)
                    cursor.execute(query, filtro)
                connection.commit()
            return redirect('/platillos/')

def editar_platillo(request, id_platillo):
    if 'empleado_id' not in request.session:
        return redirect('/login')
    else:
        if request.method=='POST':
            nombre_platillo= request.POST['nombre']
            desc= request.POST['desc']
            precio=request.POST['precio']
            ingrediente= request.POST.getlist('nombre_ingredientes')
            cantidad = request.POST.getlist('cantidad')

            print("Ingredientes: "+str(ingrediente)+"cantidad: "+str(cantidad))

            # Elimina todos los registros anteriores de platillo_detalle
            with connection.cursor() as cursor:
                query="DELETE FROM platillo_detalle where id_platillo= %s"
                filtro = (id_platillo,)
                cursor.execute(query, filtro)
            connection.commit()

            for j,y in zip(ingrediente,cantidad):

                if len(j)!=0:
                    
                    print("guardando: "+ str(j))

                    with connection.cursor() as cursor:
                        query="EXEC modificar_platillo %s, %s, %s,%s, %s"
                        filtro = (nombre_platillo, desc, precio, j,y)
                        cursor.execute(query, filtro)
                    connection.commit()
            return redirect('/platillos/')
        else:
            with connection.cursor() as cursor:
                    
                    lista_ingredientes= cursor.execute("SELECT * FROM inventario WHERE id_tipoItem=1").fetchall()

                    query="SELECT * FROM platillos WHERE id_platillo= %s"
                    filtro = (id_platillo,)
                    info_general=cursor.execute(query, filtro).fetchall()
                    print(info_general)

                    query="EXEC ingredientes_por_platillo %s"
                    filtro = (id_platillo,)
                    ingredientes=cursor.execute(query, filtro).fetchall()

            connection.commit()

            print("LISTA DE INGREDIENTES:"+str(lista_ingredientes))
            return render(request,'editar_platillo.html', context={
                'id_platillo': info_general[0][0],
                'info_general': info_general,
                'ingredientes':ingredientes,
                'catalogo_ingredientes': lista_ingredientes,
            })

def eliminar_platillo(request, id_platillo):
    if 'empleado_id' not in request.session:
        return redirect('/login')
    else:
        if request.method=='POST':

            return redirect('/platillos/')
        else:
            with connection.cursor() as cursor:
                cursor.execute("EXEC eliminar_platillo %s", str(id_platillo))
            connection.commit()
            return redirect('/platillos/')
        

#------------------------------alquiler----------------------------------  
def alquiler(request):
    if 'empleado_id' not in request.session:
        return redirect('/login')
    else:
        with connection.cursor() as cursor:
            resultados=cursor.execute("exec ver_info_alquileres").fetchall()
            #horas= cursor.execute("SELECT DATEPART(hour, CAST(horaFin AS DATETIME) - CAST(horaInicio AS DATETIME)) AS diferencia_hora FROM alquileres;").fetchall()
            alquileres = []

            for r in resultados:
                alquileres.append({
                    "id": r[0],
                    "title": f"{r[6]} {r[7]}",
                    "start": f"{r[3]} {r[4]}",
                    "end": f"{r[3]} {r[5]}"
                })

        print(alquileres)
        # Si la solicitud es AJAX, devolver los datos en formato JSON
        if request.is_ajax():
            return JsonResponse(alquileres, safe=False)

        return render(request, 'alquiler.html', context={
            'alquileres': json.dumps(alquileres)
        })

def edit_alquiler(request, id_alquiler):
    if 'empleado_id' not in request.session:
        return redirect('/login')
    else:
        if request.method == 'GET':
            with connection.cursor() as cursor:
                query="exec ver_info_alquiler %s"
                filtro = (id_alquiler,)
                cursor.execute(query, filtro)
                info = cursor.fetchall()

            with connection.cursor() as cursor:    
                tipoAlquiler= cursor.execute("SELECT * from tipoAlquiler").fetchall()
                

            hora_Inicio = info[0][4].strftime("%H:%M")
            hora_Fin= info[0][5].strftime("%H:%M")
            fecha_formateada = info[0][3].strftime("%Y-%m-%d")
            
            diferencia = calcular_tiempo(hora_Inicio, hora_Fin)

            return render(request, 'editar_alquiler.html', context={
                'info': info,
                'hora':diferencia,
                'tipoAlquiler':tipoAlquiler,
                'horaInicio': hora_Inicio,
                'horaFin': hora_Fin,
                'fecha': fecha_formateada,
            })
        else:
            cliente= request.POST['nombreCliente']
            fecha = request.POST['fecha']
            horaInicio = formatear_hora(request.POST['horaInicio'])
            horaFin = formatear_hora(request.POST['horaFin'])
            tipoAlquiler = request.POST['id_tipoAlquiler']

            nombreapellido = cliente.split()

            if len(nombreapellido)==3:
                nombreCliente = " ".join(nombreapellido[:1])
                apellidoCliente = " ".join(nombreapellido[-2:])
            else:
                # Tomar los dos primeros elementos de la lista de palabras
                nombreCliente = " ".join(nombreapellido[:2])
                apellidoCliente = " ".join(nombreapellido[-2:])

            print("info: "+ cliente+""+fecha+""+horaInicio+""+horaFin+""+tipoAlquiler)
            with connection.cursor() as cursor:
                sql_query = "exec modificar_alquiler %s, %s, %s, %s, %s, %s, %s"
                nuevos_valores = (id_alquiler,fecha, horaInicio, horaFin, nombreCliente, apellidoCliente, tipoAlquiler)
                cursor.execute(sql_query, nuevos_valores)
            
            connection.commit()
            
            return redirect('/alquiler/')

def add_alquiler2(request):
    if request.method == 'GET':
        with connection.cursor() as cursor:

            tipoAlquiler= cursor.execute("SELECT * FROM tipoAlquiler").fetchall()
        connection.commit()

        return render(request, 'add_alquiler2.html', context={
            'tipoAlquiler': tipoAlquiler,

        })
    else:
        cedula=request.POST['cedula']
        fecha = request.POST['fecha']
        horaInicio = formatear_hora(request.POST['horaInicio'])
        horaFin = formatear_hora(request.POST['horaFin'])
        tipoAlquiler = request.POST['tipoAlquiler']



        with connection.cursor() as cursor:
            sql_query = "exec registrar_alquiler %s, %s, %s, %s, %s"
            valores = (fecha, horaInicio, horaFin, cedula, tipoAlquiler)
            cursor.execute(sql_query, valores)

        connection.commit()

        return redirect('/alquiler/') 
    
def eliminar_alquiler(request,id_alquiler):
    with connection.cursor() as cursor:
        sql_query = "DELETE FROM alquiler WHERE id_alquiler = %s"
        valores = (id_alquiler,)
        cursor.execute(sql_query, valores)

    connection.commit()

    return redirect('/alquiler/')    
#--------------------------clientes--------------------------------

def add_alquiler_cliente(request):
    if request.method == 'GET':
        with connection.cursor() as cursor:
            clientes=cursor.execute("exec VerClientes").fetchall()

            
        return render(request, 'add_alquiler_cliente.html', context={
            'clientes': clientes,
}) 

def add_cliente(request):
    if request.method == 'GET':
        
        return render(request, 'add_cliente.html')
    
        
    else:
        with connection.cursor() as cursor:
            nombre = request.POST['nombre']
            apellido = request.POST['apellido']
            direccion = request.POST['direccion']
            cedula = request.POST['cedula']
            telefono = request.POST['telefono']
            
            with connection.cursor() as cursor:
             cursor.execute("EXEC addCliente @nombre=%s, @apellido=%s, @direccion=%s, @cedula=%s, @telefono=%s",(nombre, apellido, direccion, cedula, telefono))
            #sql_query = "INSERT INTO clientes (nombre, apellido, direccion, cedula, telefono) VALUES (%s, %s, %s,%s, %s)"
            #valores = (request.POST['nombre'], request.POST['apellido'], request.POST['direccion'], request.POST['cedula'],request.POST['telefono'])
            #cursor.execute(sql_query, valores)

        connection.commit()

        return redirect('/add_alquiler_cliente/') 

def edit_cliente(request, id_clientes):
    if request.method == 'GET':
        with connection.cursor() as cursor:
            query="SELECT * FROM clientes WHERE id_cliente = %s"
            filtro = (id_clientes,)
            cursor.execute(query, filtro)

            # Obtiene los resultados
            info = cursor.fetchall()
            print("Info del item:"+str(info))

        #info = Empleado.objects.filter(id_empleado=id_emp)
        return render(request, 'editar_clientes.html', context={
            'info': info,
        })
    else:
        with connection.cursor() as cursor:
        # Define tu consulta SQL de actualización
            sql_query = "UPDATE clientes SET nombre = %s, apellido = %s, direccion=%s, cedula=%s, telefono=%s WHERE id_cliente= %s"
        
        # Define los nuevos valores
            nuevos_valores = (request.POST['nombre'], request.POST['apellido'], request.POST['direccion'], request.POST['cedula'],request.POST['telefono'], id_clientes)

        # Ejecuta la consulta SQL de actualización
            cursor.execute(sql_query, nuevos_valores)

    # Asegúrate de realizar un commit para aplicar los cambios en la base de datos
        connection.commit()
        
        return redirect('/add_alquiler_cliente/')

def eliminar_cliente(request,id_clientes):
    with connection.cursor() as cursor:
        sql_query = "DELETE FROM clientes WHERE id_clientes = %s"
        valores = (id_clientes,)
        cursor.execute(sql_query, valores)

    connection.commit()

    return redirect('/add_alquiler_cliente/') 
#-------------------------------------------------------------------------
def factura_orden(request):
    if request.method == 'GET':
    
        hora_actual = str(datetime.datetime.now())
        print(hora_actual)
        return render(request, 'factura_orden.html', context={
        'hora': hora_actual,
    })
    else:
        return redirect('/')


#----------------------------------ordenes isa---------------------------------------------
def ver_ordenes(request):
    with connection.cursor() as cursor:
        ordenes=cursor.execute("SELECT * FROM orden").fetchall()
    return render(request, 'lista_ordenes.html', context={
            'ordenes': ordenes,
        })

def detalle_orden(request, id_orden):
    with connection.cursor() as cursor:
        # Obtener cantidades
        sql_query = "EXEC total_por_producto %s"
        filtro = (id_orden,)
        cursor.execute(sql_query, filtro)
        orden = cursor.fetchall()

        sql_query2 ="exec gran_total_orden %s"
        filtro = (id_orden,)
        cursor.execute(sql_query2, filtro)
        total = cursor.fetchall()
        
        print(total)
        sql_query3 ="SELECT descripcion FROM ordenes WHERE id_orden= %s;"
        filtro = (id_orden,)
        cursor.execute(sql_query3, filtro)
        notas = cursor.fetchone()
        #print(orden)

    return render(request, 'detalle_orden.html', context={
            'info': orden, 'num': int(id_orden), 
            'grantotal': total[0][2], 'notas':notas[0]
        })


def agregar_orden(request,id_mesa):
    if request.method == 'GET':
        with connection.cursor() as cursor:
            #obtenemos la lista de clientes, platillos, y consumibles del menu
            clientes = cursor.execute("exec VerClientes").fetchall()
            Bebidas = cursor.execute("SELECT * FROM VerMenu").fetchall()
            platillos = cursor.execute("SELECT * FROM platillos").fetchall()
            
        clientes_nombres = [f"{cliente[1]} {cliente[2]}" for cliente in clientes]   
        hora_actual = str(datetime.datetime.now())   

        return render(request, 'generar_orden2.html', 
                      {'bebidas': Bebidas,
                       'platillos': platillos,
                       'hora': hora_actual,
                       'clientes_nombres': clientes_nombres,
                       'id_mesa': id_mesa})
    else:
        #Inventario(Bebidas)
        print("debug")
        cantidad_items= request.POST.getlist('cantidad')
        ids_items= request.POST.getlist('id_producto')
        
        #Platillos
        cantidad_platillo= request.POST.getlist('cantidad_platillo')
        ids_platillos= request.POST.getlist('id_platillo')
        
        desc= request.POST['comentario']
        cliente=str(request.POST['cliente'])
        #---------------------------------------ID DEL CLIENTE-------------------------------------------        
        #Hay que convertir nombre del cliente a un id para ingresar a la orden       
        #Dividir la cadena en palabras
        palabras = cliente.split()
        
        if len(palabras)==3:
            nombreCliente = " ".join(palabras[:1])
        else:
            # Tomar los dos primeros elementos de la lista de palabras
            nombreCliente = " ".join(palabras[:2])
        
        print(nombreCliente)
        
        with connection.cursor() as cursor:
            #id_cliente = cursor.execute("exec buscarClientePorNombre %s ", argumentosbuscar).fetchone()
            
            query="exec buscarClientePorNombre @nombre= %s"
            valores1=(nombreCliente,)
            id =cursor.execute(query, valores1).fetchone()
            id_cliente = id[0]
            print(id)
            

              
        connection.commit()
        #----------------------------------------ID DEL EMPLEADO--------------------------------------
        idempleado=request.session['empleado_id']
        idempleadoint=idempleado.get('empleado_id')
        #------------------------------------------Ingresamos la orden------------------------------------
        with connection.cursor() as cursor:
                # Aquí inserto descripcion y activo en la tabla ORDEN
                queryAddOrden="exec addOrden %s, %s, %s, %s"
                print (str(type(id_mesa)) + str(id_mesa))  
                print (str(type(id_cliente)) +str(id_cliente))  
                print (str(type(idempleadoint))+ str(idempleadoint))  
                print (str(type(desc))+ str(desc))  
                print(queryAddOrden)
                valoresOrden=(id_mesa,id_cliente, idempleadoint,desc)
    
                cursor.execute(queryAddOrden, valoresOrden)

                # Selecciono el ultimo registro en la tabla orden
                ultimaorden = cursor.execute("SELECT TOP 1 * FROM ordenes ORDER BY id_orden DESC;").fetchone()
                id_orden=ultimaorden[0]
        connection.commit()
        print("id_orden: "+str(id_orden))
        
        
        print("orden ya creada")
        #--------------------------------Orden ya creada, aqui comenzamos a meter a item orden-----------------------------------------
        for cantidad, iditem in zip(cantidad_items, ids_items):
            if cantidad != "0":
                with connection.cursor() as cursor:
                # Ejecutar el procedimiento almacenado con la cantidad y el iditem
                    print("tipos")
                    print (str(type(id_orden)) + str(id_orden))  
                    print (str(type(iditem)) + str(iditem))  
                    print (str(type(cantidad)) + str(cantidad))

                    cursor.execute("exec addItemAOrden %s, %s, %s", (id_orden, iditem, cantidad))
            connection.commit()

        for cantidad, idplatillo in zip(cantidad_platillo, ids_platillos):

            if cantidad != "0":
                idPlatilloInt = int(idplatillo.split('+')[1])

                with connection.cursor() as cursor:
                # Ejecutar el procedimiento almacenado con la cantidad y el iditem
                    cursor.execute("exec addPlatilloAOrden %s, %s, %s", (id_orden, idPlatilloInt, cantidad))
                connection.commit()
        return redirect('/mesas/')
       

#----------------------------------------------editar orden--------------------------------------------------
def editar_orden(request,id_orden):
    if request.method == 'GET':
        with connection.cursor() as cursor:
            #obtenemos la lista de clientes, platillos, y consumibles del menu
            resultados = cursor.execute("SELECT * FROM VerMenu").fetchall()
            platillos = cursor.execute("SELECT * FROM platillos").fetchall()
            
            #obtenemos los detalles de la orden
            queryorden="EXEC verOrdenEspecifica %s"
            orden=cursor.execute(queryorden, (id_orden,)).fetchone()
            
        hora_actual = str(datetime.datetime.now())   

        return render(request, 'editar_orden.html', 
                      {'infopro': resultados,
                       'platillos': platillos,
                       'hora': hora_actual,
                       'orden': orden,
                       'id_orden': id_orden})
    else:
        #Inventario(Bebidas)
        cantidad_items= request.POST.getlist('cantidad')
        ids_items= request.POST.getlist('id_producto')
        
        #Platillos
        cantidad_platillo= request.POST.getlist('cantidad_platillo')
        ids_platillos= request.POST.getlist('id_platillo')
        
        desc= request.POST['comentario']

        print(desc)
        #------------------------idorden
        with connection.cursor() as cursor:
                # Selecciono el ultimo registro en la tabla orden
                ultimaorden = cursor.execute("SELECT TOP 1 * FROM ordenes ORDER BY id_orden DESC;").fetchone()
                id_orden=ultimaorden[0]
        connection.commit()
        
        #-----------------------actualizando comentario
        with connection.cursor() as cursor:
                querycom="exec cambiarComentarioOrden @idorden=%s, @desc= %s"
                val=(id_orden, desc)

                cursor.execute(querycom,val)
        connection.commit()
        
        #-----------------------ingesar a la orden
        for cantidad, iditem in zip(cantidad_items, ids_items):

            if cantidad != 0:
                with connection.cursor() as cursor:
                # Ejecutar el procedimiento almacenado con la cantidad y el iditem
                    print("tipos")
                    print (str(type(id_orden)) + str(id_orden))  
                    print (str(type(iditem)) + str(iditem))  
                    print (str(type(cantidad)) + str(cantidad))
                    cursor.execute("exec addItemAOrden %s, %s, %s", (id_orden, iditem, cantidad))
            connection.commit()

        for cantidad, idplatillo in zip(cantidad_platillo, ids_platillos):

            if cantidad != 0:
                idPlatilloInt = int(idplatillo.split('+')[1])

                with connection.cursor() as cursor:
                # Ejecutar el procedimiento almacenado con la cantidad y el iditem
                    cursor.execute("exec addPlatilloAOrden %s, %s, %s", (id_orden, idPlatilloInt, cantidad))
                connection.commit()
        return redirect('/mesas/') 
################ HASTA AQUÍ LLEGA AGREGAR_ORDEN #############################

#---------------------facturas alquiler------------------------------------------
def ver_facturas_alquiler(request):
    with connection.cursor() as cursor:
        facturas=cursor.execute("F").fetchall()
    return render(request, 'facturas_alquiler.html', context={
            'facturas': facturas,
        })

def add_factura_alquiler(request):
    if request.method == 'GET':
        return render(request, 'add_factura_alquiler.html')
    else:
        with connection.cursor() as cursor:

            #Hay que actualizar 3 tablas al facturar: factura, factura_empleado y detalle_alquiler
            #1) actualizando factura
            sql_query = "INSERT INTO factura (fecha, num_factura, id_empleado, id_clientes, alcoholica) VALUES (%s, %s, %s,%s, %s)"
            valores = (request.POST['fecha'], request.POST['num_factura'], request.POST['id_empleado'], request.POST['id_clientes'],0)
            cursor.execute(sql_query, valores)

            #2) actualizando factura_empleado
             # Selecciono el ultimo registro en la tablf
            id_factura_ultima = cursor.execute("SELECT TOP 1 * FROM factura ORDER BY id_factura DESC;").fetchone()
             #añadiendo el registro
            sql_query2="INSERT INTO factura_empleado (id_factura, id_empleado) VALUES (%s, %s)"
            valores2 = (id_factura_ultima[0], request.POST['id_empleado'])
            cursor.execute(sql_query2, valores2)

            #3) actualizando detalle_alquiler
             #obteniendo el tiempo total(horas) de la tabla alquiler
            id_alquiler=request.POST['id_alquiler']
            sql_queryhoras=cursor.execute("SELECT horas FROM alquiler where id_alquiler=%s;" %id_alquiler).fetchone()
            
             #obteniendo el total a pagar
            id_total = cursor.execute("SELECT a.horas * t.tarifa AS total FROM alquiler a JOIN tipoAlquiler t ON a.id_tipoAlquiler = t.id_tipoAlquiler WHERE id_alquiler=%s;" %id_alquiler).fetchone()
             #ahora si metiendo en detalle alquiler
            print(id_total[0])
            sql_query3="INSERT INTO detalle_alquiler (cantidad_tiempo, total, id_factura, id_alquiler) VALUES (%s, %s,%s,%s)"
            valores3 = (sql_queryhoras[0], id_total[0],id_factura_ultima[0],id_alquiler)
            cursor.execute(sql_query3, valores3)
        connection.commit()

        return redirect('/facturas_alquiler/') 


#---------------------mesas-----------------------------------------
def mesas(request):
    #Arreglo para mostrar el numero de mesas
    mesas = [1, 2, 3, 4, 5]

    with connection.cursor() as cursor:
        sql_query = "exec VerOrdenesActivas"
        ordenes=cursor.execute(sql_query).fetchall() 


    return render(request, 'mesas.html', context={
            'ordenes': ordenes,
            'mesas': mesas,
        })


def mesa_orden(request, id_mesa):
    if request.method == 'GET':
        with connection.cursor() as cursor:
            query="exec VerOrdenesActivasMesa @mesa= %s"
            
            mesa=(id_mesa,)
            cursor.execute(query, mesa)
            ordenes=cursor.fetchall()
           
            print(ordenes)

        return render(request, 'mesa_orden.html', context={
            'ordenes': ordenes,
            'id_mesa': id_mesa,        
        })

# Formatea la hora para almacenarlo en sql server
def formatear_hora(hora):
    hora_struct = datetime.strptime(hora, '%H:%M')
    # Obtener el formato deseado para almacenar en SQL Server
    hora_formateada = hora_struct.strftime('%H:%M:%S')

    return hora_formateada

def calcular_tiempo(inicio,fin):
    # Convierte las cadenas a objetos datetime
    hora_Inicio2 = datetime.strptime(inicio, "%H:%M")
    hora_Fin2 = datetime.strptime(fin, "%H:%M")

    # Calcula la diferencia
    diferencia = hora_Fin2 - hora_Inicio2 

    return diferencia
