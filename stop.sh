#!/bin/bash

SCRIPT_NAME="cansim.py"

# Busca o PID do processo Python
PID=$(ps aux | grep "python $SCRIPT_NAME" | grep -v grep | awk '{print $2}')

# Verifica se encontrou o processo
if [ -z "$PID" ]; then
    echo "Erro: Processo 'python $SCRIPT_NAME' não encontrado."
    exit 1
fi

echo "Processo encontrado:"
ps aux | grep "python $SCRIPT_NAME" | grep -v grep

echo -e "\nEnviando sinal SIGINT (Ctrl+C) para PID: $PID"
kill -INT $PID

# Verifica se o comando foi executado com sucesso
if [ $? -eq 0 ]; then
    echo "Sinal SIGINT enviado com sucesso!"
else
    echo "Erro ao enviar sinal para o processo."
    exit 1
fi