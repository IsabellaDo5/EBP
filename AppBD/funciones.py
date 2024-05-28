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

#items
def AñadirItemAOrden(request,idOrden,idItem):
    with connection.cursor() as cursor:
        query="exec AñadirItemAOrden @id_orden = %s, @id_item =%s"
        valores=(idOrden,idItem,)

        cursor.execute(query,valores)
    connection.commit()

def RestarItemAOrden(request,idOrden,idItem):
    with connection.cursor() as cursor:
        query="exec RestarItemAOrden @id_orden = %s, @id_item =%s"
        valores=(idOrden,idItem,)

        cursor.execute(query,valores)
    connection.commit()

#platillos

def AñadirPlatilloAOrden(request,idOrden,idPlatillo):
    with connection.cursor() as cursor:
        query="exec AñadirPlatilloAOrden @id_orden = %s, @id_platillo =%s"
        valores=(idOrden,idPlatillo,)

        cursor.execute(query,valores)
    connection.commit()

def RestarPlatilloAOrden(request,idOrden,idPlatillo):
    with connection.cursor() as cursor:
        query="exec RestarPlatilloAOrden @id_orden = %s, @id_platillo =%s"
        valores=(idOrden,idPlatillo,)

        cursor.execute(query,valores)
    connection.commit()