from our_lugo_solution import solucion
import time
from move_arm import mover_servo
from calibration import calibrar_brazo
from math import sqrt
from containers_movement import mover_carton


def mover_brazo_robot(x, y, z, orientacion, usar_calibracion=False):
    """
    Mueve el brazo robot a una posición específica usando la cinemática inversa.
    Primero mueve el brazo con la pinza elevada y luego a la posición final.

    Args:
        x (float): Coordenada X en cm
        y (float): Coordenada Y en cm
        z (int): Zona de trabajo (1-8)
        orientacion (float): Orientación deseada en grados
        usar_calibracion (bool): Si es True, realiza la calibración antes del movimiento
    """
    if usar_calibracion:
        print("\nRealizando calibración antes del movimiento...")
        calibrar_brazo()
        time.sleep(2)  # Esperar a que la calibración se complete

    # Obtener los pulsos para la posición final
    pulsos_finales, newQ5 = solucion(x, y, z, orientacion, cinta=True)

    if not pulsos_finales:
        print("Error: La posición solicitada no es alcanzable por el robot")
        return False

    # Mapeo de los pulsos a los servos correspondientes
    servos = [0, 2, 4, 6, 8]  # Servos del brazo
    distancia = sqrt(pow(x, 2) + pow(y, 2))

    # Calcular posición con pinza elevada (5 grados más arriba)
    pulsos_elevados = pulsos_finales.copy()
    pulsos_finales[0] = pulsos_finales[0] - 15
    pulsos_finales[2] = pulsos_finales[2] - 200

    orden_servos = [8, 2, 4, 6, 0]

    # Mover el servo adicional si es necesario
    newQ5 = 1008.00
    if newQ5 != 0:
        mover_servo(10, newQ5)

    # Esperar un momento para que el movimiento se complete
    time.sleep(1)

    # Segundo movimiento: posición final
    print("\nRealizando movimiento a posición final...")
    # Mover cada servo a su posición final
    for i, pulso in enumerate(orden_servos):
        time.sleep(0.5)
        mover_servo(pulso, pulsos_finales[pulso // 2])

    time.sleep(1)
    mover_servo(4, pulsos_elevados[2])
    time.sleep(0.5)

    newQ5 = 2208.00
    if newQ5 != 0:
        mover_servo(10, newQ5)

    time.sleep(1)
    mover_servo(4, pulsos_finales[2])
    time.sleep(1)

    mover_carton()

    return True


def mover_brazo_robot_manual(x, y, z, orientacion, usar_calibracion=False):
    """
    Mueve el brazo robot a una posición específica usando la cinemática inversa.
    Primero mueve el brazo con la pinza elevada y luego a la posición final.

    Args:
        x (float): Coordenada X en cm
        y (float): Coordenada Y en cm
        z (int): Zona de trabajo (1-8)
        orientacion (float): Orientación deseada en grados
        usar_calibracion (bool): Si es True, realiza la calibración antes del movimiento
    """
    if usar_calibracion:
        print("\nRealizando calibración antes del movimiento...")
        calibrar_brazo()
        time.sleep(2)  # Esperar a que la calibración se complete

    # Obtener los pulsos para la posición final
    pulsos_finales, newQ5 = solucion(x, y, z, orientacion, cinta=True)

    if not pulsos_finales:
        print("Error: La posición solicitada no es alcanzable por el robot")
        return False

    orden_servos = [0, 6, 4, 2, 8]

    # Esperar un momento para que el movimiento se complete
    time.sleep(1)

    # Segundo movimiento: posición final
    print("\nRealizando movimiento a posición final...")
    # Mover cada servo a su posición final
    mover_servo(10, 1008.00)
    time.sleep(0.5)
    for i, pulso in enumerate(orden_servos):
        time.sleep(0.5)
        mover_servo(pulso, pulsos_finales[pulso // 2])

    time.sleep(1)

    mover_servo(10, 2208.00)
    time.sleep(1)
    mover_servo(4, 1120.00)
    
    return True


def main():
    print("Control del Brazo Robot")
    print("----------------------")

    while True:
        try:
            # Preguntar si desea usar calibración
            usar_calibracion = (
                input(
                    "\n¿Desea realizar calibración antes del movimiento? (s/n): "
                ).lower()
                == "s"
            )

            # Obtener coordenadas del usuario
            x = float(input("Ingrese la coordenada X (en cm): "))
            y = float(input("Ingrese la coordenada Y (en cm): "))
            z = 1  # int(input("Ingrese la zona de trabajo (1-8): "))
            orientacion = (
                0  # float(input("Ingrese la orientación deseada (en grados): "))
            )

            # Validar entrada
            if not (1 <= z <= 8):
                print("Error: La zona de trabajo debe estar entre 1 y 8")
                continue

            if not (-90 <= orientacion <= 90):
                print("Error: La orientación debe estar entre -90 y 90 grados")
                continue

            # Intentar mover el brazo
            if mover_brazo_robot(x, y, z, orientacion, usar_calibracion):
                print("Movimiento completado exitosamente")

            # Preguntar si desea continuar
            continuar = input("\n¿Desea realizar otro movimiento? (s/n): ").lower()
            if continuar != "s":
                break

        except ValueError:
            print("Error: Por favor ingrese valores numéricos válidos")
        except KeyboardInterrupt:
            print("\nPrograma terminado por el usuario")
            break


if __name__ == "__main__":
    main()
