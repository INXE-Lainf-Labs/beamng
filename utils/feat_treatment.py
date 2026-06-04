"""Treatment functions for sensor data to match DBC format"""

def ratio_to_256(value):
    return value * 255

def ratio_to_100(value):
    return value * 100

def get_vel(vel_tuple):
    """Convert velocity vector to magnitude (km/h)"""
    speed_m_s = (vel_tuple[0]**2 + vel_tuple[1]**2 + vel_tuple[2]**2)**0.5
    return speed_m_s * 3.6