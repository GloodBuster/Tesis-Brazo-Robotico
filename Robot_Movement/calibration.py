import time
from .move_arm import mover_servo
from .our_lugo_solution import solucion


def calibrar_brazo():
    """
    Realiza la calibración del brazo robótico moviendo cada servo a su posición cero.
    """
    print("\nIniciando calibración del brazo robótico...")

    # Posiciones cero de cada servo (ajustar según sea necesario)
    pulsos_finales, _ = solucion(6, 6, 1, 0, True, 14)

    orden_servos = [2, 4, 6, 8, 0]

    for i, pulso in enumerate(orden_servos):
        print(f"\nCalibrando servo {pulso}...")
        time.sleep(0.5)
        mover_servo(pulso, pulsos_finales[pulso // 2])

    print("\nCalibración completada. El brazo está en su posición cero.")
    return True


if __name__ == "__main__":
    calibrar_brazo()
