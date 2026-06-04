"""Simulation support utilities - core simulation setup and execution"""

from datetime import datetime
from math import sqrt, atan2, degrees
from time import time, sleep
import numpy as np
import csv
import cv2
import docker
from subprocess import Popen, DEVNULL
from beamngpy import Scenario, Vehicle
from beamngpy.sensors import Electrics, Camera, PowertrainSensor
from beamngpy.api.beamng import TrafficApi
import config


def set_bng_container_up():
    """Levanta o container do BeamNG"""
    client = docker.from_env()
    try:
        client.containers.get("beamng-ubuntu22")
        print('\033[31m[ERRO]\033[0m   Já existe uma instância de simulação')
        return False
    except docker.errors.NotFound:
        print('\033[34m[INFO]\033[0m   Levantando contêiner do bng...')
        Popen(['docker', 'compose', 'up', 'beamng-ubuntu22'], cwd='/opt/BeamNG/BeamNG.tech.v0.37.6.0/tech/docker', stdout=DEVNULL, stderr=DEVNULL)
        sleep(10)
        return True


def set_bng_container_down():
    """Derruba o contêiner do BeamNG"""
    client = docker.from_env()
    try:
        client.containers.get("beamng-ubuntu22")
        print('\033[34m[INFO]\033[0m   Finalizando o contêiner')
        Popen(['docker', 'kill', 'beamng-ubuntu22'], stdout=DEVNULL, stderr=DEVNULL)
        sleep(10)
        Popen(['docker', 'rm', 'beamng-ubuntu22'], stdout=DEVNULL, stderr=DEVNULL)
    except docker.errors.NotFound:
        print('\033[31m[ERRO]\033[0m   Não existe uma instância da simulação')


def get_sim_name():
    """Retorna nome da simulação com timestamp"""
    agora = datetime.now()
    return f"s_{agora.year}{agora.month:02d}{agora.day:02d}_{agora.hour:02d}{agora.minute:02d}"


def get_pitch(forward):
    """Retorna o pitch do carro em graus (positivo=nariz pra cima)"""
    fx, fy, fz = forward
    proj_length = sqrt(fx*fx + fy*fy)
    return degrees(atan2(fz, proj_length))


def setup_simulation(beamng, circuit_key, vehicle_model='hb20', enable_traffic=False, drive_mode='waypoints', speed=None, laps=None):
    """
    Configura cenário, veículo e sensores
    
    Args:
        beamng: instância BeamNG
        circuit_key: chave do circuito em config.CIRCUITS
        vehicle_model: modelo do veículo (default: hb20)
        enable_traffic: ativar tráfego
        drive_mode: 'waypoints' ou 'traffic'
        speed: velocidade do AI (km/h)
        laps: número de voltas
    """
    circuit = config.CIRCUITS[circuit_key]
    vehicle_cfg = config.VEHICLE_MODELS[vehicle_model]
    
    # Cenário
    scenario = Scenario(config.SCENARIO, config.SCENARIO_NAME)
    vehicle = Vehicle("ego_vehicle", model=vehicle_cfg['model'], license=config.VEHICLE_LICENSE, part_config=vehicle_cfg['part_config'])
    scenario.add_vehicle(vehicle, pos=circuit['spawn_point'], rot_quat=(0, 0, 0.675, 0.737))
    scenario.make(beamng)
    print("\033[34m[INFO]\033[0m   Cenário construído")
    
    # Inicia cenário
    beamng.settings.set_deterministic(config.DETERMINISTIC_FPS)
    beamng.scenario.load(scenario)
    beamng.scenario.start()
    print("\033[34m[INFO]\033[0m   Cenário iniciado")
    
    # Sensores
    electrics = Electrics()
    vehicle.attach_sensor('electrics', electrics)
    powertrain = PowertrainSensor('powertrain', beamng, vehicle, is_send_immediately=True)
    
    # Câmera
    camera = Camera(
        "camera1", beamng, vehicle,
        requested_update_time=config.CAMERA_CONFIG['update_time'],
        pos=config.CAMERA_CONFIG['pos'],
        dir=config.CAMERA_CONFIG['dir'],
        field_of_view_y=config.CAMERA_CONFIG['fov_y'],
        near_far_planes=config.CAMERA_CONFIG['near_far'],
        resolution=config.CAMERA_CONFIG['resolution']
    )
    
    # Tráfego
    if enable_traffic:
        traffic_api = TrafficApi(beamng)
        traffic_api.spawn(**config.TRAFFIC_CONFIG)
    
    # Modo de direção
    vehicle.ai.set_aggression(config.DEFAULT_AGGRESSION)
    
    if drive_mode == 'waypoints':
        speed = speed or config.DEFAULT_SPEED
        laps = laps or config.DEFAULT_LAPS
        vehicle.ai.drive_using_waypoints(
            circuit['waypoints'],
            drive_in_lane=True,
            avoid_cars=True,
            no_of_laps=laps,
            route_speed=speed,
            route_speed_mode='limit'
        )
    else:
        vehicle.ai.set_mode('traffic')
    
    return vehicle, camera, electrics, powertrain


