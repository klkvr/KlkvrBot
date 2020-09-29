import os
os.chdir('/home/ubuntu/klkvrbot')

from config import *
from helpers import *
import time

sunset_time = get_sunset()
current_time = int(time.time())
time_100 = sunset_time - 15 * 60
time_0 = time_100 - 33 * 60
if time_0+5*60 >= current_time >= time_0:
    turn_on_bulbs()        
