import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.forms import *
from django.contrib.auth import login, logout
from django.db import OperationalError, connection
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import JsonResponse
import subprocess
import os

from django.utils.text import slugify
import datetime as datetimeglobal  # Alias para el módulo global
from datetime import datetime   # Alias para la clase específica
import time
import hashlib
from django.conf import settings

# FUNCIONES ASINCRONAS  
def items_mas_vendidos(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT TOP 5 SUM(o.cantidad) AS CantidadVendida, inv.nombre FROM inventario inv INNER JOIN orden_detalle o ON inv.id_item = o.id_item GROUP BY inv.nombre ORDER BY CantidadVendida DESC")
            # Obtiene los nombres de las columnas, 
            columns = [col[0] for col in cursor.description]
            # Obtener todos los resultados de la consulta como una lista de diccionarios [{"key":value, "key2": value2}]
            rows = [dict(zip(columns, row)) for row in cursor.fetchall()]

    except OperationalError as e:
        # Envia un error si la consulta falla
        return JsonResponse({'error': str(e)}, status=500)
    # Devuelve los datos como JSON
    return JsonResponse(rows, safe=False)


def platillos_mas_vendidos(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT TOP 5 SUM(o.cantidad) as CantidadVendida ,p.nombre from platillos p INNER JOIN orden_detalle o ON p.id_platillo = o.id_platillo GROUP BY p.nombre ORDER BY CantidadVendida DESC")
            columns = [col[0] for col in cursor.description]
            rows = [dict(zip(columns, row)) for row in cursor.fetchall()]

    except OperationalError as e:
        return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse(rows, safe=False)




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
                query= "select id_empleado, id_rol from empleados where id_cuenta = %s"
                filtro = (user[0][0],)
                cursor.execute(query, filtro)
                info_empleado_actual= cursor.fetchall()
                

                
                user_info={ 'empleado_id': info_empleado_actual[0][0]
                }
                      

            request.session['empleado_id'] = user_info
            request.session['id_rol'] =info_empleado_actual[0][1]
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
            'MEDIA_URL': settings.MEDIA_URL,
        })

# Muestra la lista de empleados
def empleados(request):
    if 'empleado_id' not in request.session:
        return redirect('/login')
    else:
        with connection.cursor() as cursor:
            resultados=cursor.execute("SELECT * FROM empleados where activo=1" ).fetchall()
            
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
        sql_query = "UPDATE empleados set activo = 0 WHERE id_empleado= %s"
        valores = (id_emp,)
        cursor.execute(sql_query, valores)

    connection.commit()

    return redirect('/empleados/')


#esta parte de aca es lo de lo sempleados inactivos, para mostrarlos y reactivarlos
# Muestra la lista de empleados
def empleados_desactivados(request):
    if 'empleado_id' not in request.session:
        return redirect('/login')
    else:
        with connection.cursor() as cursor:
            resultados=cursor.execute("SELECT * FROM empleados where activo=0" ).fetchall()
            
        print(resultados)    
        return render(request, 'empleados_desactivados.html', context={
            'trab': resultados,
        })
    
def reactivar_empleado(request, id_emp):
    with connection.cursor() as cursor:
        sql_query = "UPDATE empleados set activo = 1 WHERE id_empleado= %s"
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
                    'MEDIA_URL': settings.MEDIA_URL,
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
        sql_query = "Update inventario set activo=0 WHERE id_item = %s "
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
                'catalogo_medidas':catalogo_medidas,
                'MEDIA_URL': settings.MEDIA_URL,
            })
        else:
            cambio = request.POST["cambio_img"]
            try:
                unidad_medida= request.POST['unidad_medida']
            except:
                unidad_medida=""

            with connection.cursor() as cursor:

                img = cursor.execute("SELECT imagen from inventario WHERE id_item = %s", (id_item,)).fetchall()
                print("UNIDAD DE MEDIDA: "+unidad_medida)
                sql_query = "EXEC editar_info_item %s, %s, %s, %s, %s, %s"
                nuevos_valores = (request.POST['nombre'], request.POST['precio'],request.POST['cantidad'],unidad_medida, request.POST['id_tipoItem'],  id_item)
                cursor.execute(sql_query, nuevos_valores)
                
            connection.commit()

            # comprueba si ya existe una imagen en la db
            if len(img[0][0]) != 0:
                try:
                    request.FILES['icon']
                    eliminar_imagen(request,1,img[0][0])
                    upload_image(request,id_item,1)
                except:
                    print("No se subió ninguna img")
            # Si no existe ninguna imagen entonces se sube la imagen sin más
            else:
                upload_image(request,id_item,1)
            upload_image(request, id_item, 1)
            
            return redirect('/inventario/')
        

