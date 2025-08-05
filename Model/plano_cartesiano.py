import cv2
import numpy as np

def dibujar_plano_cartesiano(frame):
    # Obtener dimensiones del frame
    height, width = frame.shape[:2]
    # El origen ahora está más pegado a la esquina
    origen_x = 20  # Margen izquierdo reducido
    origen_y = height - 20  # Margen inferior reducido
    
    # Dibujar ejes
    cv2.line(frame, (origen_x, origen_y), (width - 20, origen_y), (0, 0, 255), 2)  # Eje X
    cv2.line(frame, (origen_x, origen_y), (origen_x, 20), (0, 0, 255), 2)  # Eje Y
    
    # Dibujar números en los ejes
    espacio_x = 44  # Espacio para el eje X
    espacio_y = 34  # Espacio para el eje Y
    for i in range(0, 21):  # Aumentar el rango de números (0 al 20)
        # Números en eje X
        x = origen_x + i * espacio_x
        if x < width - 20:
            cv2.putText(frame, str(i), (x, origen_y + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
            cv2.line(frame, (x, origen_y - 5), (x, origen_y + 5), (0, 0, 255), 1)
        
        # Números en eje Y
        y = origen_y - i * espacio_y
        if y > 20:
            cv2.putText(frame, str(i), (origen_x - 15, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
            cv2.line(frame, (origen_x - 5, y), (origen_x + 5, y), (0, 0, 255), 1)

def calcular_coordenadas(x, y, origen_x, origen_y):
    # Convertir coordenadas de píxeles a coordenadas cartesianas positivas
    coord_x = (x - origen_x) / 44  # Espacio para el eje X
    coord_y = (origen_y - y) / 34  # Espacio para el eje Y
    return round(coord_x, 2), round(coord_y, 2)

def main():
    # Inicializar la cámara
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Error: No se pudo abrir la cámara")
        return
    
    # Crear ventana
    cv2.namedWindow('Plano Cartesiano')
    # Establecer tamaño de la ventana (ancho, alto)
    cv2.resizeWindow('Plano Cartesiano', 1280, 720)
    
    # Variable para almacenar el último punto y sus coordenadas
    ultimo_punto = None
    zoom = 1.0  # Zoom inicial
    
    def mouse_callback(event, x, y, flags, param):
        nonlocal ultimo_punto, zoom
        origen_x = 20  # Margen izquierdo reducido
        origen_y = param['frame'].shape[0] - 20  # Margen inferior reducido
        
        if event == cv2.EVENT_LBUTTONDOWN:  # Clic izquierdo
            coord_x, coord_y = calcular_coordenadas(x, y, origen_x, origen_y)
            # Solo guardar el punto si está en el primer cuadrante
            if coord_x >= 0 and coord_y >= 0:
                ultimo_punto = (x, y, coord_x, coord_y)
        elif event == cv2.EVENT_RBUTTONDOWN:  # Clic derecho
            ultimo_punto = None
        elif event == cv2.EVENT_MOUSEWHEEL:  # Rueda del mouse
            if flags > 0:  # Scroll hacia arriba
                zoom = min(zoom + 5, 1000.0)  # Aumentar zoom con límite muy alto
            else:  # Scroll hacia abajo
                zoom = max(zoom - 5, 1.0)  # Disminuir zoom
            
            # Aplicar zoom a la cámara
            cap.set(cv2.CAP_PROP_ZOOM, zoom)
    
    # Configurar callback del mouse
    param = {'frame': None}
    cv2.setMouseCallback('Plano Cartesiano', mouse_callback, param)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: No se pudo leer el frame")
            break
        
        # Redimensionar el frame al tamaño deseado
        frame = cv2.resize(frame, (1280, 720))
        
        # Actualizar el frame en los parámetros
        param['frame'] = frame
        
        # Dibujar el plano cartesiano
        dibujar_plano_cartesiano(frame)
        
        # Dibujar el último punto si existe
        if ultimo_punto is not None:
            x, y, coord_x, coord_y = ultimo_punto
            cv2.circle(frame, (x, y), 5, (0, 0, 255), -1)
            texto = f"({coord_y}, {coord_x})"  # Invertir el orden de las coordenadas
            cv2.putText(frame, texto, (x + 10, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
        
        # Mostrar el nivel de zoom actual
        cv2.putText(frame, f"Zoom: {zoom:.1f}x", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Mostrar el frame
        cv2.imshow('Plano Cartesiano', frame)
        
        # Salir con 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main() 