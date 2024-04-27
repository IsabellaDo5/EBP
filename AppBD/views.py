from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.forms import *
from django.contrib.auth import login, authenticate, logout
from django.db import connection
import bcrypt
import datetime

# Create your views here.
def registro(request):
    if request.method=='POST':
        return redirect('/')
    else:
        return render(request, 'registro.html')

def login(request):
    if request.method=='POST':
        return redirect('/')
    else:
        return render(request, 'login.html')
    
def cerrar_sesion(request):
    logout(request)
    # Redirige a la página que desees después de cerrar sesión
    return redirect('/')

def inicio(request):

    '''if request.user.is_authenticated:
        return render(request, 'index.html', {'usuario': request.user})
    else:
        return redirect('signin/')'''
    return render(request, 'index.html', {'usuario': request.user})


def empleados(request):
    #trabajadores = Empleado.objects.all().values
    with connection.cursor() as cursor:
        resultados=cursor.execute("SELECT * FROM empleados").fetchall()
         
    print(resultados)    
    return render(request, 'empleados.html', context={
        'trab': resultados,
    })

def edit_empleados(request, id_emp):
    if request.method == 'GET':
        with connection.cursor() as cursor:
            query="SELECT * FROM empleados WHERE id_empleado = %s"
            filtro = (id_emp,)
            cursor.execute(query, filtro)

            # Obtiene los resultados
            info = cursor.fetchall()
            print("Info del usuario:"+str(info))

        #info = Empleado.objects.filter(id_empleado=id_emp)
        return render(request, 'editar_empleados.html', context={
            'info': info,
        })
    else:
        with connection.cursor() as cursor:
        # Define tu consulta SQL de actualización
            sql_query = "UPDATE empleados SET nombre = %s, apellido = %s, direccion = %s, cedula = %s, telefono = %s, sexo= %s  WHERE id_empleado = %s"
        
        # Define los nuevos valores
            nuevos_valores = (request.POST['nombre'], request.POST['apellido'], request.POST['direccion'], request.POST['cedula'], request.POST['telefono'], request.POST['sexo'], id_emp)

        # Ejecuta la consulta SQL de actualización
            cursor.execute(sql_query, nuevos_valores)

    # Asegúrate de realizar un commit para aplicar los cambios en la base de datos
        connection.commit()
        
        return redirect('/empleados/')
    
def agregar_empleado(request):
    if request.method == 'GET':

        with connection.cursor() as cursor:
            roles= cursor.execute("SELECT * FROM roles").fetchall()

        return render(request, 'add_empleados.html', context={
            'lista_roles':roles,
        })
    else:

        password_flat = request.POST['password']

        password = bcrypt.hashpw(password_flat,bcrypt.gensalt())

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
    with connection.cursor() as cursor:
        resultados=cursor.execute("EXEC ver_inventario").fetchall()
         
    print(resultados)    
    return render(request, 'inventario.html', context={
        'trab': resultados,
    })

def agregar_inventario(request):
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
        sql_query = "DELETE FROM item WHERE id_item = %s"
        valores = (id_item,)
        cursor.execute(sql_query, valores)

    connection.commit()

    return redirect('/inventario/')
    
def edit_inventario(request, id_item):
    if request.method == 'GET':
        with connection.cursor() as cursor:
            query="EXEC obtener_info_item %s"
            filtro = (id_item,)
            cursor.execute(query, filtro)

            # Obtiene los resultados
            info = cursor.fetchall()
        
        with connection.cursor() as cursor:
            catalogo_tipoItem = cursor.execute("SELECT nombre FROM tipoItem").fetchall()

        #info = Empleado.objects.filter(id_empleado=id_emp)
        return render(request, 'editar_item.html', context={
            'info': info,
            'catalogo_tipoItem': catalogo_tipoItem,
        })
    else:
        try:
            unidad_medida= request.POST['unidad_medida']
        except:
            unidad_medida=""

        with connection.cursor() as cursor:
            sql_query = "EXEC editar_info_item %s,%s,%s,%s,%s,%s"
            nuevos_valores = (request.POST['nombre'], request.POST['precio'],request.POST['cantidad'],unidad_medida, request.POST['id_tipoItem'],  id_item)
            cursor.execute(sql_query, nuevos_valores)
        connection.commit()
        
        return redirect('/inventario/')    
#-----------------------------platillos----------------------------------

def add_platillo(request):
    if request.method=='GET':
        with connection.cursor() as cursor:
            lista_ingredientes= cursor.execute("SELECT * FROM inventario WHERE id_tipoItem=1").fetchall()
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
        return redirect('/')

#------------------------------alquiler----------------------------------  
def alquiler(request):
    with connection.cursor() as cursor:
        resultados=cursor.execute("SELECT a.*, c.*, d.nombre AS nombrealq FROM alquiler a JOIN clientes c ON a.id_clientes = c.id_clientes JOIN tipoAlquiler d ON a.id_tipoAlquiler=d.id_tipoAlquiler;").fetchall()
         
    print(resultados)    
    return render(request, 'alquiler.html', context={
        'alquiler': resultados,
}) 

