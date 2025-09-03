import cv2
import numpy as np
from keras.models import load_model
from Cinta_Arduino.communication import ArduinoCommunication
from Robot_Movement.grab import grab_object
from Robot_Movement.calibration import calibrar_brazo
from Robot_Movement.containers_movement import (
    colocar_papel_y_carton,
    colocar_plastico,
    colocar_vidrio,
    colocar_metal_y_bateria,
)
import time
import threading

# Configuración del modelo
MODEL_PATH = "Model/keras_model.h5"
MODEL_IMAGE_SIZE = 224

# Tamaño de la pantalla de visualización
DISPLAY_WIDTH = 700
DISPLAY_HEIGHT = 700

# Diccionario de categorías
labels_clasificacion = {
    "3": "Baterias",
    "0": "Carton",
    "5": "Metal",
    "1": "Papel",
    "4": "Plastico",
    "2": "Vidrio",
}

# Mapeo de categorías a funciones de movimiento
funciones_movimiento = {
    "Baterias": colocar_metal_y_bateria,
    "Carton": colocar_papel_y_carton,
    "Metal": colocar_metal_y_bateria,
    "Papel": colocar_papel_y_carton,
    "Plastico": colocar_plastico,
    "Vidrio": colocar_vidrio,
}

# Variables globales
clasifying = False
arduino = ArduinoCommunication(port="COM7")
model = None
cap = None

# Estado de las categorías para la interfaz visual
categoria_activa = None
colores_categorias = {
    "Papel": (255, 0, 0),  # Azul
    "Carton": (255, 0, 0),  # Azul
    "Plastico": (0, 255, 255),  # Amarillo
    "Vidrio": (0, 255, 0),  # Verde
    "Metal": (0, 0, 255),  # Rojo
    "Baterias": (0, 0, 255),  # Rojo
}
color_inactivo = (128, 128, 128)  # Gris

# Lock para sincronización entre hilos
lock_clasificacion = threading.Lock()

# Contador de errores de cámara
errores_camara = 0
MAX_ERRORES_CAMARA = 10


def cargar_modelo():
    """Carga el modelo de clasificación desde archivo local."""
    try:
        print("Cargando modelo...")
        model = load_model(MODEL_PATH, compile=False)
        print("Modelo cargado exitosamente")
        return model
    except Exception as e:
        print(f"Error al cargar el modelo: {e}")
        return None


def procesar_imagen(frame):
    """Procesa una imagen con el modelo y retorna las predicciones."""
    global model
    if model is None:
        return None

    # Redimensionar la imagen para la predicción (700x700 -> 224x224)
    image = cv2.resize(
        frame, (MODEL_IMAGE_SIZE, MODEL_IMAGE_SIZE), interpolation=cv2.INTER_AREA
    )

    # Preparar la imagen para el modelo
    image_array = np.asarray(image, dtype=np.float32).reshape(
        1, MODEL_IMAGE_SIZE, MODEL_IMAGE_SIZE, 3
    )
    image_array = (image_array / 127.5) - 1

    # Realizar la predicción
    prediction = model.predict(image_array, verbose=0)
    return prediction[0]


def obtener_clasificacion(prediction):
    """Obtiene la clasificación principal basada en la predicción."""
    if prediction is None:
        return None

    # Encontrar la categoría con mayor probabilidad
    max_index = np.argmax(prediction)
    max_prob = prediction[max_index]

    # Solo clasificar si la probabilidad es mayor al 70%
    if max_prob > 0.6:
        categoria = labels_clasificacion[str(max_index)]
        return categoria, max_prob
    return None, 0