#esto va a aser para cuando "elimines un itme", con esto lo restauras
def reactivar_item(request,id_item):
    with connection.cursor() as cursor:
        sql_query = "Update inventario set activo=1 WHERE id_item = %s "
        valores = (id_item,)
        cursor.execute(sql_query, valores)

    connection.commit()

    return redirect('/inventario/')

#aqui los items eliminados
def inventario_eliminado(request):
    if 'empleado_id' not in request.session:
        return redirect('/login')
    else:
        if request.method == 'GET':
            with connection.cursor() as cursor:
                resultados=cursor.execute("EXEC ver_inventario_eliminado").fetchall()
            
                print(resultados)    
                return render(request, 'inventario_eliminado.html', context={
                    'trab': resultados,
                    'MEDIA_URL': settings.MEDIA_URL,
                })

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
                'MEDIA_URL': settings.MEDIA_URL,
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
                img = cursor.execute("SELECT imagen from platillos WHERE id_platillo = %s", (id_platillo,)).fetchall()
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
            print("IMAGEN: "+ str(img[0][0]))
            # comprueba si ya existe una imagen en la db
            if img[0][0] != None:
                try:
                    request.FILES['icon']
                    eliminar_imagen(request,2,img[0][0])
                    upload_image(request,id_platillo,2)
                except:
                    print("No se subió ninguna img")
            # Si no existe ninguna imagen entonces se sube la imagen sin más
            else:
                print("No existe img en la db, entra a segundo if")
                upload_image(request,id_platillo,2)
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
            sql_query = "UPDATE clientes SET nombre = %s, apellido = %s, direccion=%s, cedula=%s, telefono=%s , activo = %s WHERE id_cliente= %s"
        
        # Define los nuevos valores
            nuevos_valores = (request.POST['nombre'], request.POST['apellido'], request.POST['direccion'], request.POST['cedula'],request.POST['telefono'],1, id_clientes)

        # Ejecuta la consulta SQL de actualización
            cursor.execute(sql_query, nuevos_valores)

    # Asegúrate de realizar un commit para aplicar los cambios en la base de datos
        connection.commit()
        
        return redirect('/add_alquiler_cliente/')

def eliminar_cliente(request,id_clientes):
    with connection.cursor() as cursor:
        sql_query = "Update clientes set activo = 0 WHERE id_cliente = %s"
        valores = (id_clientes,)
        cursor.execute(sql_query, valores)

    connection.commit()

    return redirect('/add_alquiler_cliente/') 
