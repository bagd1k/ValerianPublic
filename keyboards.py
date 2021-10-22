from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from telebot import types
import json


def Main():
    keyboard = VkKeyboard(one_time=False)
    keyboard.add_callback_button('Индексы', color=VkKeyboardColor.PRIMARY, payload={"type": "Индексы"})
    keyboard.add_callback_button('Рынок', color=VkKeyboardColor.PRIMARY, payload={"type": "Рынок"})
    keyboard.add_line()
    keyboard.add_callback_button('Фарм', color=VkKeyboardColor.PRIMARY, payload={"type": "Фарм"})
    keyboard.add_callback_button('Войны', color=VkKeyboardColor.PRIMARY, payload={"type": "Войны"})
    keyboard.add_line()
    keyboard.add_callback_button('Помощь', color=VkKeyboardColor.PRIMARY, payload={"type": "Помощь"})
    return keyboard.get_keyboard()


def Prices():
    keyboard = VkKeyboard(one_time=False)
    keyboard.add_callback_button('Цены', color=VkKeyboardColor.PRIMARY, payload={"type": "Цены"})
    keyboard.add_callback_button('Гос', color=VkKeyboardColor.PRIMARY, payload={"type": "Гос"})
    keyboard.add_line()
    keyboard.add_callback_button('Назад', color=VkKeyboardColor.PRIMARY, payload={"type": "Назад"})
    return keyboard.get_keyboard()


def Indexes():
    keyboard = VkKeyboard(one_time=False)
    keyboard.add_callback_button('ЖФ', color=VkKeyboardColor.PRIMARY, payload={"type": "ЖФ"})
    keyboard.add_callback_button('Медка', color=VkKeyboardColor.PRIMARY, payload={"type": "Медка"})
    keyboard.add_line()
    keyboard.add_callback_button('Военка', color=VkKeyboardColor.PRIMARY, payload={"type": "Военка"})
    keyboard.add_callback_button('Школа', color=VkKeyboardColor.PRIMARY, payload={"type": "Школа"})
    keyboard.add_line()
    keyboard.add_callback_button('Таблица', color=VkKeyboardColor.PRIMARY, payload={"type": "Таблица"})
    keyboard.add_line()
    keyboard.add_callback_button('Назад', color=VkKeyboardColor.PRIMARY, payload={"type": "Назад"})
    return keyboard.get_keyboard()


def Governor():
    keyboard = VkKeyboard(one_time=False)
    keyboard.add_callback_button('Индексы', color=VkKeyboardColor.PRIMARY, payload={"type": "Индексы"})
    keyboard.add_callback_button('Рынок', color=VkKeyboardColor.PRIMARY, payload={"type": "Рынок"})
    keyboard.add_line()
    keyboard.add_callback_button('Фарм', color=VkKeyboardColor.PRIMARY, payload={"type": "Фарм"})
    keyboard.add_callback_button('Войны', color=VkKeyboardColor.PRIMARY, payload={"type": "Войны"})
    keyboard.add_line()
    keyboard.add_callback_button('Инфа', color=VkKeyboardColor.PRIMARY, payload={"type": "Инфа"})
    keyboard.add_line()
    keyboard.add_callback_button('Помощь', color=VkKeyboardColor.PRIMARY, payload={"type": "Помощь"})
    return keyboard.get_keyboard()


def Empty():
    return json.dumps({'one_time': False, 'buttons': []})


def Inline(user_id, source):
    if source == 'vk':
        keyboard = VkKeyboard(inline=True)
        keyboard.add_button('Сила', color=VkKeyboardColor.PRIMARY, payload="{\"" + user_id + "\":\"1\"}")
        keyboard.add_button('Знания', color=VkKeyboardColor.PRIMARY, payload="{\"" + user_id + "\":\"2\"}")
        keyboard.add_button('Вынка', color=VkKeyboardColor.PRIMARY, payload="{\"" + user_id + "\":\"3\"}")
        keyboard.add_line()
        keyboard.add_button('Сила R', color=VkKeyboardColor.PRIMARY, payload="{\"" + user_id + "\":\"4\"}")
        keyboard.add_button('Знания R', color=VkKeyboardColor.PRIMARY, payload="{\"" + user_id + "\":\"5\"}")
        keyboard.add_button('Вынка R', color=VkKeyboardColor.PRIMARY, payload="{\"" + user_id + "\":\"6\"}")
        keyboard.add_line()
        keyboard.add_button('Копка', color=VkKeyboardColor.PRIMARY, payload="{\"" + user_id + "\":\"0\"}")
        keyboard.add_button('Скинуть', color=VkKeyboardColor.PRIMARY, payload="{\"" + user_id + "\":\"9\"}")
        keyboard.add_button('Авто', color=VkKeyboardColor.PRIMARY, payload="{\"" + user_id + "\":\"8\"}")
        return keyboard.get_keyboard()
    elif source == 'tg':
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(text='Сила', callback_data="{\"" + user_id + "\":\"1\"}"),
                     types.InlineKeyboardButton(text='Знания', callback_data="{\"" + user_id + "\":\"2\"}"),
                     types.InlineKeyboardButton(text='Вынка', callback_data="{\"" + user_id + "\":\"3\"}"),
                     types.InlineKeyboardButton(text='Вынка R', callback_data="{\"" + user_id + "\":\"6\"}"),)
        return keyboard


def getTime():
    keyboard = VkKeyboard(inline=True)
    keyboard.add_callback_button('Да', color=VkKeyboardColor.PRIMARY, payload={'type': '1488'})
    return keyboard.get_keyboard()


def Info(reg_id):
    keyboard = VkKeyboard(inline=True)
    keyboard.add_callback_button('Раскрыть', color=VkKeyboardColor.PRIMARY, payload={"type":  int(reg_id)})
    return keyboard.get_keyboard()


def Hide(reg_id):
    keyboard = VkKeyboard(inline=True)
    keyboard.add_callback_button('Скрыть', color=VkKeyboardColor.PRIMARY, payload={"type": -int(reg_id)})
    return keyboard.get_keyboard()


def anotherAcc():
    keyboard = VkKeyboard(inline=True)
    keyboard.add_callback_button('Другой акк', color=VkKeyboardColor.PRIMARY, payload={'type': '1488'})
    return keyboard.get_keyboard()
