import time
from Robot_Movement.move_arm import mover_servo
from Robot_Movement.our_lugo_solution import solucion


def grab_object():
    print("\nAgarrando un objeto...")

    pulsos_finales, _ = solucion(15, 10, 1, 0, True)

    orden_servos = [0, 4, 2, 6, 8]

    mover_servo(10, 1008.00)
    time.sleep(0.5)

    for i, pulso in enumerate(orden_servos):
        time.sleep(0.5)
        mover_servo(pulso, pulsos_finales[pulso // 2])

    time.sleep(1)
    mover_servo(10, 1900.00)

    return True


if __name__ == "__main__":
    grab_object()
