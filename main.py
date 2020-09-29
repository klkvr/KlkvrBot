import os
os.chdir('/home/ubuntu/klkvrbot')

import telebot
from telebot import types
from config import *
from helpers import *
from templates import *


bot = telebot.TeleBot(BOT_HASH)

def lights_info(user_id, message_id, edit=0):
    room_data = get_room_data()
    stripe_data = get_stripe_data()
    color_name = 'Неизвестный'
    for color in COLORS:
        if stripe_data['color'] == color['rgb']:
            color_name = color['name']
    msg = '<b>Инфа по освещению:</b>\n\n<b>Свет в комнате:</b> '
    if room_data['power'] == 'on':
        msg += 'включен, яркость ' + str(room_data['brightness']) + '%'
    else:
        msg += 'выключен'
    msg += '\n\n<b>Светодиодная лента:</b> '
    if stripe_data['power'] == 'on':
        msg += 'включена, яркость ' + str(stripe_data['brightness']) + '%, цвет ' + color_name
    else:
        msg += 'выключена'
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton(text='Управление светом', callback_data='ignore'))
    kb.add(*[types.InlineKeyboardButton(text=i['text'], callback_data=i['callback']) for i in [{'text': 'вкл', 'callback': 'turn_on_room'}, {'text': 'выкл', 'callback': 'turn_off_room'}]])
    kb.add(*[types.InlineKeyboardButton(text=i['text'], callback_data=i['callback']) for i in [{'text': 'вкл 50%', 'callback': 'bulbs_bright:50'}, {'text': 'вкл 100%', 'callback': 'bulbs_bright:100'}]])
    kb.add(types.InlineKeyboardButton(text='Управление лентой', callback_data='ignore'))
    kb.add(*[types.InlineKeyboardButton(text=i['text'], callback_data=i['callback']) for i in [{'text': 'вкл', 'callback': 'turn_on_stripe'}, {'text': 'выкл', 'callback': 'turn_off_stripe'}]])
    kb.add(*[types.InlineKeyboardButton(text=i['text'], callback_data=i['callback']) for i in [{'text': 'вкл 50%', 'callback': 'stripe_bright:50'}, {'text': 'вкл 100%', 'callback': 'stripe_bright:100'}]])
    kb.add(*[types.InlineKeyboardButton(text=i['emoji'], callback_data='stripe_rgb:' + str(i['rgb'][0]) + ':' + str(i['rgb'][1]) + ':' + str(i['rgb'][2])) for i in COLORS[:3]])
    kb.add(*[types.InlineKeyboardButton(text=i['emoji'], callback_data='stripe_rgb:' + str(i['rgb'][0]) + ':' + str(i['rgb'][1]) + ':' + str(i['rgb'][2])) for i in COLORS[3:]])
    if not edit:
        bot.send_message(user_id, msg, reply_markup=kb, parse_mode="HTML")
    else:
        bot.edit_message_text(chat_id=user_id, message_id=message_id, text=msg, reply_markup=kb, parse_mode="HTML")

def send_servers(user_id, message_id=-1, edit=0):
    if not edit:
        bot.send_message(user_id, choose_server, reply_markup=servers_kb)
    else:
        bot.edit_message_text(chat_id=user_id, message_id=message_id, text= choose_server, reply_markup=servers_kb)

def send_vpn(user_id, message_id=-1, edit=0):
    msg = f'Статус сервера: {get_vpn_instance_state()}'
    kb = types.InlineKeyboardMarkup()
    kb.add(*[types.InlineKeyboardButton(text='Включить', callback_data='start_vpn_instance'), types.InlineKeyboardButton(text='Выключить', callback_data='stop_vpn_instance')])
    if not edit:
        bot.send_message(user_id, msg, reply_markup=kb)
    else:
        bot.edit_message_text(chat_id=user_id, message_id=message_id, text=msg, reply_markup=kb)


@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id 
    bot.send_message(user_id, 'че тут писать', reply_markup=MAIN_BUTTONS)

@bot.message_handler(content_types=['text'])
def text(message):
    try:
        user_id = message.chat.id
        if user_id in ADMINS:
            message_id = message.message_id
            text = message.text
            if text == 'Освещение':
                lights_info(user_id, message_id)
            elif text == 'Сервера':
                send_servers(user_id)
            elif text == 'VPN':
                send_vpn(user_id)
    except:
        print('error')


@bot.callback_query_handler(func=lambda call: True)
def inline(query):
    try:
        user_id = query.from_user.id
        if user_id in ADMINS:
            data = query.data
            message_id = query.message.message_id
            if data == 'turn_on_room':
                turn_on_bulbs()
                lights_info(user_id, message_id, 1)
            elif data == 'turn_off_room':
                turn_off_bulbs()
                lights_info(user_id, message_id, 1)
            elif data == 'turn_on_stripe':
                room_stripe.turn_on()
                lights_info(user_id, message_id, 1)
            elif data == 'turn_off_stripe':
                room_stripe.turn_off()
                lights_info(user_id, message_id, 1)
            elif 'bulbs_bright' in data:
                bulbs_set_brightness(int(data.split(':')[1]))
                lights_info(user_id, message_id, 1)
            elif 'stripe_bright' in data:
                room_stripe.set_brightness(int(data.split(':')[1]))
                lights_info(user_id, message_id, 1)
            elif 'stripe_rgb' in data:
                rgb = [int(i) for i in data.split(':')[1:]]
                room_stripe.set_rgb(rgb[0], rgb[1], rgb[2])
                lights_info(user_id, message_id, 1)
            elif 'show_server:' in data:
                server_id = int(data.split(':')[1])
                server = SERVERS[server_id]
                msg = f'<b>IP: </b><i>{server["ip"]}</i>\n\n<b>Password: </b><i>{server["password"]}</i>'
                kb = types.InlineKeyboardMarkup()
                kb.add(types.InlineKeyboardButton(text="Назад", callback_data="servers"))
                bot.edit_message_text(chat_id=user_id, message_id=message_id, text=msg, reply_markup=kb, parse_mode="HTML")
            elif data == "servers":
                send_servers(user_id, message_id, 1)
            elif data == 'start_vpn_instance':
                start_vpn_instance()
                time.sleep(2)
                send_vpn(user_id, message_id, 1)
            elif data == 'stop_vpn_instance':
                stop_vpn_instance()
                time.sleep(2)
                send_vpn(user_id, message_id, 1)
    except:
        print('error')

@bot.message_handler(commands=['on'])
def on(message):
    user_id = message.chat.id
    if user_id in ADMINS:
        print('here')
        turn_on_bulbs()

        
@bot.message_handler(commands=['off']) 
def off(message):
    user_id = message.chat.id
    print('here')
    if user_id in ADMINS:
        print('here')
        turn_off_bulbs()

        
bot.polling()