def mostrar_estado(frame, estado, clasificacion=None, probabilidad=0):
    """Muestra el estado actual en el frame."""
    # Mostrar estado del sistema
    cv2.putText(
        frame,
        f"Estado: {estado}",
        (10, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2,
        cv2.LINE_AA,
    )

    # Mostrar clasificación si existe
    if clasificacion:
        cv2.putText(
            frame,
            f"Clasificado como: {clasificacion}",
            (10, 60),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2,
            cv2.LINE_AA,
        )
        cv2.putText(
            frame,
            f"Probabilidad: {probabilidad:.2%}",
            (10, 90),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2,
            cv2.LINE_AA,
        )


def dibujar_categorias(frame):
    """Dibuja las 6 categorías con sus cuadrados de colores."""
    global categoria_activa

    # Configuración de la interfaz - ahora 6 categorías separadas
    categorias = ["Papel", "Carton", "Plastico", "Vidrio", "Metal", "Baterias"]
    pos_x = 10
    pos_y = 120
    espaciado_y = 35
    tamano_cuadrado = 20
    espaciado_texto = 30

    # Obtener categoría activa de forma thread-safe
    with lock_clasificacion:
        categoria_actual = categoria_activa

    for i, categoria in enumerate(categorias):
        y = pos_y + i * espaciado_y

        # Determinar el color del cuadrado
        if categoria_actual == categoria:
            color = colores_categorias[categoria]
        else:
            color = color_inactivo

        # Dibujar cuadrado
        cv2.rectangle(
            frame, (pos_x, y), (pos_x + tamano_cuadrado, y + tamano_cuadrado), color, -1
        )  # -1 para rellenar

        # Dibujar borde del cuadrado
        cv2.rectangle(
            frame,
            (pos_x, y),
            (pos_x + tamano_cuadrado, y + tamano_cuadrado),
            (255, 255, 255),
            2,
        )

        # Dibujar texto de la categoría
        cv2.putText(
            frame,
            categoria,
            (pos_x + espaciado_texto, y + tamano_cuadrado - 5),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2,
            cv2.LINE_AA,
        )


def inicializar_camara():
    """Inicializa la cámara."""
    global cap

    # Intentar diferentes índices de cámara
    for camera_index in [0, 1, 2]:
        print(f"Intentando conectar a cámara {camera_index}...")
        cap = cv2.VideoCapture(camera_index)

        if cap.isOpened():
            # Intentar configurar resolución
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, DISPLAY_WIDTH)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, DISPLAY_HEIGHT)

            # Dar tiempo a la cámara para inicializarse completamente
            time.sleep(1)

            # Verificar que realmente se puede leer un frame
            ret, test_frame = cap.read()
            if ret and test_frame is not None:
                print(f"Cámara {camera_index} inicializada exitosamente")
                print(
                    f"Resolución configurada: {DISPLAY_WIDTH}x{DISPLAY_HEIGHT} píxeles"
                )
                print(
                    f"Imagen para modelo: {MODEL_IMAGE_SIZE}x{MODEL_IMAGE_SIZE} píxeles"
                )
                return True
            else:
                print(f"Cámara {camera_index} no puede leer frames")
                cap.release()
        else:
            print(f"No se pudo abrir cámara {camera_index}")

    print("Error: No se pudo inicializar ninguna cámara.")
    return False


def reinicializar_camara():
    """Reinicializa la cámara si hay problemas."""
    global cap, errores_camara
    print("Reinicializando cámara...")

    if cap is not None:
        cap.release()

    time.sleep(2)  # Esperar antes de reintentar
    errores_camara = 0

    return inicializar_camara()


