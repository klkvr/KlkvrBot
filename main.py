import os
os.chdir('/home/ubuntu/klkvrbot')

from aiogram import Bot, Dispatcher, executor, types
from aiogram.utils import exceptions, executor
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.dispatcher.handler import CancelHandler, current_handler
from config import *
from helpers import *
from templates import *


class ShitMiddleware(BaseMiddleware):
    def __init__(self):
        super(ShitMiddleware, self).__init__()
    async def on_process_message(self, message, data):
        handler = current_handler.get()
        print('new_message', message.message_id)
        data["test_user"] = message.from_user.id


bot = Bot(BOT_HASH)
dp = Dispatcher(bot)
async def lights_info(user_id, message_id, edit=0):
    room_data = get_room_data()
    stripe_data = get_stripe_data()
    color_name = 'Неизвестный'
    for color in COLORS:
        if stripe_data['color'] == color['rgb']:
            color_name = color['name']
    msg = '<b>Инфа по освещению:</b>\n\n<b>Свет в комнате:</b> '
    if room_data['power'] == 'on':
        msg += f"включен, яркость {room_data['brightness']}%, температура {room_data['color_temp']}"
    else:
        msg += 'выключен'
    msg += '\n\n<b>Светодиодная лента:</b> '
    if stripe_data['power'] == 'on':
        msg += f"включена, яркость {stripe_data['brightness']}%, цвет {color_name}"
    else:
        msg += 'выключена'
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton(text='Управление светом', callback_data='ignore'))
    kb.add(*[types.InlineKeyboardButton(text=i[0], callback_data=i[1]) for i in [['вкл', 'turn_on_room'], ['выкл', 'turn_off_room']]])
    kb.add(*[types.InlineKeyboardButton(text=i[0], callback_data=i[1]) for i in [['вкл 50%', 'bulbs_bright:50'], ['вкл 100%', 'bulbs_bright:100']]])
    kb.add(*[types.InlineKeyboardButton(text=i[0], callback_data=i[1]) for i in [['ночной свет', 'bulbs_ct:1700'], ['дневной свет', 'bulbs_ct:4000']]])
    kb.add(types.InlineKeyboardButton(text='Управление лентой', callback_data='ignore'))
    kb.add(*[types.InlineKeyboardButton(text=i['text'], callback_data=i['callback']) for i in [{'text': 'вкл', 'callback': 'turn_on_stripe'}, {'text': 'выкл', 'callback': 'turn_off_stripe'}]])
    kb.add(*[types.InlineKeyboardButton(text=i['text'], callback_data=i['callback']) for i in [{'text': 'вкл 50%', 'callback': 'stripe_bright:50'}, {'text': 'вкл 100%', 'callback': 'stripe_bright:100'}]])
    kb.add(*[types.InlineKeyboardButton(text=i['emoji'], callback_data='stripe_rgb:' + str(i['rgb'][0]) + ':' + str(i['rgb'][1]) + ':' + str(i['rgb'][2])) for i in COLORS[:3]])
    kb.add(*[types.InlineKeyboardButton(text=i['emoji'], callback_data='stripe_rgb:' + str(i['rgb'][0]) + ':' + str(i['rgb'][1]) + ':' + str(i['rgb'][2])) for i in COLORS[3:]])
    if not edit:
        await bot.send_message(user_id, msg, reply_markup=kb, parse_mode="HTML")
    else:
        await bot.edit_message_text(chat_id=user_id, message_id=message_id, text=msg, reply_markup=kb, parse_mode="HTML")

async def send_servers(user_id, message_id=-1, edit=0):
    if not edit:
        await bot.send_message(user_id, choose_server, reply_markup=servers_kb)
    else:
        await bot.edit_message_text(chat_id=user_id, message_id=message_id, text= choose_server, reply_markup=servers_kb)

