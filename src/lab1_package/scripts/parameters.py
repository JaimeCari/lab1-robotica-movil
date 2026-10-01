
MOVE_BINDINGS = {
    'i': (0.2, 0.0),
    'j': (-0.2, 0.0),
    'a': (0.0, 1.0),
    's': (0.0, -1.0),
    'q': (0.2, 1.0),
    'w': (0.2, -1.0),
}

INSTRUCTIONS = (
            "Presiona o mantén presionada una tecla para mover el robot:\n\n"
            "  i : avanzar          j : retroceder\n"
            "  a : rotar +          s : rotar -\n"
            "  q : avanzar + rotar +   w : avanzar + rotar -\n"
        )

DATA_DIR = "/home/jaimecari/Documents/ROB_MOVIL/lab01_ws/data"

PATH_POSE_LOADER = "/home/jaimecari/Documents/ROB_MOVIL/lab01_ws/src/lab1_package/config/poses.txt"

EPS = 1e-7  
FACTOR_CORRECCION = 1.0911736178