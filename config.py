"""Configuration and constants for BeamNG simulation"""

# Circuitos do INMETRO
CIRCUITS = {
    'c1': {
        'name': 'Circuito ao redor dos prédios',
        'spawn_point': (111.048, 245.349, 23.921),
        'waypoints': ['c1_1', 'c1_2', 'c1_3', 'c1_4', 'c1_5', 'c1_6', 'c1_7', 'c1_8', 'c1_9', 'c1_10', 'c1_11', 'c1_12', 'c1_13', 'c1_1']
    },
    'c2': {
        'name': 'Subindo e descendo o prédio 20',
        'spawn_point': (111.048, 245.349, 23.921),
        'waypoints': ['c2_1', 'c2_2', 'c2_3', 'c2_4', 'c2_5', 'c2_6', 'c2_7', 'c2_8', 'c2_9', 'c2_10', 'c2_11', 'c2_12', 'c2_13', 'c2_14', 'c2_15', 'c2_16', 'c2_17', 'c2_18', 'c2_19', 'c2_20', 'c2_21', 'c2_22', 'c2_23', 'c2_24', 'c2_25', 'c2_26', 'c2_27', 'c2_28', 'c2_29', 'c2_30', 'c2_31', 'c2_32', 'c2_33', 'c2_34']
    },
    'c3': {
        'name': 'DIMCI até a rotatória',
        'spawn_point': (111.048, 245.349, 23.921),
        'waypoints': ['c3_1', 'c3_2', 'c3_3', 'c3_4', 'c3_5', 'c3_6', 'c3_7']
    },
    'c4': {
        'name': 'DIMCI até rotatória com caminho inverso',
        'spawn_point': (111.048, 245.349, 23.921),
        'waypoints': ['c3_1', 'c3_2', 'c3_3', 'c3_4', 'c3_5', 'c3_6', 'c4_1', 'c4_2', 'c4_3', 'c4_4', 'c4_5', 'c4_6', 'c4_7', 'c4_8']
    }
}

# Configurações padrão
BEAMNG_HOST = "127.0.0.1"
BEAMNG_PORT = 25252
BEAMNG_HOME = r"C:\Games\BeamNG.tech.v0.37.6.0"
BEAMNG_USER = r"c:\Users\Pichau\AppData\Local\BeamNG\BeamNG.tech"

SCENARIO = "inmetro"
SCENARIO_NAME = "vehicle logging"

# Modelos de veículo
VEHICLE_MODELS = {
    'hb20': {'model': 'brenoveras_hb20_premium', 'part_config': 'vehicles/sbr/electric_300.pc'},
    'sbr': {'model': 'sbr', 'part_config': 'vehicles/sbr/electric_300.pc'},
}
DEFAULT_MODEL = 'hb20'

VEHICLE_LICENSE = "LAINF"

# Sensores e dados
DBC_FILE = './dbc/byd.dbc'
DATA_COLUMNS = {
    'fuel': 'ratio_to_100',
    'brake_input': 'ratio_to_256',
    'throttle': 'ratio_to_256',
    'vel': 'get_vel',
}

# Câmera
CAMERA_CONFIG = {
    'update_time': 0.01,
    'pos': (-0.3, 1, 3),
    'dir': (0, -1, 0),
    'fov_y': 70,
    'near_far': (0.1, 1000),
    'resolution': (1024, 1024)
}

# Simulação
DEFAULT_CIRCUIT = 'c1'
DEFAULT_SPEED = 12
DEFAULT_LAPS = 1
DEFAULT_AGGRESSION = 0.3
SIM_MAX_STEPS = 1000000
FRAME_CAPTURE_INTERVAL = 10
SIM_STEP_SLEEP = 1.0
PATIENCE_THRESHOLD = 10

# Tráfego
TRAFFIC_CONFIG = {
    'max_amount': 2,
    'police_ratio': 0,
    'extra_amount': 2,
    'parked_amount': 10
}

ROUTE_SPEED_MODES = ['limit', 'set']
DEFAULT_ROUTE_SPEED_MODE = 'limit'

# Determinismo
DETERMINISTIC_FPS = 60
VIDEO_FPS = 10
VIDEO_CODEC = "mp4v"