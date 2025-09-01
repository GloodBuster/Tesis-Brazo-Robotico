from .our_lugo_solution import solucion
import time
from .move_arm import mover_servo


def mover(x, y, z=1, orientacion=0, custom_offset=None, cinta=False):
    pulsos_finales, _ = solucion(x, y, z, orientacion, cinta, custom_offset)

    if not pulsos_finales:
        print("Error: La posición solicitada no es alcanzable por el robot")
        return False

    pulsos_finales[0] = pulsos_finales[0] - 15
    orden_servos = [0, 8, 6, 4, 2]

    print("\nRealizando movimiento a posición final...")

    for _, pulso in enumerate(orden_servos):
        time.sleep(0.5)
        mover_servo(pulso, pulsos_finales[pulso // 2])

    time.sleep(1)
    mover_servo(10, 1008.00)

    return True


def colocar_papel_y_carton():
    return mover(0, 19, custom_offset=6, cinta=True)


def colocar_plastico():
    return mover(0, 1, custom_offset=13, cinta=True)


def colocar_vidrio():
    return mover(3, -1, custom_offset=13, cinta=True)


def colocar_metal_y_bateria():
    return mover(18, -6, custom_offset=6, cinta=True)


def main():
    print("Que desecho quieres colocar?")
    print("1. Papel y carton")
    print("2. Plastico")
    print("3. Vidrio")
    print("4. Metal y bateria")
    print("5. Salir")
    opcion = int(input("Selecciona una opcion: "))

    if opcion == 1:
        colocar_papel_y_carton()
    elif opcion == 2:
        colocar_plastico()
    elif opcion == 3:
        colocar_vidrio()
    elif opcion == 4:
        colocar_metal_y_bateria()
    elif opcion == 5:
        print("Saliendo...")
    else:
        print("Opcion no valida")


if __name__ == "__main__":
    main()
