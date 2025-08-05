from math import acos,pow,atan,sqrt,degrees,asin, atan2
import numpy as np
from save_results import guardar_resultados
from angles import angulos_pulsos, pulsos, servo_calibration
# Calibrated link lengths (measure these precisely with calipers)
e1, e2, e3, e4, e5, cinta_offset = 6, 10, 12, 5, 6, 8     # Updated with precise measurements

def solucion(x, y, z, orientacion, cinta=False):
    
    # Apply calibration
    m = cinta_offset if cinta else 0
    a = (e4 + e5 + m - e1)
    
    # Calculate base parameters
    b = sqrt(x**2 + y**2)
    c = sqrt(a**2 + b**2)
    
    # Check reachability
    if not (a < c and b < c):
        return None, None
    
    # Calculate base angles
    q1 = degrees(atan2(y, x))
    
    # Shoulder joint calculation with corrected geometric relationships
    alpha1 = asin(a / c)
    alpha2 = acos((c**2 + e2**2 - e3**2) / (2 * c * e2))
    q2 = degrees(alpha2 + alpha1)  # Adjusted for correct shoulder angle
    
    # Elbow joint
    q3 =degrees(acos((e2**2 + e3**2 - c**2) / (2 * e2 * e3)))
    
    # Wrist joint with stability factor
    beta1 = asin(b / c)
    beta2 = acos((c**2 + e3**2 - e2**2) / (2 * c * e3))
    q4 = degrees(beta1 + beta2)
    
    # Orientation
    q5 = orientacion
    
    # Ensure joints stay within limits
    q2 = max(min(q2, servo_calibration['q2']['max_angle']), servo_calibration['q2']['min_angle'])
    q3 = max(min(q3, servo_calibration['q3']['max_angle']), servo_calibration['q3']['min_angle'])
    
    pulses = pulsos(q1, q2, q3, q4, q5)
    newQ5 = angulos_pulsos(-q1, 'q5')
    
    # Guardar resultados en el archivo JSON
    guardar_resultados(x, y, z, orientacion, q1, q2, q3, q4, q5, pulses, newQ5)
    
    return pulses, newQ5