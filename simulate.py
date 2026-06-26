#!/usr/bin/env python3
"""Main simulation script - parametrized entry point"""

import argparse
import sys
from os import mkdir, makedirs, rmdir
from beamngpy import BeamNGpy
from utils.camera_utils import generate_video
from utils.can_parser import CANParser
from utils.sim_sup import get_sim_name, setup_simulation, simulation_loop, set_bng_container_up, set_bng_container_down
from utils.reports import generate_report
from utils import feat_treatment
import config


def run_simulation(circuit='c1', speed=None, laps=None, use_container=False, enable_report=False, enable_traffic=False, vehicle_model='hb20', repetitions=1):
    """Execute simulation with given parameters"""

    # Convertendo km/h para m/s
    if speed is not None:
        speed = speed / 3.6

    for rep in range(repetitions):
        print(f"\n{'='*60}")
        if repetitions > 1:
            print(f"Repetição {rep+1}/{repetitions}")
        print(f"Circuito: {config.CIRCUITS[circuit]['name']}")
        print(f"Velocidade: {speed or config.DEFAULT_SPEED} km/h | Voltas: {laps or config.DEFAULT_LAPS}")
        print(f"Tráfego: {'Ativado' if enable_traffic else 'Desativado'}")
        print(f"{'='*60}\n")
        
        # Container setup
        if use_container and not set_bng_container_up():
            return False
        
        # Convertendo km/h para m/s
        if speed is not None:
            speed = speed / 3.6

        # Simulation name
        nome_sim = get_sim_name()
        
        # Create directories
        makedirs(f'./data', exist_ok=True)
        mkdir(f'./data/{nome_sim}')
        mkdir(f'./data/{nome_sim}/imgs')
        
        try:
            # Initialize BeamNG
            beamng = BeamNGpy(host=config.BEAMNG_HOST, port=config.BEAMNG_PORT, home=config.BEAMNG_HOME, user=config.BEAMNG_USER)
            beamng.open(launch=not use_container)
            print('\033[34m[INFO]\033[0m   BeamNG iniciado')
            
            # Initialize CAN parser
            can_parser = CANParser(config.DBC_FILE)
            
            # Setup simulation
            vehicle, camera, electrics, powertrain = setup_simulation(
                beamng, circuit, vehicle_model, enable_traffic, 'waypoints', speed, laps
            )
            
            # Build feature columns
            features = {}
            for col, treatment in config.DATA_COLUMNS.items():
                features[col] = treatment
            
            # Run simulation loop
            simulation_loop(beamng, nome_sim, vehicle, camera, features, can_parser, powertrain)
            
            # Generate video
            print('\033[34m[INFO]\033[0m   Montando vídeo')
            generate_video(nome_sim)
            rmdir(f'./data/{nome_sim}/imgs')
            print('\033[34m[INFO]\033[0m   Vídeo salvo')
            
            print('\033[34m[INFO]\033[0m   CSV salvo')
            print(f"\033[34m[INFO]\033[0m  Dados salvos em ./data/{nome_sim}")
            
            # Disconnect
            beamng.disconnect()
            print('\033[34m[INFO]\033[0m   BeamNG encerrado')
            
            # Generate report
            if enable_report:
                print('\033[34m[INFO]\033[0m   Gerando relatório do percurso')
                generate_report(nome_sim)
                print('\033[34m[INFO]\033[0m   Relatório gerado')
        
        except Exception as e:
            print(f'\033[31m[ERRO]\033[0m   Erro durante simulação: {e}')
            import traceback
            traceback.print_exc()
            return False
        
        finally:
            # Container cleanup
            if use_container:
                set_bng_container_down()
    
    return True


def main():
    parser = argparse.ArgumentParser(
        description='Execute simulação veicular no BeamNG',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  python simulate.py --circuit c1 --speed 15
  python simulate.py --circuit c3 --laps 2 --repetitions 3
  python simulate.py --circuit c2 --traffic --report
  python simulate.py --circuit c4 --speed 20 --laps 2 --repetitions 5 --report
        """
    )
    
    parser.add_argument('--circuit', '-c', choices=config.CIRCUITS.keys(), default=config.DEFAULT_CIRCUIT,
                        help=f'Circuito a usar (padrão: {config.DEFAULT_CIRCUIT})')
    
    parser.add_argument('--speed', '-s', type=int, default=config.DEFAULT_SPEED,
                        help=f'Velocidade em km/h (padrão: {config.DEFAULT_SPEED})')
    
    parser.add_argument('--laps', '-l', type=int, default=config.DEFAULT_LAPS,
                        help=f'Número de voltas (padrão: {config.DEFAULT_LAPS})')
    
    parser.add_argument('--repetitions', '-r', type=int, default=1,
                        help='Número de vezes para repetir a simulação (padrão: 1)')
    
    parser.add_argument('--report', action='store_true',
                        help='Gerar relatório PDF após simulação')
    
    parser.add_argument('--traffic', action='store_true',
                        help='Habilitar tráfego na simulação')
    
    parser.add_argument('--container', action='store_true',
                        help='Usar container Docker do BeamNG')
    
    parser.add_argument('--model', '-m', choices=config.VEHICLE_MODELS.keys(), default=config.DEFAULT_MODEL,
                        help=f'Modelo do veículo (padrão: {config.DEFAULT_MODEL})')
    
    args = parser.parse_args()
    
    success = run_simulation(
        circuit=args.circuit,
        speed=args.speed,
        laps=args.laps,
        use_container=args.container,
        enable_report=args.report,
        enable_traffic=args.traffic,
        vehicle_model=args.model,
        repetitions=args.repetitions
    )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
