from os import mkdir, makedirs, rmdir
from beamngpy import BeamNGpy, Scenario, Vehicle
from beamngpy.sensors import Electrics, Camera, PowertrainSensor
from beamngpy.api.beamng import TrafficApi
from utils.camera_utils import generate_video
from utils.can_parser import CANParser
from utils.sim_sup import get_sim_name, simulation_loop, set_bng_container_up, set_bng_container_down, get_coordinates_list
from utils import feat_treatment
from utils.reports import generate_report
from beamngpy.vehicle.lka import LaneKeepingAssist

def main(report):

    nome_sim = get_sim_name()

    # Inicializa o diretório da simulação
    makedirs(f'./data', exist_ok=True)
    mkdir(f'./data/{nome_sim}')
    mkdir(f'./data/{nome_sim}/imgs')

    # Instanciando o BeamNG
    beamng = BeamNGpy(host="127.0.0.1", port=25252, home="C:\Games\BeamNG.tech.v0.37.6.0", user=r"c:\Users\Pichau\AppData\Local\BeamNG\BeamNG.tech")
    beamng.open(launch=True)
    print('\033[34m[INFO]\033[0m   BeamNG iniciado')

    # Instanciando o CANParser
    dbc_path = './dbc/byd.dbc'
    can_parser = CANParser(dbc_path)

    # Configurando o cenário
    scenario = Scenario("inmetroTake3", "vehicle logging")
    
    vehicle = Vehicle("ego_vehicle", model="brenoveras_hb20_premium", license="LAINF", part_config='vehicles/sbr/electric_300.pc')
    scenario.add_vehicle(
        vehicle,
        pos=(-769.1, 400.8, 142.8), rot_quat=(0.0173, -0.0019, -0.6354, 0.7720)
    )

    scenario.make(beamng)
    print("\033[34m[INFO]\033[0m   Cenário construído")

    # Setando determinismo e iniciando cenário
    beamng.settings.set_deterministic(60)
    beamng.scenario.load(scenario)
    beamng.scenario.start()
    print("\033[34m[INFO]\033[0m   Cenário iniciado")
    
    # Pausa a simulação, para ser controlada pelos steps
    #beamng.pause()    

    # Instanciando APIs
    trafficApi = TrafficApi(beamng)

    # Instanciando e anexando sensor do veículo
    electrics = Electrics()
    vehicle.attach_sensor('electrics', electrics)
    powertrain = PowertrainSensor('powertrain', beamng, vehicle, is_send_immediately=True)

    # Configurando a câmera
    camera = Camera(
        "camera1",
        beamng,
        vehicle,
        requested_update_time=0.01,
        pos=(-0.3, 1, 2),
        dir=(0, -1, 0),
        field_of_view_y=70,
        near_far_planes=(0.1, 1000),
        resolution=(1024, 1024)
    )
    
    # Inserindo tráfego
    trafficApi.spawn(
        max_amount=2,
        police_ratio=0,
        extra_amount=2,
        parked_amount=10
    )  

    # Colunas dos dados que serão coletados, juntamente com o seu método de tratamento
    colunas = {
        'fuel': feat_treatment.ratio_to_100,
        'brake_input': feat_treatment.ratio_to_256,
        'throttle': feat_treatment.ratio_to_256,
        'vel': feat_treatment.get_vel,
        #'outputTorque1': feat_treatment.times_1 (O HB20 não esse parametro)
    }
    
    script_path = r"c:\Users\Pichau\AppData\Local\BeamNG\BeamNG.tech\current\levels\inmetrotake3\trajectory.json"
    script = vehicle.ai.import_script_ai_file(script_path)
    vehicle.ai.execute_script(script, True)

    # Looping da simulação
    simulation_loop(beamng, nome_sim, vehicle, camera, colunas, 1000000, can_parser, powertrain)

    # Monta e salva o vídeo gerado
    print('\033[34m[INFO]\033[0m   Montando vídeo')
    generate_video(nome_sim)
    rmdir(f'./data/{nome_sim}/imgs')
    print('\033[34m[INFO]\033[0m   Vídeo salvo')

    print('\033[34m[INFO]\033[0m   CSV salvo')
    print(f"\033[34m[INFO]\033[0m  Dados salvos em {nome_sim}")

    # Fecha a conexão com o BeamNg
    #beamng.close()
    print('\033[34m[INFO]\033[0m   BeamNG encerrado')

    if report:
        print('\033[34m[INFO]\033[0m   Gerando relatório do percurso')
        generate_report(nome_sim)
        print('\033[34m[INFO]\033[0m   Relatório gerado')

if __name__ == "__main__":
    main(True)