def edit_alquiler(request, id_alquiler):
    if request.method == 'GET':
        with connection.cursor() as cursor:
            query="SELECT * FROM alquiler WHERE id_alquiler = %s"
            filtro = (id_alquiler,)
            cursor.execute(query, filtro)

            # Obtiene los resultados
            info = cursor.fetchall()
            print("Info del item:"+str(info))

        #info = Empleado.objects.filter(id_empleado=id_emp)
        return render(request, 'editar_alquiler.html', context={
            'info': info,
        })
    else:
        with connection.cursor() as cursor:
        # Define tu consulta SQL de actualización
            sql_query = "UPDATE alquiler SET horas = %s, id_tipoAlquiler = %s, id_clientes=%s WHERE id_alquiler= %s"
        
        # Define los nuevos valores
            nuevos_valores = (request.POST['horas'], request.POST['id_tipoAlquiler'], request.POST['id_clientes'], id_alquiler)

        # Ejecuta la consulta SQL de actualización
            cursor.execute(sql_query, nuevos_valores)

    # Asegúrate de realizar un commit para aplicar los cambios en la base de datos
        connection.commit()
        
        return redirect('/alquiler/')

def add_alquiler2(request):
    if request.method == 'GET':
        return render(request, 'add_alquiler2.html')
    else:
        with connection.cursor() as cursor:
            sql_query = "INSERT INTO alquiler (horas, id_tipoAlquiler, id_clientes) VALUES (%s, %s, %s)"
            valores = (request.POST['horas'], request.POST['id_tipoAlquiler'], request.POST['id_clientes'])
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
    with connection.cursor() as cursor:
        clientes=cursor.execute("sp_get_clientes").fetchall()
         
    print(clientes)    
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
             cursor.execute("EXEC sp_insert_cliente @nombre=%s, @apellido=%s, @direccion=%s, @cedula=%s, @telefono=%s",(nombre, apellido, direccion, cedula, telefono))
            #sql_query = "INSERT INTO clientes (nombre, apellido, direccion, cedula, telefono) VALUES (%s, %s, %s,%s, %s)"
            #valores = (request.POST['nombre'], request.POST['apellido'], request.POST['direccion'], request.POST['cedula'],request.POST['telefono'])
            #cursor.execute(sql_query, valores)

        connection.commit()

        return redirect('/add_alquiler_cliente/') 

def edit_cliente(request, id_clientes):
    if request.method == 'GET':
        with connection.cursor() as cursor:
            query="SELECT * FROM clientes WHERE id_clientes = %s"
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
            sql_query = "UPDATE clientes SET nombre = %s, apellido = %s, direccion=%s, cedula=%s, telefono=%s WHERE id_clientes= %s"
        
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
        total = cursor.fetchone()

        sql_query3 ="SELECT descripcion FROM orden WHERE id_orden= %s;"
        filtro = (id_orden,)
        cursor.execute(sql_query3, filtro)
        notas = cursor.fetchone()
        #print(orden)

    return render(request, 'detalle_orden.html', context={
            'info': orden, 'num': int(id_orden), 
            'grantotal': total[0], 'notas':notas[0]
        })


def agregar_orden(request):
    if request.method == 'GET':
        with connection.cursor() as cursor:
            resultados=cursor.execute("SELECT * FROM inventario").fetchall()
        
        hora_actual = str(datetime.datetime.now())   

        return render(request, 'generar_orden.html', {'infopro': resultados, 'hora': hora_actual})
    else:
        cant= request.POST.getlist('cantidad')
        ids= request.POST.getlist('id_producto')
        coment= request.POST['comentario']

        with connection.cursor() as cursor:
                # Aquí inserto descripcion y activo en la tabla ORDEN
                sql_query1 = "INSERT INTO orden(descripcion, activa) VALUES (%s, %s)"
                valores1 = (coment, 1)
                cursor.execute(sql_query1, valores1)

                # Selecciono el ultimo registro en la tabla orden
                id_orden = cursor.execute("SELECT TOP 1 * FROM orden ORDER BY id_orden DESC;").fetchone()
        connection.commit()
        print("id_orden: "+str(id_orden))
        
        
        ##################### PARA INSERTAR A ITEM_ORDEN ######################################
        for x in range(len(cant)):
            
            if int(cant[x]) != 0:
                with connection.cursor() as cursor:
                    #Inserto registros a la tabla item_orden
                    sql_query = "INSERT INTO item_orden(id_item, id_orden,cantidad) VALUES (%s, %s, %s)"
                    valores = (ids[x], id_orden[0],cant[x])
                    cursor.execute(sql_query, valores)

                connection.commit()
            elif int(cant[x])==0:
                x+=1
        
        ##################### PARA ACTUALIZAR LA CANTIDAD DE STOCK ##########################
        for j,y in zip(ids,cant):

            if int(y) != 0:
                with connection.cursor() as cursor:
                # Obtener cantidades

                    sql_query = "SELECT cantidad FROM item WHERE id_item = %s"
                    filtro = (j,)
                    cursor.execute(sql_query, filtro)
                    cant_inicial = cursor.fetchone()

                    cant_nueva = int(cant_inicial[0])- int(y)
                    print("Id: "+str(j)+" cantidad nueva: "+str(cant_nueva))

                # Actualizar cantidades
                    sql_query = "UPDATE item SET cantidad = %s WHERE id_item = %s"
                    nueva_cant = (cant_nueva, j)
                    cursor.execute(sql_query, nueva_cant)

                connection.commit()
        return redirect('/orden_detalle/'+str(id_orden[0]))
    
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


#---------------------facturas orden------------------------------------------