import time
from Robot_Movement.calibration import calibrar_brazo
from Robot_Movement.grab import grab_object
from Robot_Movement.containers_movement import (
    colocar_papel_y_carton,
    colocar_plastico,
    colocar_vidrio,
    colocar_metal_y_bateria,
)


if __name__ == "__main__":
    calibrar_brazo()
    time.sleep(2)
    colocar_vidrio()
    time.sleep(2)
    calibrar_brazo()