import cv2
import numpy as np
from rembg import remove, new_session
from PIL import Image
import io
import threading
from queue import Queue
import time

def redimensionar_imagen(imagen, ancho_maximo=300):
    # Obtener las dimensiones originales
    alto, ancho = imagen.shape[:2]
    
    # Calcular el nuevo alto manteniendo la proporción
    proporcion = ancho_maximo / ancho
    nuevo_alto = int(alto * proporcion)
    
    # Redimensionar la imagen
    return cv2.resize(imagen, (ancho_maximo, nuevo_alto))

def procesar_frame(frame, session):
    try:
        # Redimensionar el frame
        frame = redimensionar_imagen(frame)
        
        # Convertir el frame a formato PIL
        frame_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        
        # Eliminar el fondo usando la sesión reutilizada
        frame_sin_fondo = remove(frame_pil, session=session)
        
        # Convertir de nuevo a formato OpenCV
        frame_sin_fondo_cv = cv2.cvtColor(np.array(frame_sin_fondo), cv2.COLOR_RGB2BGR)
        
        # Convertir a escala de grises para encontrar contornos
        gris = cv2.cvtColor(frame_sin_fondo_cv, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gris, 1, 255, cv2.THRESH_BINARY)
        
        # Aplicar operaciones morfológicas para mejorar la detección
        kernel = np.ones((5,5), np.uint8)
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
        
        # Encontrar contornos
        contornos, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filtrar contornos por área mínima
        area_minima = 1000  # Ajustar este valor según sea necesario
        contornos_filtrados = [cnt for cnt in contornos if cv2.contourArea(cnt) > area_minima]
        
        if contornos_filtrados:
            # Encontrar el contorno más grande
            contorno_max = max(contornos_filtrados, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(contorno_max)
            
            # Calcular el centroide del rectángulo
            centro_x = x + w // 2
            centro_y = y + h // 2
            
            return (x, y, w, h, centro_x, centro_y)
    except Exception as e:
        print(f"Error en procesamiento: {e}")
    
    return None

def worker_thread(frame_queue, result_queue, session):
    while True:
        if not frame_queue.empty():
            frame = frame_queue.get()
            if frame is None:
                break
            resultado = procesar_frame(frame, session)
            if resultado:
                result_queue.put(resultado)
            frame_queue.task_done()

def main():
    # Iniciar la captura de video
    cap = cv2.VideoCapture(1)
    
    # Configurar la resolución de captura
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    # Variables para el procesamiento intercalado
    contador_frames = 0
    FRAMES_A_SALTAR = 2
    ultimas_coordenadas = None
    
    # Crear colas para el procesamiento en segundo plano
    frame_queue = Queue(maxsize=2)
    result_queue = Queue(maxsize=2)
    
    # Crear una sesión reutilizable para rembg
    session = new_session()  # Volvemos al modelo por defecto
    
    # Iniciar el hilo de procesamiento
    worker = threading.Thread(target=worker_thread, args=(frame_queue, result_queue, session))
    worker.daemon = True
    worker.start()
    
    ultimo_tiempo = time.time()
    fps = 0
    fps_procesamiento = 0
    contador_procesamiento = 0
    ultimo_tiempo_procesamiento = time.time()
    
    while True:
        # Leer un frame del video
        ret, frame = cap.read()
        
        if not ret:
            print("Error al capturar el video")
            break
        
        # Redimensionar el frame para mostrar
        frame = redimensionar_imagen(frame)
        
        # Procesar solo cada N frames
        if contador_frames % FRAMES_A_SALTAR == 0 and frame_queue.qsize() < 2:
            frame_queue.put(frame.copy())
            contador_procesamiento += 1
            
            # Calcular FPS de procesamiento
            tiempo_actual = time.time()
            if tiempo_actual - ultimo_tiempo_procesamiento >= 1.0:
                fps_procesamiento = contador_procesamiento
                contador_procesamiento = 0
                ultimo_tiempo_procesamiento = tiempo_actual
        
        # Verificar si hay nuevos resultados
        if not result_queue.empty():
            ultimas_coordenadas = result_queue.get()
        
        # Dibujar el rectángulo y centroide usando las últimas coordenadas conocidas
        if ultimas_coordenadas:
            x, y, w, h, centro_x, centro_y = ultimas_coordenadas
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.circle(frame, (centro_x, centro_y), 5, (0, 255, 0), -1)
        
        # Calcular y mostrar FPS
        tiempo_actual = time.time()
        fps = 1 / (tiempo_actual - ultimo_tiempo)
        ultimo_tiempo = tiempo_actual
        
        # Mostrar FPS en pantalla
        cv2.putText(frame, f"FPS Video: {fps:.1f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, f"FPS Procesamiento: {fps_procesamiento}", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        # Mostrar el frame procesado
        cv2.imshow('Video con Detección', frame)
        
        # Incrementar contador de frames
        contador_frames += 1
        
        # Salir si se presiona 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    # Limpiar
    frame_queue.put(None)
    worker.join()
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
