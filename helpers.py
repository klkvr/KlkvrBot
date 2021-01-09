import os
os.chdir('/home/ubuntu/klkvrbot')

from config import *
import time
from datetime import datetime
import requests
import hcloud

def turn_off_bulbs():
    room_bulb1.turn_off()
    room_bulb2.turn_off()
    room_bulb3.turn_off()
def turn_on_bulbs():
    room_bulb1.turn_on()
    room_bulb2.turn_on()
    room_bulb3.turn_on()

def bulbs_set_brightness(b=100):
    room_bulb1.set_brightness(b)
    room_bulb2.set_brightness(b)
    room_bulb3.set_brightness(b)

def bulbs_set_color_temp(b=4500):
    room_bulb1.set_color_temp(b)
    room_bulb2.set_color_temp(b)
    room_bulb3.set_color_temp(b)

def get_normal_rgb(shit):
    binary = '{0:024b}'.format(shit)
    binr = binary[:8]
    bing = binary[8:16]
    binb = binary[16:24]
    r = int(binr, 2)
    g = int(bing, 2)
    b = int(binb, 2)
    return [r, g, b]

def get_room_data():
    room_bulb1_data = room_bulb1.get_properties()
    room_bulb2_data = room_bulb2.get_properties()
    room_bulb3_data = room_bulb3.get_properties()
    brightness = max(int(room_bulb1_data['bright']), int(room_bulb2_data['bright']), int(room_bulb3_data['bright']))
    color_temp = max(int(room_bulb1_data['ct']), int(room_bulb2_data['ct']), int(room_bulb3_data['ct']))
    power = 'on'
    if not room_bulb1_data['power'] == room_bulb2_data['power'] == room_bulb3_data['power'] == 'off':
        bulbs_set_brightness(brightness)
    if room_bulb1_data['power'] == room_bulb2_data['power'] == room_bulb3_data['power'] == 'off':
        power = 'off'
        brightness = 0
    return {'power': power, 'brightness': brightness, 'color_temp': color_temp}

def get_stripe_data():
    room_stripe_data = room_stripe.get_properties()
    power = room_stripe_data['power']
    color = get_normal_rgb(int(room_stripe_data['rgb']))
    return {'power': power, 'color': color, 'brightness': int(room_stripe_data['bright'])}

def get_sunset():
    url_format = 'https://voshod-solnca.ru/ajax/sun.php?lat=59.833494&lon=30.355353&bdate={date}&timezone=Europe%2FMoscow' 
    date = datetime.now().strftime('%d.%m.%Y')
    data = requests.get(url_format.format(date=date)).json()
    sunset_time = data[0]['sunset_unix'] // 1000
    return sunset_time

def start_vpn_server():
    try:
        client = hcloud.Client(HETZNER_APIKEY)
        client.servers.get_by_id(VPN_SERVER_ID).power_on()
        return True
    except:
        return False

def stop_vpn_server():
    try:
        client = hcloud.Client(HETZNER_APIKEY)
        client.servers.get_by_id(VPN_SERVER_ID).shutdown()
        return True
    except:
        return False

def get_vpn_server_state():
    try:
        client = hcloud.Client(HETZNER_APIKEY)
        return client.servers.get_by_id(VPN_SERVER_ID).status
    except:
        return False