#-------------------------------------------------------------------------
def factura_orden(request):
    if request.method == 'GET':
    
        hora_actual = str(datetimeglobal.datetime.now())
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
    if request.method == 'GET':
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

          sql_query4 ="exec verOrdenEspecifica %s"
          filtro = (id_orden,)
          cursor.execute(sql_query4, filtro)
          detallesOrden = cursor.fetchall()

          fecha = str(datetimeglobal.datetime.now().strftime('%Y-%m-%d'))
          print(fecha)
        return render(request, 'detalle_orden.html', context={
            'fecha': fecha,
            'info': orden, 'num': int(id_orden),
            'detallesOrden': detallesOrden,
            'grantotal': total[0][2], 'notas':notas[0],
            'id_orden': id_orden
        })
    else:
       #necesito guardar en la bd ka factura, pero antes necesito obtener todo 
       #IMPORTANTE=Necesitas ver si la orden esta activa o no para ver si actualizas la factura o creas una nueva
       #fecha-------
       fecha = str(datetimeglobal.datetime.now().strftime('%Y-%m-%d'))
       print("facturafecha: " +fecha)
       
       with connection.cursor() as cursor:
            #Estado-----
            estadoOrden=int(request.POST['estado'])
            #descuento-------
            descuento=float(request.POST['descuentoFactura'])
            print("decsuento: " +str(descuento)+ str(type(descuento)))
            #alcoholica-------
            acloholica= cursor.execute("exec revisarOrdenAlcoholica %s",(id_orden,)).fetchone()
            alcoholicaInt=acloholica[0]
            #id_empleado-------
            idempleado=request.session['empleado_id']
            idempleadoint=idempleado.get('empleado_id')
            #id_cliente-------
            nombreCliente=str(request.POST['nombreCliente'])
            print("nombre del cliente: " +str(nombreCliente)+ str(type(nombreCliente)))
            cliente=cursor.execute("exec verClienteEspecificoNombre %s",(nombreCliente,)).fetchone()
            id_cliente=cliente[0]
            print("id del cliente: " +str(id_cliente)+ str(type(id_cliente)))
            #id_alquiler(en este caso va a ser null)-------
            id_alquiler=None
            #abono-------
            abono=float(request.POST['abono'])
            print("abono: " +str(abono)+ str(type(abono)))



            if(estadoOrden==1):
                cursor.execute("EXEC facturarOrden @fecha=%s, @descuento=%s, @alcoholica=%s, @idEmpleado=%s, @idCliente=%s, @idOrden=%s, @idAlquiler=%s, @abono=%s"
                                               ,(fecha,descuento,alcoholicaInt,idempleadoint,id_cliente,id_orden,id_alquiler,abono))
            elif(estadoOrden==0):
                cursor.execute("EXEC editarFactura @fecha=%s, @descuento=%s, @alcoholica=%s, @idEmpleado=%s, @idCliente=%s, @idOrden=%s, @idAlquiler=%s, @abono=%s"
                                               ,(fecha,descuento,alcoholicaInt,idempleadoint,id_cliente,id_orden,id_alquiler,abono))
       connection.commit()
       return redirect('/mesas/')


    


def agregar_orden(request,id_mesa):
    if request.method == 'GET':
        with connection.cursor() as cursor:
            #obtenemos la lista de clientes, platillos, y consumibles del menu
            clientes = cursor.execute("exec VerClientes").fetchall()
            Bebidas = cursor.execute("SELECT * FROM VerMenu").fetchall()
            platillos = cursor.execute("SELECT * FROM platillos").fetchall()
            
        clientes_nombres = [f"{cliente[1]} {cliente[2]}" for cliente in clientes]   
        hora_actual = str(datetimeglobal.datetime.now().strftime('%Y-%m-%d'))

        return render(request, 'generar_orden2.html', 
                      {'bebidas': Bebidas,
                       'platillos': platillos,
                       'hora': hora_actual,
                       'clientes_nombres': clientes_nombres,
                       'id_mesa': id_mesa,
                       'MEDIA_URL': settings.MEDIA_URL,})
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
    #el trabajo duro de esto lo hago en javascript y en funciones.py
    if request.method == 'GET':
        with connection.cursor() as cursor:
            #obtenemos la lista de clientes, platillos, y consumibles del menu
            bebidas = cursor.execute("SELECT * FROM VerMenu").fetchall()
            platillos = cursor.execute("SELECT * FROM platillos").fetchall()
            detallesOrden = cursor.execute("exec verDetallesDeOrden %s ", (id_orden,)).fetchall()
            #obtenemos los detalles de la orden
            queryorden="EXEC verOrdenEspecifica %s"
            orden=cursor.execute(queryorden, (id_orden,)).fetchone()
            
        hora_actual = str(datetimeglobal.datetime.now())   
        print(platillos)
        return render(request, 'editar_orden.html', 
                      {'bebidas': bebidas,
                       'platillos': platillos,
                       'hora': hora_actual,
                       'orden': orden,
                       'id_orden': id_orden,
                       'detallesOrden': detallesOrden})
    else:
        desc= request.POST['comentario']

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
    
