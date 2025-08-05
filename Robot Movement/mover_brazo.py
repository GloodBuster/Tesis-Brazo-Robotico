import subprocess

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
    servo_rangos = {
        0: (496, 2496),
        2: (816, 1408),
        4: (448, 2096),
        6: (2096, 2464),
        8: (496, 2352),
        10: (1008, 2208),
    }
    servos_validos = list(servo_rangos.keys())

    while True:
        try:
            servo = int(input(f"Ingrese el número de servo a mover ({servos_validos}, o -1 para salir): "))
            if servo == -1:
                break
            if servo not in servos_validos:
                print(f"Error: El número de servo debe ser uno de los siguientes: {servos_validos}")
                continue

            min_pos, max_pos = servo_rangos[servo]
            posicion = int(input(f"Ingrese la posición deseada en microsegundos para el servo {servo} ({min_pos}-{max_pos}): "))

            if not (min_pos <= posicion <= max_pos):
                print(f"Error: La posición para el servo {servo} debe estar entre {min_pos} y {max_pos} us.")
                continue

            mover_servo(servo, posicion)

        except ValueError:
            print("Entrada inválida. Por favor, ingrese números enteros.")