def procesar_clasificacion():
    """Procesa la clasificación y mueve el robot."""
    global clasifying, categoria_activa

    with lock_clasificacion:
        if clasifying:
            return
        clasifying = True
    print("Iniciando proceso de clasificación...")

    try:
        # PRIMERA FASE: Clasificación del objeto
        print("Fase 1: Clasificando objeto...")
        time.sleep(1)

        # Obtener frame completo de la cámara
        ret, frame = cap.read()
        if not ret:
            print("Error al capturar frame para clasificación")
            return

        print(f"Imagen capturada: {frame.shape[1]}x{frame.shape[0]} píxeles")
        print(
            f"Redimensionando a: {MODEL_IMAGE_SIZE}x{MODEL_IMAGE_SIZE} píxeles para el modelo"
        )

        # Procesar imagen completa con el modelo (se redimensiona internamente)
        prediction = procesar_imagen(frame)

        if prediction is None:
            print("Error al procesar la imagen")
            return

        clasificacion, probabilidad = obtener_clasificacion(prediction)

        if not clasificacion:
            print("No se pudo clasificar el objeto con suficiente confianza")
            return

        print(
            f"Objeto clasificado como: {clasificacion} (Probabilidad: {probabilidad:.2%})"
        )

        # Actualizar categoría activa para la interfaz visual
        with lock_clasificacion:
            categoria_activa = clasificacion

        # SEGUNDA FASE: Movimiento del robot
        print("Fase 2: Iniciando movimiento del robot...")

        # Verificar que existe función de movimiento para esta clasificación
        if clasificacion not in funciones_movimiento:
            print(f"No hay función de movimiento definida para {clasificacion}")
            return

        # Capturar objeto
        print("Capturando objeto...")
        grab_object()
        time.sleep(0.5)

        # Calibrar brazo
        print("Calibrando brazo...")
        calibrar_brazo()
        time.sleep(0.5)

        # Mover objeto a su ubicación correspondiente
        print(f"Movimiento objeto a ubicación de {clasificacion}...")
        funciones_movimiento[clasificacion]()
        print("Objeto colocado exitosamente")
        time.sleep(0.5)

        # Calibrar brazo nuevamente
        print("Calibrando brazo final...")
        calibrar_brazo()
        time.sleep(0.5)

    except Exception as e:
        print(f"Error durante el proceso de clasificación: {e}")
    finally:
        with lock_clasificacion:
            clasifying = False
            categoria_activa = None  # Resetear categoría activa inmediatamente
        print("Proceso de clasificación completado")


