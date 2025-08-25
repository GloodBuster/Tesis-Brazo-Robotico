import json
import os
from datetime import datetime

def guardar_resultados(x, y, z, orientacion, q1, q2, q3, q4, q5, pulses, newQ5):
    """
    Guarda los resultados de la función solucion en un archivo JSON.
    Si el archivo existe, agrega los nuevos resultados a la lista existente.
    """
    archivo_json = 'resultados_robot.json'
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    nuevo_resultado = {
        'timestamp': timestamp,
        'parametros_entrada': {
            'x': x,
            'y': y,
            'z': z,
            'orientacion': orientacion
        },
        'angulos': {
            'q1': q1,
            'q2': q2,
            'q3': q3,
            'q4': q4,
            'q5': q5
        },
        'pulsos': {
            'pulses': pulses,
            'newQ5': newQ5
        }
    }
    
    # Cargar datos existentes o crear nueva lista
    if os.path.exists(archivo_json):
        with open(archivo_json, 'r') as f:
            try:
                resultados = json.load(f)
            except json.JSONDecodeError:
                resultados = []
    else:
        resultados = []
    
    # Agregar nuevo resultado
    resultados.append(nuevo_resultado)
    
    # Guardar todos los resultados
    with open(archivo_json, 'w') as f:
        json.dump(resultados, f, indent=4)