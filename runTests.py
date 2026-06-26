#!/usr/bin/env python3
"""Run multiple simulations with standard parameters"""

import subprocess
from sys import executable

# Parâmetros para executar simulações
n_repetitions = 10
circuit = "c1"
speed = 12
laps = 1

print(f"Executando {n_repetitions} simulações no circuito {circuit}")

for i in range(n_repetitions):
    print(f"\n{'='*60}")
    print(f"Rodada {i+1}/{n_repetitions}")
    print(f"{'='*60}")
    subprocess.run([executable, "simulate.py", "-c", circuit, "-s", str(speed), "-l", str(laps)])

print(f"\n{'='*60}")
print("Todos os testes foram concluídos!")
print(f"{'='*60}")