def main():
    global model, arduino, cap

    print("Iniciando sistema de clasificación automática...")
    print(
        f"Configuración: Pantalla {DISPLAY_WIDTH}x{DISPLAY_HEIGHT}, Modelo {MODEL_IMAGE_SIZE}x{MODEL_IMAGE_SIZE}"
    )

    # Cargar modelo
    model = cargar_modelo()
    if model is None:
        print("No se pudo cargar el modelo. Saliendo...")
        return

    # Inicializar cámara
    if not inicializar_camara():
        print("No se pudo inicializar la cámara.")
        print("¿Deseas continuar con una imagen de prueba? (s/n): ", end="")
        try:
            respuesta = input().lower()
            if respuesta == "s":
                # Crear una imagen de prueba
                frame_prueba = np.zeros(
                    (DISPLAY_HEIGHT, DISPLAY_WIDTH, 3), dtype=np.uint8
                )
                cv2.putText(
                    frame_prueba,
                    "MODO PRUEBA - Sin Camara",
                    (DISPLAY_WIDTH // 2 - 150, DISPLAY_HEIGHT // 2),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (255, 255, 255),
                    2,
                )
                print("Modo prueba activado")
            else:
                print("Saliendo...")
                return
        except:
            print("Saliendo...")
            return

    # Conectar con Arduino
    if not arduino.connect():
        print("No se pudo conectar con Arduino. Verifica el puerto COM7")
        return

    print("Conectado exitosamente con Arduino")

    # Función callback para procesar nuevos valores
    def on_temp_update(temp_value):
        return temp_value

    # Iniciar monitoreo
    arduino.start_monitoring(callback=on_temp_update)

    calibrar_brazo()
    time.sleep(1)

    print("Sistema listo. Presiona 'ESC' para salir")
    print("El sistema clasificará automáticamente cuando detecte un objeto")

    try:
        while True:
            # Capturar frame de la cámara o usar imagen de prueba
            if "frame_prueba" in locals():
                frame = frame_prueba.copy()
            else:
                try:
                    ret, frame = cap.read()
                    if not ret or frame is None:
                        errores_camara += 1
                        print(
                            f"Error al capturar frame de la cámara ({errores_camara}/{MAX_ERRORES_CAMARA}), reintentando..."
                        )

                        if errores_camara >= MAX_ERRORES_CAMARA:
                            print("Demasiados errores de cámara, reinicializando...")
                            if not reinicializar_camara():
                                print(
                                    "No se pudo reinicializar la cámara, usando modo prueba"
                                )
                                frame_prueba = np.zeros(
                                    (DISPLAY_HEIGHT, DISPLAY_WIDTH, 3), dtype=np.uint8
                                )
                                cv2.putText(
                                    frame_prueba,
                                    "MODO PRUEBA - Error de Camara",
                                    (DISPLAY_WIDTH // 2 - 150, DISPLAY_HEIGHT // 2),
                                    cv2.FONT_HERSHEY_SIMPLEX,
                                    1,
                                    (255, 255, 255),
                                    2,
                                )
                                frame = frame_prueba.copy()
                            else:
                                errores_camara = 0
                        else:
                            time.sleep(0.5)
                            continue
                    else:
                        errores_camara = (
                            0  # Resetear contador si la captura fue exitosa
                        )
                except Exception as e:
                    errores_camara += 1
                    print(
                        f"Error en captura de frame: {e} ({errores_camara}/{MAX_ERRORES_CAMARA})"
                    )
                    if errores_camara >= MAX_ERRORES_CAMARA:
                        print("Demasiados errores de cámara, reinicializando...")
                        if not reinicializar_camara():
                            print(
                                "No se pudo reinicializar la cámara, usando modo prueba"
                            )
                            frame_prueba = np.zeros(
                                (DISPLAY_HEIGHT, DISPLAY_WIDTH, 3), dtype=np.uint8
                            )
                            cv2.putText(
                                frame_prueba,
                                "MODO PRUEBA - Error de Camara",
                                (DISPLAY_WIDTH // 2 - 150, DISPLAY_HEIGHT // 2),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                1,
                                (255, 255, 255),
                                2,
                            )
                            frame = frame_prueba.copy()
                        else:
                            errores_camara = 0
                    else:
                        time.sleep(0.5)
                        continue

            # Crear copia del frame para mostrar
            frame_mostrar = frame.copy()

            # Mostrar estado actual
            with lock_clasificacion:
                estado_actual = clasifying
            estado = "Clasificando..." if estado_actual else "Esperando objeto"
            mostrar_estado(frame_mostrar, estado)

            # Dibujar categorías con sus cuadrados de colores
            dibujar_categorias(frame_mostrar)

            # Mostrar instrucciones
            cv2.putText(
                frame_mostrar,
                "Presiona 'ESC' para salir",
                (10, frame_mostrar.shape[0] - 20),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
                1,
                cv2.LINE_AA,
            )

            # Mostrar la imagen
            cv2.imshow("Sistema de Clasificacion Automatica", frame_mostrar)

            # Verificar si hay un objeto para clasificar
            temp = arduino.get_temp_value()
            with lock_clasificacion:
                clasificando_actual = clasifying
            if temp and not clasificando_actual:
                print("Objeto detectado, iniciando clasificación...")
                # Procesar en un hilo separado para no congelar la interfaz
                thread_clasificacion = threading.Thread(target=procesar_clasificacion)
                thread_clasificacion.daemon = True
                thread_clasificacion.start()

            # Capturar teclas
            key = cv2.waitKey(1) & 0xFF
            if key == 27:  # ESC
                break

            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\nDeteniendo programa...")
    finally:
        if cap:
            cap.release()
        cv2.destroyAllWindows()
        arduino.disconnect()
        print("Programa terminado")


if __name__ == "__main__":
    main()
