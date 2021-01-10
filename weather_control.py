import os
os.chdir('/home/ubuntu/klkvrbot')

from config import *
from helpers import *
import time
from datetime import datetime

sunset_time = get_sunset()
current_time = int(time.time())
current_date = datetime.fromtimestamp(current_time)
bulbs_data = get_room_data()
print(bulbs_data)
if bulbs_data['power'] == 'on':
    if [current_date.hour, current_date.minute] == [0, 0]:
        bulbs_set_color_temp(1700)
    elif current_date.hour >= 8:
        bulbs_set_color_temp(4000)
time_100 = sunset_time - 15 * 60
time_0 = time_100 - 33 * 60
if time_0+5*60 >= current_time >= time_0:
    turn_on_bulbs()        
