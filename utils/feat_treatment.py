"""
Módulo que define os tratamentos que podem ser necessários 
para os dados do bng serem compatíveis com os dbc 
"""

def times_1(value):
    return value * 1

def ratio_to_256(value):
    return value * 255

def ratio_to_100(value):
    return value * 100

def ms_to_kh(value):
    return value * 3.6

def get_vel(vel_tuple):
    """
    Recebe as velocidades vetoriais e retorna a velocidade representada no velocímetro
    """
    speed_m_s = (vel_tuple[0]**2 + vel_tuple[1]**2 + vel_tuple[2]**2)**0.5
    speed_km_h = speed_m_s * 3.6
    return speed_km_h