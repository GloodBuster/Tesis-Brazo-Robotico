import subprocess
from time import sleep

def mover_servo(numero_servo, posicion_us):
    """
    Ejecuta el archivo C++ compilado para mover un servo de la Pololu Maestro.

    Args:
        numero_servo (int): El número del servo a mover (0, 2, 4, 6, 8, 10).
        posicion_us (int): La posición deseada del servo en microsegundos.
    """
    try:
        # Construye el comando para ejecutar el archivo C++ con los parámetros
        comando = ["./control_brazo.exe", str(numero_servo), str(posicion_us)]

        # Ejecuta el comando y captura la salida
        resultado = subprocess.run(comando, capture_output=True, text=True, check=True)

        # Imprime la salida del programa C++
        print(resultado.stdout)

    except subprocess.CalledProcessError as e:
        # Si el programa C++ devuelve un error, imprime el error
        print(f"Error al ejecutar el programa C++: {e}")
        print(f"Salida del error: {e.stderr}")
    except FileNotFoundError:
        print("Error: No se encontró el archivo control_brazo.exe. Asegúrate de que esté en el mismo directorio.")

if __name__ == "__main__":
    try:
        while True:
            mover_servo(8, 550)
            sleep(0.5)
            mover_servo(8, 1300)
            sleep(0.5)

    except KeyboardInterrupt:
        print("\nProgram interrupted by user.")