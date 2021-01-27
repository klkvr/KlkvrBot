import os
os.chdir('/home/ubuntu/klkvrbot')

from aiogram import types
from config import *
MAIN_BUTTONS = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
MAIN_BUTTONS.add(*['Освещение', 'Сервера', 'VPN'])
choose_server = 'Выбери сервер для просмотра данных'
servers_kb = types.InlineKeyboardMarkup()
for i in range(len(SERVERS)):
    servers_kb.add(types.InlineKeyboardButton(text=SERVERS[i]['name'], callback_data=f'show_server:{i}'))