def ordenes_inactivas(request):
    with connection.cursor() as cursor:
        sql_query = "exec VerOrdenesInactivas"
        ordenes=cursor.execute(sql_query).fetchall() 


    return render(request, 'ordenes_inactivas.html', context={
            'ordenes': ordenes,
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

def upload_image(request, id_item, accion):

    if request.method == 'POST':

        if accion == 1:
            title = "item_"+str(id_item)
        elif accion == 2:
            title = "platillo_"+str(id_item)

        try:
            image_file = request.FILES["icon"]

            print("Imagen retorno"+str(image_file))
            # Renombrar la imagen
            original_filename = image_file.name
            extension = original_filename.split('.')[-1]
            new_filename = f"{slugify(title)}.{extension}"
            
            # Guarda el archivo en el sistema de archivos
            upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploads')
            os.makedirs(upload_dir, exist_ok=True)
            file_path = os.path.join(upload_dir, new_filename)
            with open(file_path, 'wb+') as destination:
                for chunk in image_file.chunks():
                    destination.write(chunk)

            if accion == 1:
                # Guarda la imagen en la tabla de inventario
                with connection.cursor() as cursor:
                    cursor.execute(
                        "UPDATE inventario  SET imagen = %s WHERE id_item = %s;",
                        [ 'uploads/' + new_filename, id_item]
                    )
            if accion == 2:
                print("Entrando a guardar imagen del platillo con id: "+str(id_item))
                # Guarda la imagen en la tabla de platillos
                with connection.cursor() as cursor:
                    cursor.execute(
                        "UPDATE platillos SET imagen = %s WHERE id_platillo = %s;",
                        [ 'uploads/' + new_filename, id_item]
                    )
        except:
            print("No se subió ninguna imagen.")

def eliminar_imagen(request, accion, ruta_item):

    if accion == 1:
        ruta_imagen = os.path.join(settings.MEDIA_ROOT, ruta_item)
    elif accion == 2: 
        ruta_imagen = os.path.join(settings.MEDIA_ROOT, ruta_item)

    print(ruta_imagen)
    # Verificar si el archivo existe y eliminarlo
    if os.path.isfile(ruta_imagen):
        os.remove(ruta_imagen)
        return HttpResponse('Imagen eliminada correctamente')
    else:
        return HttpResponse('La imagen no existe', status=404)
    
def eliminar_imagen_bd(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        id_item = data.get('id')
        nuevo_valor = data.get('nuevo_valor')

        print("ID:"+str(id_item))
        print("nUEVO VALOR :"+str(nuevo_valor))
        with connection.cursor() as cursor:
            img = cursor.execute("SELECT imagen from inventario WHERE id_item = %s", (id_item,)).fetchall()
            cursor.execute(
                "UPDATE inventario  SET imagen = %s WHERE id_item = %s;",
                    [ nuevo_valor, id_item]
                )
            
        eliminar_imagen(request, 1,str(img[0][0]))
        return JsonResponse({'status': 'success'})
    


def respaldos(request):
    if request.method == 'GET':
        return render(request, 'respaldos.html', context={
        })
    else:
        with connection.cursor() as cursor:
            carpeta=request.POST['carpeta']
            print(carpeta)
            respaldo=request.POST['nombreRespaldo']
            print(respaldo)
        connection.commit()
        bat_script = f"""
@echo off

rem Configuración de variables
set server=DESKTOP-905LS6C\SQLEXPRESS
set user=sa
set password=123456789
set database=EBP
set backup_file={carpeta}{respaldo}.bak rem Ruta completa con el nombre del archivo

rem Ejecutar el comando sqlcmd para realizar la copia de seguridad
sqlcmd -S DESKTOP-905LS6C\SQLEXPRESS -U sa -P 123456789 -Q "BACKUP DATABASE [EBP] TO DISK = '{carpeta}{respaldo}.bak'"

rem Salir del script
exit /b 0
"""
        
        # Guardar el contenido en un archivo .bat
        nombre_archivo = 'backup_script.bat'
        with open(nombre_archivo, 'w') as archivo:
            archivo.write(bat_script)

        # Ejecutar el archivo .bat usando subprocess
        try:
            resultado = subprocess.run([nombre_archivo], shell=True, capture_output=True, text=True)
            print(resultado.stdout)
            print(resultado.stderr)
        except subprocess.CalledProcessError as e:
            print(f"Error al ejecutar el script: {e}")
        finally:
            # Eliminar el archivo .bat después de usarlo (opcional)
            import os
            os.remove(nombre_archivo)
        return redirect('/') 


def respaldos_automaticos(request):
    if request.method == 'GET':
        return render(request, 'respaldos_automaticos.html', context={
        })
    else:
        with connection.cursor() as cursor:
            carpeta=request.POST['carpeta']
            print(carpeta)
            respaldo=request.POST['nombreRespaldo']
            print(respaldo)
            hora=request.POST['horaRespaldo']
            print(hora)
        connection.commit()
        bat_script = f"""
            @echo off

            rem Configuración de variables
            set server=DESKTOP-905LS6C\SQLEXPRESS
            set user=sa
            set password=123456789
            set database=EBP
            set backup_file={carpeta}{respaldo}.bak rem Ruta completa con el nombre del archivo

            rem Ejecutar el comando sqlcmd para realizar la copia de seguridad
            sqlcmd -S DESKTOP-905LS6C\SQLEXPRESS -U sa -P 123456789 -Q "BACKUP DATABASE [EBP] TO DISK = '{carpeta}{respaldo}.bak'"

            rem Salir del script
            exit /b 0
        """
        # Guardar el contenido en un archivo .bat
        #Esta direccione es estatica y sinceramente me gustaria hacerlo en C:\ pero no le quiero 
        #otorgar permisos al servidor para que escriba en el disco root
        #Si estas leyendo esto: cambia esta direccion estatica a lo que te plazca
        nombre_archivo = "F:\\tarea_respaldo_automatico.bat"

        #estas son mis credenciales de windows, tambien vas a tener que cambiarlas
        #TIENE QUE HABER UNA MEJOR MANERA DE HACER ESTO
        #Si lo hay y es usando la bd, talvez mas adelante lo haga

        #WINDOWS
        usuario="admin123"
        contraseña="123"
        #ruta_archivo="C:\\tarea_respaldo_automatico.bat"
        with open(nombre_archivo, 'w') as archivo:
            archivo.write(bat_script)

        # Actualizar o crear la tarea utilizando schtasks
        task_name = "crear_backup"
        comandoActualizar = f'schtasks /change /tn "{task_name}" /tr "{nombre_archivo}" /st {hora} /ru {usuario} /rp {contraseña}'
        comandoCrear = f'schtasks /create /tn "{task_name}" /tr "{nombre_archivo}" /sc daily /st {hora} /ru {usuario} /rp {contraseña}'

        # Intenta actualizar la tarea existente
        resultado = os.system(comandoActualizar)
        if resultado != 0:
            # Si la actualización falla (por ejemplo, si la tarea no existe), crea la tarea
            os.system(comandoCrear)

        return redirect('/') 



