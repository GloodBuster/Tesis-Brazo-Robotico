from Cinta_Arduino.communication import ArduinoCommunication
from Robot_Movement.grab import grab_object
from Robot_Movement.containers_movement import colocar_vidrio
from Robot_Movement.calibration import calibrar_brazo
import time

clasifying = False
arduino = ArduinoCommunication(port="COM7")

# Conectar con Arduino
if not arduino.connect():
    print("No se pudo conectar con Arduino. Verifica el puerto COM7")
    exit(1)

print("Conectado exitosamente con Arduino")

# Función callback para procesar nuevos valores
def on_temp_update(temp_value):
    return temp_value

# Iniciar monitoreo
arduino.start_monitoring(callback=on_temp_update)

try:
    while True:
        time.sleep(0.3)
        if clasifying:
            continue

        # Obtener valor actual
        temp = arduino.get_temp_value()
        
        if not temp:
            continue
        
        clasifying = True
        grab_object()
        calibrar_brazo()
        colocar_vidrio()
        calibrar_brazo()
        time.sleep(1)
        clasifying = False
        
        
        

except KeyboardInterrupt:
    print("\nDeteniendo programa...")
finally:
    arduino.disconnect()