#  Otras funciones pueden usarla sin saber cómo funciona internamente.
#Hace un solo trabajo
# No depende de ninguna otra clase o estructura externa.

def calcular_tiempo(inicio, fin):
    # Convierte las horas y minutos a enteros
    inicio_horas, inicio_minutos = map(int, inicio.split(":"))
    fin_horas, fin_minutos = map(int, fin.split(":"))

    # Calcula el total de minutos desde la medianoche
    inicio_total_minutos = inicio_horas * 60 + inicio_minutos
    fin_total_minutos = fin_horas * 60 + fin_minutos

    # Calcula la diferencia en minutos
    diferencia_minutos = fin_total_minutos - inicio_total_minutos

    # Si la diferencia es negativa, significa que la hora final es al día siguiente
    if diferencia_minutos < 0:
        diferencia_minutos += 24 * 60

    # Convierte la diferencia de minutos a horas y minutos
    horas = diferencia_minutos // 60
    minutos = diferencia_minutos % 60

    print("HORAS:"+str(horas))
    # Retorna la diferencia como una cadena en formato HH:MM
    return f"{horas:02}:{minutos:02}"
