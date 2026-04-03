import subprocess
from sys import executable

n = 10  # número de testes para cada variação

for i in range(n):
    print(f"Executando teste {i+1}/{n} para inmetroCircuit.py") 
    subprocess.run([executable, "inmetroCircuit.py"])

print("Todos os testes foram concluídos")