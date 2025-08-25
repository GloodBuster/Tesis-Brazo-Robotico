import subprocess
import os

def mover_servo(numero_servo, posicion_us):
    """
    Ejecuta el archivo C++ compilado para mover un servo de la Pololu Maestro.

    Args:
        numero_servo (int): El número del servo a mover (0, 2, 4, 6, 8, 10).
        posicion_us (int): La posición deseada del servo en microsegundos.
    """
    try:
        # Obtener la ruta del directorio donde está este archivo
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Construir la ruta completa al ejecutable
        exe_path = os.path.join(current_dir, "control_brazo.exe")
        
        comando = [exe_path, str(numero_servo), str(posicion_us)]
        resultado = subprocess.run(comando, capture_output=True, text=True, check=True)
        print(f"Servo {numero_servo} movido a posición {posicion_us}")
        print(resultado.stdout)

    except subprocess.CalledProcessError as e:
        print(f"Error al ejecutar el programa C++: {e}")
        print(f"Salida del error: {e.stderr}")
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo {exe_path}")
        print("Asegúrate de que control_brazo.exe esté en el directorio Robot_Movement/")