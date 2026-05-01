from datetime import datetime
from math import sqrt, atan2, degrees
from time import time, sleep
import pandas as pd
import numpy as np
import csv
import cv2
import docker
import json
from subprocess import Popen, DEVNULL
from random import sample, seed
from beamngpy import ScenarioObject
from pprint import pprint

def set_bng_container_up():
    """
    Levanta o container do BeamNG
    """

    # O bloco dentro do try especifica quando existe um conteiner do bng em execução.
    client = docker.from_env()
    try:
        client.containers.get("beamng-ubuntu22")
        print('\033[31m[ERRO]\033[0m   Já existe uma instância de simulação. Finalizando...')
        return False
    except docker.errors.NotFound:
        # Caso não exista, levanta o conteiner
        print('\033[34m[INFO]\033[0m   Levantando contêiner do bng...')
        process = Popen(['docker', 'compose', 'up', 'beamng-ubuntu22'], cwd='/opt/BeamNG/BeamNG.tech.v0.37.6.0/tech/docker', stdout=DEVNULL, stderr=DEVNULL)
        
        # TODO: substituir pela verificação de status do contêiner 
        sleep(10)
        
        return True

def set_bng_container_down():
    """
    Derruba o contêiner do BeamNG após a execução da simulação
    """
    client = docker.from_env()
    try:
        client.containers.get("beamng-ubuntu22")
        print('\033[34m[INFO]\033[0m   Finalizando o contêiner')
        Popen(['docker', 'kill', 'beamng-ubuntu22'], stdout=DEVNULL, stderr=DEVNULL)
        sleep(10)
        Popen(['docker', 'rm', 'beamng-ubuntu22'], stdout=DEVNULL, stderr=DEVNULL)
    except docker.errors.NotFound:
        print('\033[31m[ERRO]\033[0m   Não existe uma instância da simulação. Finalizando...')

def get_sim_name(): 
    """
    Retorna uma string com a identificação da simulação a ser executada
    """

    agora = datetime.now()
    sim_name = f"s_{agora.year}{agora.month:02d}{agora.day:02d}_{agora.hour:02d}{agora.minute:02d}"
    return sim_name


def get_pitch(forward):
    """
    Retorna o pitch do carro em graus.
    Positive -> nariz para cima
    Negative -> nariz para baixo
    """
    # forward projetado no plano XY
    fx, fy, fz = forward
    proj_length = sqrt(fx*fx + fy*fy)
    pitch = degrees(atan2(fz, proj_length))
    return pitch

def simulation_loop(bng, sim_name, vehicle, camera, features, length, can_parser, powertrain):

    with open(f'./data/{sim_name}/readable.csv', 'w', newline='') as file, open(f'./data/{sim_name}/can.log', 'w') as file_can, open(f'./data/{sim_name}/can_debug.log', 'w') as can_debbug_file:

        # Prepara o cabeçalho da saída .csv
        cabecalho = ['time', 'step', 'angle', 'posX', 'posY', 'posZ'] + list(features.keys())

        # Iniciar o objeto de escrita csv
        writer = csv.writer(file, delimiter=';')

        # Escreve o cabeçalho
        writer.writerow(cabecalho)
        
        try:
            print('\033[34m[INFO]\033[0m   Coletando dados')
            
            patience = 0

            # Looping da simulação
            for i in range(1, length):

                if patience > 10:
                    print('\033[34m[INFO]\033[0m   Carro encerrou o trajeto. Finalizando...')
                    break

                leitura = []
                leitura_can = []

                # Atualiza os sensores
                vehicle.sensors.poll()
        
                # Captura um frame para montar saída
                if i % 10 == 0:
                    frame = camera.poll_raw()

                    arr = np.frombuffer(frame['colour'], dtype=np.uint8)

                    arr = arr.reshape((1024, 1024, 3))     

                    arrbgr = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)

                    cv2.imwrite(f'./data/{sim_name}/imgs/f{i}.png', arrbgr)

                tmstamp = time()

                if i % 1000 == 0:
                    print(f'\033[32m[SIMU]\033[0m  step {i}')

                # Recupera informações posicionais do veículo
                dir_vector = vehicle.state['dir']
                x, y, z = vehicle.state['pos']
                elev_angle = get_pitch(dir_vector)

                # Adiciona no CSV: step, timestamp e informações posicionais
                leitura.append(tmstamp)
                leitura.append(i)
                leitura.append(elev_angle)
                leitura.append(x)
                leitura.append(y)
                leitura.append(z)

                # Incrementa a leitura com os valores de sensor do carro
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

                # Faz o tratamento específico da feature
                for i, col in enumerate(features.keys()):
                    treated_value = features[col](valores[i])

                    if col == "vel":
                        if int(treated_value) == 0:
                            patience += 1
                        else:
                            patience = 0

                    log_line = can_parser.log(col, treated_value)
                    leitura_can.append(log_line)
                    can_debbug_file.write(f'{log_line} -> {col} : {treated_value}\n')

                # Escreve a leitura atual
                writer.writerow(leitura)
                
                # Escreve no arquivo CAN
                for leitura in leitura_can:
                    file_can.write(f'{leitura}\n')

                sleep(1.0)

        except KeyboardInterrupt:
            print('\033[33m[WARN]\033[0m   Interrompendo simulação')

def get_waypoints_list():
    """
    Função responsável por retornar o conjunto de coordenadas em que o veículo irá trafegar
    Args:
        coordinates: coordenadas dos pontos
    Returns:
        Lista com o nome dos waypoints do trajeto
    """
        
    wps = []
    
    with open("wps/west_coast_usa.ndjson", "r", encoding="utf-8") as f:
        for linha in f:
            wps.append(json.loads(linha))

    seed(42)

    amostra = sample(wps, k=5)

    amostra = [w['name'] for w in amostra]

    print(amostra)

    return amostra

def get_coordinates_list():
    """
    Função responsável por retornar o conjunto de coordenadas em que o veículo irá trafegar
    Returns:
        Lista com as coordenadas dos waypoints do trajeto
    """
    waypoints = []
    with open("wps/west_coast_usa.ndjson", "r", encoding="utf-8") as f:
        for line in f:
            waypoints.append(json.loads(line))

    seed(42)

    random_samples = sample(waypoints, k=5)

    coordinates = []

    for s in random_samples:
        s['speed'] = 30
        coordinates.append(s)

    return coordinates
