import cantools
from time import time

class CANParser:

    # Inicializa a classe tendo como argumento o arquivo DBC
    def __init__(self, dbc):
        """
        Classe utilitária para codificação CAN
        Args:
            dbc: caminho para o arquivo dbc
        """
        self.db = cantools.database.load_file(dbc)

    # Codifica e formata a mensagem CAN
    def insert_pid(self, raw_message, pid, signal):

        pid = str(pid)[2:]
        pid = '0' * (4 - len(pid)) + pid

        # Verifica quantos bytes ocupam o sinal
        start = signal.start / 8
        length = signal.length / 8
        start_a = start + length

        msg_bytes = raw_message.split(' ')
        msg_bytes[2], msg_bytes[3] = pid[:2], pid[2:]
        msg_bytes[1] = '62'
        
        # Preenche com o checksum para todos os bytes não utilizados
        for i in range(int(start_a), 8):
            msg_bytes[i] = 'AA'
        
        # Conta o payload válido
        msg_bytes[0] = '0' + str(sum(1 for x in msg_bytes[1:] if x != 'AA'))
        
        return ' '.join(msg_bytes).upper()
    
    def encode(self, msg, value):

        """
        Retorna um payload CAN
        Args:
            msg: ID da mensagem
            value: valor da mensagem
        """

        # Pega o nome da mensagem
        message = self.db.get_message_by_name(msg)
        
        # Pega o PID
        pid = hex(message.frame_id)

        signal = message.signals[0]
        info = {signal.name: value}

        raw_message = str(message.encode(info).hex(' '))

        formatted = self.insert_pid(raw_message, pid, signal)
        
        return formatted, message.senders[0][1:]

    # Função que converte para formato de log CAN
    def log(self, msg, value):

        """
        Função que retorna uma string formatada para um log CAN
        Args:
            msg: mensagem a ser codificada
            value: valor a ser transposto
        """

        payload, ecu = self.encode(msg, value)

        timestamp = time()

        log_message = f'({timestamp:.6f})  can0  {ecu}   [8]  {payload}'

        return log_message

    def decode_log_line(self, log_msg):

        """
        Função que recebe uma string de um frame CAN, formatado pela função log,
        e decodifica o valor para o seu formato original

        Args:
            log_msg: mensagem no formato CAN log
        """

        log_msg = log_msg.split()
        
        pid = int(''.join(log_msg[6:8]), 16)
        
        payload = ''.join(log_msg[4:])

        payload = bytes.fromhex(payload)

        msg = self.db.get_message_by_frame_id(pid)

        return msg.decode(payload)