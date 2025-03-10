# Principio de Sustitución de Liskov

from django.db import OperationalError, connection
from django.http import JsonResponse

#Ambos casos retornan el mismo tipo de dato (JsonResponse), 
# asegurando que el código que llame a esta función no se rompa al sustituirla por otra versión
def platillos_mas_vendidos(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT TOP 5 SUM(o.cantidad) as CantidadVendida ,p.nombre from platillos p INNER JOIN orden_detalle o ON p.id_platillo = o.id_platillo GROUP BY p.nombre ORDER BY CantidadVendida DESC")
            columns = [col[0] for col in cursor.description]
            rows = [dict(zip(columns, row)) for row in cursor.fetchall()]

    except OperationalError as e:
        return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse(rows, safe=False)