async def send_vpn(user_id, message_id=-1, edit=0):
    msg = f'Статус сервера: {get_vpn_server_state()}'
    kb = types.InlineKeyboardMarkup()
    kb.add(*[types.InlineKeyboardButton(text='Включить', callback_data='start_vpn_server'), types.InlineKeyboardButton(text='Выключить', callback_data='stop_vpn_server')])
    if not edit:
        await bot.send_message(user_id, msg, reply_markup=kb)
    else:
        await bot.edit_message_text(chat_id=user_id, message_id=message_id, text=msg, reply_markup=kb)


@dp.message_handler(commands=['start'])
async def start(message):
    user_id = message.chat.id 
    await bot.send_message(user_id, 'че тут писать', reply_markup=MAIN_BUTTONS)

@dp.message_handler(content_types=['text'])
async def text(message: types.Message, test_user):
    try:
        print(test_user)
        user_id = message.chat.id
        if user_id in ADMINS:
            message_id = message.message_id
            text = message.text
            if text == 'Освещение':
                await lights_info(user_id, message_id)
            elif text == 'Сервера':
                await send_servers(user_id)
            elif text == 'VPN':
                await send_vpn(user_id)
    except:
        print('error')


@dp.callback_query_handler()
async def inline(query):
    try:
        user_id = query.from_user.id
        if user_id in ADMINS:
            data = query.data
            message_id = query.message.message_id
            if data == 'turn_on_room':
                turn_on_bulbs()
                await lights_info(user_id, message_id, 1)
            elif data == 'turn_off_room':
                turn_off_bulbs()
                await lights_info(user_id, message_id, 1)
            elif data == 'turn_on_stripe':
                room_stripe.turn_on()
                await lights_info(user_id, message_id, 1)
            elif data == 'turn_off_stripe':
                room_stripe.turn_off()
                await lights_info(user_id, message_id, 1)
            elif 'bulbs_bright' in data:
                bulbs_set_brightness(int(data.split(':')[1]))
                await lights_info(user_id, message_id, 1)
            elif 'bulbs_ct:' in data:
                bulbs_set_color_temp(int(data.split(':')[1]))
                await lights_info(user_id, message_id, 1)
            elif 'stripe_bright' in data:
                room_stripe.set_brightness(int(data.split(':')[1]))
                await lights_info(user_id, message_id, 1)
            elif 'stripe_rgb' in data:
                rgb = [int(i) for i in data.split(':')[1:]]
                room_stripe.set_rgb(rgb[0], rgb[1], rgb[2])
                await lights_info(user_id, message_id, 1)
            elif 'show_server:' in data:
                server_id = int(data.split(':')[1])
                server = SERVERS[server_id]
                msg = f'<b>IP: </b><i>{server["ip"]}</i>\n\n<b>Password: </b><i>{server["password"]}</i>'
                kb = types.InlineKeyboardMarkup()
                kb.add(types.InlineKeyboardButton(text="Назад", callback_data="servers"))
                await bot.edit_message_text(chat_id=user_id, message_id=message_id, text=msg, reply_markup=kb, parse_mode="HTML")
            elif data == "servers":
                await send_servers(user_id, message_id, 1)
            elif data == 'start_vpn_server':
                start_vpn_server()
                time.sleep(2)
                await end_vpn(user_id, message_id, 1)
            elif data == 'stop_vpn_server':
                stop_vpn_server()
                time.sleep(2)
                await send_vpn(user_id, message_id, 1)
    except:
        print('error')

@dp.message_handler(commands=['on'])
async def on(message):
    user_id = message.chat.id
    if user_id in ADMINS:
        turn_on_bulbs()

        
@dp.message_handler(commands=['off']) 
async def off(message):
    user_id = message.chat.id
    if user_id in ADMINS:
        turn_off_bulbs()

if __name__ == '__main__':
    dp.middleware.setup(ShitMiddleware())
    executor.start_polling(dp, skip_updates=False)