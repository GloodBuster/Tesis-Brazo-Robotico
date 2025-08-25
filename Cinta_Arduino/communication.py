import serial
import time
import threading
from typing import Optional, Callable


class ArduinoCommunication:
    def __init__(self, port: str = "COM7", baudrate: int = 9600, timeout: int = 1):
        """
        Inicializa la comunicación con Arduino

        Args:
            port: Puerto serial (ej: 'COM3' en Windows, '/dev/ttyUSB0' en Linux)
            baudrate: Velocidad de comunicación
            timeout: Tiempo de espera para operaciones de lectura
        """
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial_connection: Optional[serial.Serial] = None
        self.is_connected = False
        self.is_monitoring = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.temp_value = None
        self.last_update = None
        self.callback_function: Optional[Callable] = None

    def connect(self) -> bool:
        """
        Establece conexión con Arduino

        Returns:
            bool: True si la conexión fue exitosa, False en caso contrario
        """
        try:
            self.serial_connection = serial.Serial(
                port=self.port, baudrate=self.baudrate, timeout=self.timeout
            )
            time.sleep(2)  # Esperar a que Arduino se reinicie
            self.is_connected = True
            print(f"Conectado exitosamente a Arduino en {self.port}")
            return True
        except serial.SerialException as e:
            print(f"Error al conectar con Arduino: {e}")
            self.is_connected = False
            return False

    def disconnect(self):
        """Cierra la conexión con Arduino"""
        if self.serial_connection and self.serial_connection.is_open:
            self.stop_monitoring()
            self.serial_connection.close()
            self.is_connected = False
            print("Desconectado de Arduino")

    def send_command(self, command: str) -> bool:
        """
        Envía un comando a Arduino

        Args:
            command: Comando a enviar

        Returns:
            bool: True si el comando se envió exitosamente
        """
        if not self.is_connected:
            print("No hay conexión con Arduino")
            return False

        try:
            self.serial_connection.write(f"{command}\n".encode())
            return True
        except Exception as e:
            print(f"Error al enviar comando: {e}")
            return False

    def read_line(self) -> Optional[str]:
        """
        Lee una línea del puerto serial

        Returns:
            str: Línea leída o None si no hay datos
        """
        if not self.is_connected or not self.serial_connection:
            return None

        try:
            # Verificar si hay datos disponibles
            if self.serial_connection.in_waiting > 0:
                line = self.serial_connection.readline()
                if line:
                    # Decodificar y limpiar la línea
                    decoded_line = line.decode("utf-8", errors="ignore").strip()
                    if decoded_line:  # Solo retornar líneas no vacías
                        return decoded_line
        except serial.SerialException as e:
            print(f"Error de comunicación serial: {e}")
            self.is_connected = False
        except UnicodeDecodeError as e:
            print(f"Error al decodificar datos: {e}")
        except Exception as e:
            print(f"Error inesperado al leer datos: {e}")

        return None

    def get_temp_value(self) -> Optional[int]:
        """
        Obtiene el valor actual de la variable temp

        Returns:
            int: Valor de temp o None si no está disponible
        """
        return self.temp_value

    def get_last_update(self) -> Optional[float]:
        """
        Obtiene el timestamp de la última actualización

        Returns:
            float: Timestamp o None si no hay datos
        """
        return self.last_update

    def start_monitoring(self, callback: Optional[Callable] = None):
        """
        Inicia el monitoreo continuo de datos de Arduino

        Args:
            callback: Función opcional que se ejecuta cuando se reciben nuevos datos
        """
        if not self.is_connected:
            print("No hay conexión con Arduino")
            return

        self.callback_function = callback
        self.is_monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        print("Monitoreo iniciado")

    def stop_monitoring(self):
        """Detiene el monitoreo continuo"""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1)
        print("Monitoreo detenido")

    def _monitor_loop(self):
        """Bucle interno para monitorear datos de Arduino"""
        consecutive_errors = 0
        max_consecutive_errors = 5

        while self.is_monitoring and self.is_connected:
            try:
                line = self.read_line()
                if line:
                    self._process_line(line)
                    consecutive_errors = 0  # Resetear contador de errores
                else:
                    # Si no hay datos, esperar un poco más
                    time.sleep(0.05)

            except Exception as e:
                consecutive_errors += 1
                print(
                    f"Error en bucle de monitoreo ({consecutive_errors}/{max_consecutive_errors}): {e}"
                )

                if consecutive_errors >= max_consecutive_errors:
                    print("Demasiados errores consecutivos. Deteniendo monitoreo.")
                    self.is_monitoring = False
                    break

                time.sleep(0.5)  # Esperar más tiempo después de un error

    def _process_line(self, line: str):
        """
        Procesa una línea recibida de Arduino

        Args:
            line: Línea de texto recibida
        """
        try:
            # Intentar convertir directamente a número
            if line.strip().isdigit():
                new_temp_value = int(line.strip())

                # Solo actualizar si el valor cambió
                if self.temp_value != new_temp_value:
                    self.temp_value = new_temp_value
                    self.last_update = time.time()

                    print(f"Temp actualizado: {self.temp_value}")

                    # Ejecutar callback si está definido
                    if self.callback_function:
                        try:
                            self.callback_function(self.temp_value)
                        except Exception as e:
                            print(f"Error en callback: {e}")
                else:
                    # Valor repetido, solo actualizar timestamp
                    self.last_update = time.time()

        except ValueError as e:
            print(f"No se pudo convertir el valor de temp: {line} - Error: {e}")
        except Exception as e:
            print(f"Error al procesar línea '{line}': {e}")