def simulation_loop(bng, sim_name, vehicle, camera, features, can_parser, powertrain):
    """Loop principal de coleta de dados"""
    
    from utils import feat_treatment
    
    with open(f'./data/{sim_name}/readable.csv', 'w', newline='') as file, \
         open(f'./data/{sim_name}/can.log', 'w') as file_can, \
         open(f'./data/{sim_name}/can_debug.log', 'w') as can_debbug_file:
        
        header = ['time', 'step', 'angle', 'posX', 'posY', 'posZ'] + list(features.keys())
        writer = csv.writer(file, delimiter=';')
        writer.writerow(header)
        
        try:
            print('\033[34m[INFO]\033[0m   Coletando dados')
            patience = 0
            
            for i in range(1, config.SIM_MAX_STEPS):
                if patience > config.PATIENCE_THRESHOLD:
                    print('\033[34m[INFO]\033[0m   Carro encerrou o trajeto')
                    break
                
                vehicle.sensors.poll()
                
                if i % config.FRAME_CAPTURE_INTERVAL == 0:
                    frame = camera.poll_raw()
                    arr = np.frombuffer(frame['colour'], dtype=np.uint8).reshape((1024, 1024, 3))
                    arrbgr = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
                    cv2.imwrite(f'./data/{sim_name}/imgs/f{i}.png', arrbgr)
                
                if i % 1000 == 0:
                    print(f'\033[32m[SIMU]\033[0m  step {i}')
                
                leitura = [time(), i, get_pitch(vehicle.state['dir'])] + list(vehicle.state['pos'])
                leitura_can = []
                
                data = vehicle.sensors['electrics'].data
                valores = []
                for j in features.keys():
                    if j == 'outputTorque1':
                        valores.append(powertrain.poll()['rearMotor']['outputTorque1'])
                    elif j == 'vel':
                        valores.append(vehicle.state['vel'])
                    else:
                        valores.append(data[j])
                
                leitura.extend(valores)
                
                for i, col in enumerate(features.keys()):
                    treatment_func = getattr(feat_treatment, features[col])
                    treated_value = treatment_func(valores[i])
                    
                    if col == "vel" and int(treated_value) == 0:
                        patience += 1
                    else:
                        patience = 0
                    
                    log_line = can_parser.log(col, treated_value)
                    leitura_can.append(log_line)
                    can_debbug_file.write(f'{log_line} -> {col} : {treated_value}\n')
                
                writer.writerow(leitura)
                for leitura in leitura_can:
                    file_can.write(f'{leitura}\n')
                
                sleep(config.SIM_STEP_SLEEP)
        
        except KeyboardInterrupt:
            print('\033[33m[WARN]\033[0m   Interrompendo simulação')
