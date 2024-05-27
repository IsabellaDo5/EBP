"""ProyectoBD URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from AppBD import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.inicio),
    path('login/', views.login),
    path('logout/', views.cerrar_sesion),
    #Seccion de empleados
    path('eliminar_empleado/<int:id_emp>/',views.eliminar_empleado),
    path('add_empleados/',views.agregar_empleado),
    path('empleado/<int:id_emp>/', views.edit_empleados),
    path('empleados/', views.empleados),
    # Seccion de inventario
    path('inventario/', views.inventario, name='inventario'),
    path('add_inventario/',views.agregar_inventario),
    path('item/<int:id_item>/',views.edit_inventario),
    path('eliminar_inventario/<int:id_item>/',views.eliminar_item),
    #Seccion de platillos
    path('platillos/', views.platillos, name='platillos'),
    path('agregar_platillo/', views.add_platillo, name='agregar-platillo'),
    path('eliminar_platillo/<int:id_platillo>/', views.eliminar_platillo, name='eliminar_platillo'),
    path('modificar_platillo/<int:id_platillo>/', views.editar_platillo),


    path('obtenerMedidaItem/<str:nombreMedida>/', views.obtenerMedidaItem),
    #Alquileres
    path('alquiler/', views.alquiler, name="alquileres"),
    path('add_alquiler2/', views.add_alquiler2),
    path('alquiler/<int:id_alquiler>/',views.edit_alquiler),
    path('eliminar_alquiler/<int:id_alquiler>/',views.eliminar_alquiler),
    #clientes
    path('add_cliente/', views.add_cliente),
    path('add_alquiler_cliente/', views.add_alquiler_cliente),
    path('cliente/<int:id_clientes>/',views.edit_cliente),
    path('eliminar_cliente/<int:id_clientes>/',views.eliminar_cliente),

    #Orden isa
    path('generar_orden/<int:id_mesa>', views.agregar_orden, name="gen_orden"),
    path('orden_detalle/<int:id_orden>', views.detalle_orden),
    path('ver_ordenes', views.ver_ordenes, name='ordenes'),

    

    #Facturas alquiler
    path('facturas_alquiler/', views.ver_facturas_alquiler),
    path('add_factura_alquiler/', views.add_factura_alquiler),

    

    #orden hotep
    path('mesas/', views.mesas, name="mesas"),
    path('mesa_orden/<int:id_mesa>/', views.mesa_orden),

    #Facturas orden
    path('editar_orden/<int:id_orden>/', views.editar_orden),

]