# Funciones de utilidad
def list_available_ports():
    """
    Lista los puertos seriales disponibles

    Returns:
        list: Lista de puertos disponibles
    """
    import serial.tools.list_ports

    ports = serial.tools.list_ports.comports()
    available_ports = []

    for port in ports:
        available_ports.append(port.device)
        print(f"Puerto disponible: {port.device} - {port.description}")

    return available_ports


def example_usage(port: str = None):
    """Ejemplo de uso de la clase ArduinoCommunication"""

    # Listar puertos disponibles
    print("Puertos disponibles:")
    available_ports = list_available_ports()

    if not available_ports:
        print("No se encontraron puertos seriales")
        return

    # Usar el puerto especificado o el primero disponible
    if port is None:
        port = available_ports[0]
        print(f"Usando el primer puerto disponible: {port}")
    else:
        if port not in available_ports:
            print(
                f"El puerto {port} no está disponible. Puertos disponibles: {available_ports}"
            )
            return
        print(f"Usando puerto especificado: {port}")

    # Crear instancia de comunicación
    arduino = ArduinoCommunication(port=port)

    # Función callback para procesar nuevos valores de temp
    def on_temp_update(temp_value):
        print(f"¡Nuevo valor de temp recibido: {temp_value}!")
        if temp_value == 1:  # HIGH - luz bloqueada
            print("Estado: Luz bloqueada (LED rojo encendido)")
        else:  # LOW - luz presente
            print("Estado: Luz presente (LED verde encendido)")

    try:
        # Conectar con Arduino
        if arduino.connect():
            # Iniciar monitoreo con callback
            arduino.start_monitoring(callback=on_temp_update)

            # Mantener el programa ejecutándose
            print("Presiona Ctrl+C para detener...")
            while True:
                time.sleep(1)

                # También puedes obtener el valor actual en cualquier momento
                current_temp = arduino.get_temp_value()
                if current_temp is not None:
                    print(f"Valor actual de temp: {current_temp}")
    except KeyboardInterrupt:
        print("\nDeteniendo programa...")
    finally:
        arduino.disconnect()


def get_temp_value(arduino: ArduinoCommunication = None):
    if not arduino.is_connected:
        print("Arduino no está conectado")
        return None
    
    return arduino.get_temp_value()


if __name__ == "__main__":
    # Puedes especificar el puerto aquí o dejarlo como None para usar el primero disponible
    example_usage(port="COM7")  # Cambia esto al puerto que quieras usar
