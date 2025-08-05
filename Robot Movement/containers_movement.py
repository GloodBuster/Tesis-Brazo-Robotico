from our_lugo_solution import solucion
import time
from move_arm import mover_servo
from calibration import calibrar_brazo
from math import sqrt


def mover_carton():
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
    # Obtener los pulsos para la posición final
    x = 15
    y = 0
    z = 1
    orientacion = 0
    pulsos_finales, newQ5 = solucion(x, y, z, orientacion)

    if not pulsos_finales:
        print("Error: La posición solicitada no es alcanzable por el robot")
        return False

    # Mapeo de los pulsos a los servos correspondientes
    servos = [0, 2, 4, 6, 8]  # Servos del brazo
    distancia = sqrt(pow(x, 2) + pow(y, 2))

    # Calcular posición con pinza elevada (5 grados más arriba)
    pulsos_finales[0] = pulsos_finales[0] - 15

    orden_servos = [0, 8, 6, 4, 2]


    print("\nRealizando movimiento a posición final...")

    for i, pulso in enumerate(orden_servos):
        time.sleep(0.5)
        mover_servo(pulso, pulsos_finales[pulso // 2])

    time.sleep(1)
    mover_servo(10, 1008.00)

    # Esperar un momento para que el movimiento se complete

    return True


def main():
    mover_carton()


if __name__ == "__main__":
    main()
