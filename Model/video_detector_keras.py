import cv2
import numpy as np
from PIL import Image
import tensorflow as tf

MODEL_PATH = "HyperWasteClassificator.keras"
camera = 1
REMOVER_FONDO = False  # Variable para controlar si se remueve el fondo

def cargar_modelo():
    """Carga el modelo de clasificación de desechos desde archivo local."""
    try:
        model_clasificacion = tf.keras.models.load_model(MODEL_PATH)
        return model_clasificacion
    except Exception as e:
        print(f"Error al cargar el modelo: {e}")
        return None

def clasificar_desecho(frame, model_clasificacion):
    """Clasifica el material de la imagen."""
    try:
        # Convertir el frame a formato PIL
        imagen_pil = Image.fromarray(frame).convert("RGB")
        
        # Redimensionar la imagen al tamaño esperado por el modelo (ajustar según sea necesario)
        imagen_pil = imagen_pil.resize((224, 224))
        
        # Convertir a array numpy y normalizar
        imagen_array = np.array(imagen_pil) / 255.0
        imagen_array = np.expand_dims(imagen_array, axis=0)
        
        # Realizar la predicción
        predicciones = model_clasificacion.predict(imagen_array, verbose=0)[0]
        
        labels_clasificacion = {
            "0": "Baterias", "1": "Carton", "2": "Metal", 
            "3": "Papel", "4": "Plastico", "5": "Vidrio"
        }
        
        predictions = {labels_clasificacion[str(i)]: round(float(predicciones[i]), 3) 
                      for i in range(len(predicciones))}
        print('predictions', predictions)
        return predictions
    except Exception as e:
        print(f"Error al clasificar desecho: {e}")
        return {}

def procesar_video():
    """Procesa el video de la cámara en tiempo real y clasifica los desechos."""
    # Cargar modelo
    model_clasificacion = cargar_modelo()
    if model_clasificacion is None:
        return

    # Inicializar la cámara
    cap = cv2.VideoCapture(camera)
    if not cap.isOpened():
        print("Error: No se pudo abrir la cámara.")
        return

    # Configurar la resolución de la cámara
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    # Variables para controlar el procesamiento
    frame_count = 0
    frame_interval = 10  # Procesar cada 10 frames
    ultima_clasificacion = None

    print("Presiona 'ESC' para salir")
    print("La cámara está activa. Mostrando clasificación en tiempo real...")
    print(f"Remover fondo: {'Activado' if REMOVER_FONDO else 'Desactivado'}")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error al capturar frame de la cámara")
            break

        frame_count += 1
        
        # Solo procesar cada frame_interval frames
        if frame_count % frame_interval == 0:
            try:
                resultados_clasificacion = clasificar_desecho(
                    frame, 
                    model_clasificacion,
                )
                
                if resultados_clasificacion:
                    material = max(resultados_clasificacion, key=resultados_clasificacion.get)
                    confianza_material = resultados_clasificacion[material]
                    ultima_clasificacion = f"{material} ({confianza_material:.2f})"
            except Exception as e:
                print(f"Error en el procesamiento: {e}")

        # Mostrar la última clasificación si existe
        if ultima_clasificacion:
            cv2.putText(frame, ultima_clasificacion, (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2, cv2.LINE_AA)

        # Mostrar instrucciones en pantalla
        cv2.putText(frame, "Presiona 'ESC' para salir", (10, frame.shape[0] - 20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1, cv2.LINE_AA)

        cv2.imshow("Clasificación de Desechos - Cámara en Tiempo Real", frame)
        
        # Salir con ESC
        if cv2.waitKey(1) == 27:
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    procesar_video() 