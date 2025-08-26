import cv2
import numpy as np
from keras.models import load_model

# Configuración
MODEL_PATH = "keras_model.h5"
camera = 0

# Tamaño de la imagen para el modelo
MODEL_IMAGE_SIZE = 224

# Diccionario de categorías
labels_clasificacion = {
    "3": "Baterias", "0": "Carton", "5": "Metal", 
    "1": "Papel", "4": "Plastico", "2": "Vidrio"
}

def dibujar_barra_progreso(frame, x, y, porcentaje, color):
    """Dibuja una barra de progreso en el frame."""
    ancho_barra = 200
    alto_barra = 20
    # Dibujar fondo de la barra
    cv2.rectangle(frame, (x, y), (x + ancho_barra, y + alto_barra), (50, 50, 50), -1)
    # Dibujar barra de progreso
    ancho_progreso = int(ancho_barra * porcentaje)
    cv2.rectangle(frame, (x, y), (x + ancho_progreso, y + alto_barra), color, -1)
    # Dibujar borde
    cv2.rectangle(frame, (x, y), (x + ancho_barra, y + alto_barra), (255, 255, 255), 1)

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

def procesar_imagen(model, frame):
    """Procesa una imagen con el modelo y retorna las predicciones."""
    # Redimensionar la imagen para la predicción
    image = cv2.resize(frame, (224, 224), interpolation=cv2.INTER_AREA)
    
    # Preparar la imagen para el modelo
    image_array = np.asarray(image, dtype=np.float32).reshape(1, 224, 224, 3)
    image_array = (image_array / 127.5) - 1

    # Realizar la predicción
    prediction = model.predict(image_array, verbose=0)
    return prediction[0]

def mostrar_resultados(frame, prediction):
    """Muestra los resultados de la clasificación en el frame."""
    # Colores para las barras de progreso
    colores = {
        "Baterias": (0, 0, 255),    # Rojo
        "Carton": (0, 165, 255),    # Naranja
        "Metal": (255, 255, 0),     # Cyan
        "Papel": (255, 255, 255),   # Blanco
        "Plastico": (0, 255, 0),    # Verde
        "Vidrio": (255, 0, 0)       # Azul
    }
    
    # Mostrar todas las categorías con sus porcentajes
    y_offset = 30
    for i, (label, nombre) in enumerate(labels_clasificacion.items()):
        porcentaje = prediction[int(label)]
        color = colores[nombre]
        
        # Mostrar nombre y porcentaje
        texto = f"{nombre}: {porcentaje:.2%}"
        cv2.putText(frame, texto, (10, y_offset), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2, cv2.LINE_AA)
        
        # Dibujar barra de progreso
        dibujar_barra_progreso(frame, 150, y_offset - 20, porcentaje, color)
        
        y_offset += 40

def procesar_video():
    """Procesa el video de la cámara en tiempo real y clasifica los desechos."""
    # Cargar modelo
    model = cargar_modelo()
    if model is None:
        return

    # Inicializar la cámara
    cap = cv2.VideoCapture(camera)
    if not cap.isOpened():
        print("Error: No se pudo abrir la cámara.")
        return
    print('Camera opened')

    # Configurar la resolución de la cámara a 400x400
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, MODEL_IMAGE_SIZE)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, MODEL_IMAGE_SIZE)

    print("Presiona 'ESPACIO' para tomar una foto y clasificar")
    print("Presiona 'ESC' para salir")
    print(f"Tamaño de imagen: {MODEL_IMAGE_SIZE}x{MODEL_IMAGE_SIZE} píxeles")

    # Variables de control
    modo_foto = False
    frame_foto = None
    resultados = None

    while True:
        # Capturar frame de la cámara
        ret, frame = cap.read()
        if not ret:
            print("Error al capturar frame de la cámara")
            break

        # Crear una copia del frame para mostrar
        frame_mostrar = frame.copy()

        if modo_foto:
            # Modo foto: mostrar la foto tomada con los resultados
            if frame_foto is not None and resultados is not None:
                # Mostrar la foto tomada
                cv2.putText(frame_mostrar, "FOTO TOMADA - Resultados de Clasificacion", 
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2, cv2.LINE_AA)
                
                # Mostrar los resultados
                mostrar_resultados(frame_mostrar, resultados)
                
                # Instrucciones para volver al video
                cv2.putText(frame_mostrar, "Presiona 'ESPACIO' para volver al video", 
                           (10, frame_mostrar.shape[0] - 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1, cv2.LINE_AA)
        else:
            # Modo video normal
            cv2.putText(frame_mostrar, "Modo Video - Presiona 'ESPACIO' para tomar foto", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2, cv2.LINE_AA)

        # Mostrar instrucciones generales
        cv2.putText(frame_mostrar, "Presiona 'ESC' para salir", 
                   (10, frame_mostrar.shape[0] - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1, cv2.LINE_AA)

        # Mostrar la imagen
        cv2.imshow("Clasificación de Desechos - Cámara en Tiempo Real", frame_mostrar)

        # Capturar teclas
        key = cv2.waitKey(1) & 0xFF
        
        if key == 27:  # ESC
            break
        elif key == 32:  # ESPACIO
            if not modo_foto:
                # Tomar foto y procesar
                modo_foto = True
                frame_foto = frame.copy()
                print("Tomando foto y procesando...")
                resultados = procesar_imagen(model, frame_foto)
                print("Foto procesada. Presiona ESPACIO para volver al video.")
            else:
                # Volver al modo video
                modo_foto = False
                frame_foto = None
                resultados = None
                print("Volviendo al modo video...")

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    procesar_video() 