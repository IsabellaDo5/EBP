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
# Create your views here.

#funcion para obtener la medida de los ingredientes en los platillos
def obtenerMedidaItem(request, nombreItem):
    with connection.cursor() as cursor:
        cursor.execute("exec VerMedidaItem %s", (nombreItem,))
        query = cursor.fetchall()
        # Convierte los resultados a una lista de diccionarios
        medidaNombre = [{'medidaNombre': query[0]}]
    return JsonResponse(medidaNombre, safe=False)

#-----------------Funciones para añadir y restar items y platillos a las ordenes---------------------

# Items
def AñadirItemAOrden(request, idOrden, idItem):
    try:
        with connection.cursor() as cursor:
            query = "exec AñadirItemAOrden @id_orden = %s, @id_item = %s"
            valores = (idOrden, idItem,)
            cursor.execute(query, valores)
        connection.commit()
        return JsonResponse({'status': 'success', 'message': 'Item añadido a la orden'}, status=200)
    except Exception as e:
        print(f"Error al añadir item a la orden: {e}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

def RestarItemAOrden(request, idOrden, idItem):
    try:
        with connection.cursor() as cursor:
            query = "exec RestarItemAOrden @id_orden = %s, @id_item = %s"
            valores = (idOrden, idItem,)
            cursor.execute(query, valores)
        connection.commit()
        return JsonResponse({'status': 'success', 'message': 'Item restado de la orden'}, status=200)
    except Exception as e:
        print(f"Error al restar item de la orden: {e}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

# Platillos
def AñadirPlatilloAOrden(request, idOrden, idPlatillo):
    try:
        with connection.cursor() as cursor:
            query = "exec AñadirPlatilloAOrden @id_orden = %s, @id_platillo = %s"
            print(idPlatillo)
            valores = (idOrden, idPlatillo,)
            cursor.execute(query, valores)
        connection.commit()
        return JsonResponse({'status': 'success', 'message': 'Platillo añadido a la orden'}, status=200)
    except Exception as e:
        print(f"Error al añadir platillo a la orden: {e}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

def RestarPlatilloAOrden(request, idOrden, idPlatillo):
    try:
        with connection.cursor() as cursor:
            query = "exec RestarPlatilloAOrden @id_orden = %s, @id_platillo = %s"
            valores = (idOrden, idPlatillo,)
            cursor.execute(query, valores)
        connection.commit()
        return JsonResponse({'status': 'success', 'message': 'Platillo restado de la orden'}, status=200)
    except Exception as e:
        print(f"Error al restar platillo de la orden: {e}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    


    
def verCantidadBebidaEnOrden(request, idOrden,idItem):
    with connection.cursor() as cursor:
        cursor.execute("exec verCantidadBebidaEnOrden @idOrden = %s, @idItem = %s", (idOrden,idItem,))
        query = cursor.fetchall()
        # Convierte los resultados a una lista de diccionarios
        cantidad = [{'cantidad': query[0]}]
    return JsonResponse(cantidad, safe=False)

def verCantidadPlatilloEnOrden(request, idOrden,idPlatillo):
    with connection.cursor() as cursor:
        cursor.execute("exec verCantidadPlatilloEnOrden @idOrden = %s, @idPlatillo = %s", (idOrden,idPlatillo,))
        query = cursor.fetchall()
        # Convierte los resultados a una lista de diccionarios
        cantidad = [{'cantidad': query[0]}]
    return JsonResponse(cantidad, safe=False)