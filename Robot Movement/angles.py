import numpy as np

from move_arm import mover_servo

servo_calibration = {
    "q1": {
        "min_angle": 0,
        "max_angle": 90,
        "min_pulse": 1505,
        "max_pulse": 2418,
        "offset": 0,
    },
    "q2": {
        "min_angle": 20,
        "max_angle": 90,
        "min_pulse": 942,
        "max_pulse": 1250,
        "offset": 0,
        "gravity_comp": {0: 0, 10: 2, 20: 5, 30: 8},
    },
    "q3": {
        "min_angle": 45,
        "max_angle": 180,
        "min_pulse": 1904,
        "max_pulse": 448,
        "offset": 0,
    },
    "q4": {
        "min_angle": 72,
        "max_angle": 110,
        "min_pulse": 2464,
        "max_pulse": 2096,
        "offset": 0,
    },
    "q5": {
        "min_angle": 0,
        "max_angle": 90,
        "min_pulse": 946,
        "max_pulse": 1900,
        "offset": 0,
    },
}


def angulos_pulsos(z, joint_name):
    """Improved pulse calculation with individual joint calibration"""
    cal = servo_calibration[joint_name]
    # Linear mapping with bounds checking
    pulse = np.interp(
        z, [cal["min_angle"], cal["max_angle"]], [cal["min_pulse"], cal["max_pulse"]]
    )
    return round(pulse, 5)


def angulos_pulsos_manual(z, joint_name):
    """Manual pulse calculation with individual joint calibration"""
    cal = servo_calibration[joint_name]
    # Linear mapping with bounds checking
    proporcion = (z - cal["min_angle"]) / (cal["max_angle"] - cal["min_angle"])
    pulse = cal["min_pulse"] + proporcion * (cal["max_pulse"] - cal["min_pulse"])
    return round(pulse, 5)


def pulsos(q1, q2, q3, q4, q5):
    """Updated pulse calculation using calibrated parameters"""
    return [
        angulos_pulsos(q1, "q1"),
        angulos_pulsos(q2, "q2"),
        angulos_pulsos(q3, "q3"),
        angulos_pulsos(q4, "q4"),
        angulos_pulsos(q5, "q5"),
    ]


if __name__ == "__main__":
    q1 = 0
    q2 = 45
    q3 = 90
    q4 = 0
    q5 = 0
    print(pulsos(q1, q2, q3, q4, q5))
    mover_servo(8, pulsos(q1, q2, q3, q4, q5)[4])
