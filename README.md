# BeamNG Simulation - INMETRO

Simulação veicular no BeamNG com coleta de dados CAN e geração de vídeos/relatórios.

## Uso Rápido

```bash
# Simulação básica (circuito c1, velocidade 12 km/h)
python simulate.py

# Com parâmetros customizados
python simulate.py --circuit c1 --speed 15 --laps 2 --report

# Múltiplas repetições
python simulate.py --circuit c3 --repetitions 5

# Com tráfego habilitado
python simulate.py --circuit c2 --traffic --report

# Com container Docker
python simulate.py --circuit c4 --container --report
```

## Circuitos Disponíveis

- **c1**: Circuito ao redor dos prédios (13 waypoints)
- **c2**: Subindo e descendo o prédio 20 (34 waypoints)
- **c3**: DIMCI até a rotatória (7 waypoints)
- **c4**: DIMCI até rotatória com caminho inverso (14 waypoints)

## Argumentos CLI

```
--circuit, -c     Circuito a usar (padrão: c1) [c1, c2, c3, c4]
--speed, -s       Velocidade em km/h (padrão: 12)
--laps, -l        Número de voltas (padrão: 1)
--repetitions, -r Repetir simulação N vezes (padrão: 1)
--report          Gerar relatório PDF após simulação
--traffic         Habilitar tráfego na simulação
--container       Usar container Docker do BeamNG
--model, -m       Modelo do veículo [hb20, sbr] (padrão: hb20)
```

## Batch Testing

```bash
# Executar 10 simulações com parâmetros padrão
python runTests.py
```

## Saídas

Cada simulação gera:
```
./data/s_YYYYMMDD_HHMM/
├── readable.csv        # Dados coletados (CSV)
├── can.log            # Log CAN formatado
├── can_debug.log      # Debug de cada ponto CAN
├── recording.mp4      # Vídeo da simulação
└── report.pdf         # Relatório (se --report)
```

## Configuração

Customizar parâmetros em `config.py`:
- Circuitos e waypoints
- Host/porta BeamNG
- Configurações de câmera
- Sensores e tratamentos de dados
- Parâmetros de tráfego

## Arquivos Principais

- **simulate.py** - Entry point único parametrizado
- **config.py** - Todas as constantes e configurações
- **utils/sim_sup.py** - Lógica core de simulação
- **utils/feat_treatment.py** - Tratamento de dados de sensores
- **utils/can_parser.py** - Codificação/decodificação CAN
- **utils/camera_utils.py** - Geração de vídeos
- **utils/reports.py** - Geração de relatórios PDF
