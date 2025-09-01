import cv2
import numpy as np
from keras.models import load_model

# Configuración
MODEL_PATH = "keras_model.h5"
camera = 0

# Tamaño de la imagen para el modelo
MODEL_IMAGE_SIZE = 224

# Posición de la zona de detección (centro por defecto)
zona_x = 320  # Centro horizontal (640/2)
zona_y = 240  # Centro vertical (480/2)

# Diccionario de categorías
labels_clasificacion = {
    "3": "Baterias", "0": "Carton", "5": "Metal", 
    "1": "Papel", "4": "Plastico", "2": "Vidrio"
}

def dibujar_zona_deteccion(frame):
    """Dibuja la zona de detección en el frame."""
    global zona_x, zona_y
    
    # Calcular las esquinas de la zona de detección
    x1 = zona_x - MODEL_IMAGE_SIZE // 2
    y1 = zona_y - MODEL_IMAGE_SIZE // 2
    x2 = zona_x + MODEL_IMAGE_SIZE // 2
    y2 = zona_y + MODEL_IMAGE_SIZE // 2
    
    # Dibujar rectángulo de la zona de detección
    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
    
    # Agregar texto "Zona de Detección"
    cv2.putText(frame, "Zona de Deteccion", (x1, y1 - 10), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2, cv2.LINE_AA)
    
    # Mostrar coordenadas de la zona
    cv2.putText(frame, f"Pos: ({zona_x}, {zona_y})", (x1, y2 + 20), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1, cv2.LINE_AA)
    
    return (x1, y1, x2, y2)

def mostrar_coordenadas_configuracion(frame):
    """Muestra las coordenadas para configurar en main.py"""
    # Calcular coordenadas relativas al centro
    center_x = 640 // 2
    center_y = 480 // 2
    offset_x = zona_x - center_x
    offset_y = zona_y - center_y
    
    # Mostrar instrucciones de configuración
    cv2.putText(frame, "CONFIGURACION PARA MAIN.PY:", (10, 30), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2, cv2.LINE_AA)
    
    cv2.putText(frame, f"ZONA_X = {zona_x}", (10, 60), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2, cv2.LINE_AA)
    
    cv2.putText(frame, f"ZONA_Y = {zona_y}", (10, 90), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2, cv2.LINE_AA)
    
    cv2.putText(frame, f"Offset X: {offset_x:+d}", (10, 120), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2, cv2.LINE_AA)
    
    cv2.putText(frame, f"Offset Y: {offset_y:+d}", (10, 150), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2, cv2.LINE_AA)

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
    image = cv2.resize(frame, (MODEL_IMAGE_SIZE, MODEL_IMAGE_SIZE), interpolation=cv2.INTER_AREA)
    
    # Preparar la imagen para el modelo
    image_array = np.asarray(image, dtype=np.float32).reshape(1, MODEL_IMAGE_SIZE, MODEL_IMAGE_SIZE, 3)
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
    global zona_x, zona_y
    
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

    # Configurar la resolución de la cámara a 640x480 (igual que en main.py)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    print("=== CONTROLES ===")
    print("Flechas: Mover zona de detección")
    print("ESPACIO: Tomar foto y clasificar")
    print("ESC: Salir")
    print(f"Tamaño de zona: {MODEL_IMAGE_SIZE}x{MODEL_IMAGE_SIZE} píxeles")
    print("Zona de detección ajustable en tiempo real")

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

        # Dibujar zona de detección en ambos modos
        zona_coords = dibujar_zona_deteccion(frame_mostrar)
        
        # Mostrar coordenadas de configuración
        mostrar_coordenadas_configuracion(frame_mostrar)

        # Mostrar instrucciones generales
        cv2.putText(frame_mostrar, "Presiona 'ESC' para salir", 
                   (10, frame_mostrar.shape[0] - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1, cv2.LINE_AA)

        # Mostrar la imagen
        cv2.imshow("Clasificación de Desechos - Zona de Detección Ajustable", frame_mostrar)

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
                
                # Extraer zona de detección con la posición actual
                x1, y1, x2, y2 = zona_coords
                zona_deteccion = frame_foto[y1:y2, x1:x2]
                resultados = procesar_imagen(model, zona_deteccion)
                
                print("Foto procesada. Presiona ESPACIO para volver al video.")
            else:
                # Volver al modo video
                modo_foto = False
                frame_foto = None
                resultados = None
                print("Volviendo al modo video...")
        elif key == 82:  # Flecha arriba
            zona_y = max(MODEL_IMAGE_SIZE // 2, zona_y - 10)
            print(f"Zona movida arriba. Nueva posición: ({zona_x}, {zona_y})")
        elif key == 84:  # Flecha abajo
            zona_y = min(480 - MODEL_IMAGE_SIZE // 2, zona_y + 10)
            print(f"Zona movida abajo. Nueva posición: ({zona_x}, {zona_y})")
        elif key == 81:  # Flecha izquierda
            zona_x = max(MODEL_IMAGE_SIZE // 2, zona_x - 10)
            print(f"Zona movida izquierda. Nueva posición: ({zona_x}, {zona_y})")
        elif key == 83:  # Flecha derecha
            zona_x = min(640 - MODEL_IMAGE_SIZE // 2, zona_x + 10)
            print(f"Zona movida derecha. Nueva posición: ({zona_x}, {zona_y})")

    cap.release()
    cv2.destroyAllWindows()
    
    # Mostrar configuración final
    print("\n=== CONFIGURACION FINAL PARA MAIN.PY ===")
    print(f"ZONA_X = {zona_x}")
    print(f"ZONA_Y = {zona_y}")
    
    # Calcular coordenadas relativas al centro
    center_x = 640 // 2
    center_y = 480 // 2
    offset_x = zona_x - center_x
    offset_y = zona_y - center_y
    print(f"Offset X: {offset_x:+d}")
    print(f"Offset Y: {offset_y:+d}")

if __name__ == "__main__":
    procesar_video()
