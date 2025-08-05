import time
from angles import pulsos
from move_arm import mover_servo

def calibrar_brazo():
    """
    Realiza la calibración del brazo robótico moviendo cada servo a su posición cero.
    """
    print("\nIniciando calibración del brazo robótico...")
    
    # Posiciones cero de cada servo (ajustar según sea necesario)
    posiciones_cero = {
        0: 0,  # Base
        2: 90,  # Hombro
        4: 90,  # Codo
        6: 90,  # Muñeca
        8: 0,  # Rotación pinza
        10: 2208  # Pinza
    }
    
    orden_servos = [2, 4, 6, 8, 0]
    resultado_pulsos = pulsos(posiciones_cero[0], posiciones_cero[2], posiciones_cero[4], 
                              posiciones_cero[6], posiciones_cero[8])
    
    for i, pulso in enumerate(orden_servos):
        print(f"\nCalibrando servo {pulso}...")
        time.sleep(0.5)
        mover_servo(pulso, resultado_pulsos[pulso//2])
    
    time.sleep(0.5)
    mover_servo(10, 2208.00)
    
    print("\nCalibración completada. El brazo está en su posición cero.")
    return posiciones_cero

if __name__ == "__main__":
    calibrar_brazo()