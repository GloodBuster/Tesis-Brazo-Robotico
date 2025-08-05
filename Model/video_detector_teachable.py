import cv2
import numpy as np
from keras.models import load_model

# Configuración
MODEL_PATH = "keras_model.h5"
camera = 0

# Tamaño fijo de la zona de detección
RECT_WIDTH = 300
RECT_HEIGHT = 300

# Diccionario de categorías
labels_clasificacion = {
    "3": "Baterias", "0": "Carton", "5": "Metal", 
    "1": "Papel", "4": "Plastico", "2": "Vidrio"
}

def dibujar_zona_deteccion(frame):
    """Dibuja un rectángulo fijo de 300x600 píxeles en la parte inferior central."""
    height, width = frame.shape[:2]
    
    # Calcular posición del rectángulo (centrado horizontalmente, en la parte inferior)
    # Centrar horizontalmente
    x1 = (width - RECT_WIDTH) // 2
    # Posicionar en la parte inferior
    y1 = height - RECT_HEIGHT - 50  # 50 píxeles de margen desde abajo
    
    # Dibujar el rectángulo
    cv2.rectangle(frame, (x1, y1), (x1 + RECT_WIDTH, y1 + RECT_HEIGHT), (0, 255, 0), 2)
    
    # Agregar texto indicativo
    cv2.putText(frame, "Zona de Deteccion", (x1, y1 - 10), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2, cv2.LINE_AA)
    
    # Mostrar dimensiones
    dimensiones_texto = f"Ancho: {RECT_WIDTH}px, Alto: {RECT_HEIGHT}px"
    cv2.putText(frame, dimensiones_texto, (10, height - 20), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2, cv2.LINE_AA)
    
    return x1, y1, RECT_WIDTH, RECT_HEIGHT

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

    # Configurar la resolución de la cámara
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    print("Presiona 'ESC' para salir")
    print("Zona de detección fija: 300x600 píxeles")

    # Colores para las barras de progreso
    colores = {
        "Baterias": (0, 0, 255),    # Rojo
        "Carton": (0, 165, 255),    # Naranja
        "Metal": (255, 255, 0),     # Cyan
        "Papel": (255, 255, 255),   # Blanco
        "Plastico": (0, 255, 0),    # Verde
        "Vidrio": (255, 0, 0)       # Azul
    }

    while True:
        # Capturar frame de la cámara
        ret, frame = cap.read()
        if not ret:
            print("Error al capturar frame de la cámara")
            break

        # Dibujar la zona de detección
        x1, y1, rect_width, rect_height = dibujar_zona_deteccion(frame)
        
        # Recortar la imagen solo a la zona de detección
        zona_deteccion = frame[y1:y1+rect_height, x1:x1+rect_width]
        
        # Verificar que la zona recortada no esté vacía
        if zona_deteccion.size == 0:
            print("Error: La zona de detección está fuera de los límites de la imagen")
            continue

        # Redimensionar la imagen recortada para la predicción
        image = cv2.resize(zona_deteccion, (224, 224), interpolation=cv2.INTER_AREA)
        
        # Preparar la imagen para el modelo
        image_array = np.asarray(image, dtype=np.float32).reshape(1, 224, 224, 3)
        image_array = (image_array / 127.5) - 1

        # Realizar la predicción
        prediction = model.predict(image_array, verbose=0)
        
        # Mostrar todas las categorías con sus porcentajes
        y_offset = 30
        for i, (label, nombre) in enumerate(labels_clasificacion.items()):
            porcentaje = prediction[0][int(label)]
            color = colores[nombre]
            
            # Mostrar nombre y porcentaje
            texto = f"{nombre}: {porcentaje:.2%}"
            cv2.putText(frame, texto, (10, y_offset), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2, cv2.LINE_AA)
            
            # Dibujar barra de progreso
            dibujar_barra_progreso(frame, 150, y_offset - 20, porcentaje, color)
            
            y_offset += 40

        # Mostrar instrucciones en pantalla
        cv2.putText(frame, "Presiona 'ESC' para salir", (10, frame.shape[0] - 50), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1, cv2.LINE_AA)

        # Mostrar la imagen
        cv2.imshow("Clasificación de Desechos - Cámara en Tiempo Real", frame)

        # Salir con ESC
        if cv2.waitKey(1) == 27:
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    procesar_video() 