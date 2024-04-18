from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import json


def Main(lang):
    keyboard = VkKeyboard(one_time=False)
    keyboard.add_callback_button(lang.indexes, color=VkKeyboardColor.PRIMARY, payload={"type": "Индексы"})
    keyboard.add_callback_button(lang.market, color=VkKeyboardColor.PRIMARY, payload={"type": "Рынок"})
    keyboard.add_line()
    keyboard.add_callback_button(lang.farm, color=VkKeyboardColor.PRIMARY, payload={"type": "Фарм"})
    keyboard.add_callback_button(lang.wars, color=VkKeyboardColor.PRIMARY, payload={"type": "Войны"})
    keyboard.add_line()
    keyboard.add_callback_button(lang.help, color=VkKeyboardColor.PRIMARY, payload={"type": "Помощь"})
    keyboard.add_callback_button('WP', color=VkKeyboardColor.PRIMARY, payload={"type": "WP"})
    return keyboard.get_keyboard()


def Prices(lang):
    keyboard = VkKeyboard(one_time=False)
    keyboard.add_callback_button(lang.prices, color=VkKeyboardColor.PRIMARY, payload={"type": "Рыночек"})
    keyboard.add_callback_button(lang.state, color=VkKeyboardColor.PRIMARY, payload={"type": "ГосЦены"})
    keyboard.add_line()
    keyboard.add_callback_button(lang.back, color=VkKeyboardColor.PRIMARY, payload={"type": "Назад"})
    return keyboard.get_keyboard()


def privateMarket(lang):
    keyboard = VkKeyboard(one_time=False)
    keyboard.add_callback_button(lang.resources, color=VkKeyboardColor.PRIMARY, payload={"type": "Ресурсы"})
    keyboard.add_callback_button(lang.weapons, color=VkKeyboardColor.PRIMARY, payload={"type": "Оружие"})
    keyboard.add_line()
    keyboard.add_callback_button(lang.back, color=VkKeyboardColor.PRIMARY, payload={"type": "Назад"})
    return keyboard.get_keyboard()


def Indexes(lang):
    keyboard = VkKeyboard(one_time=False)
    keyboard.add_callback_button(lang.homes, color=VkKeyboardColor.PRIMARY, payload={"type": "ЖФ"})
    keyboard.add_callback_button(lang.medicine, color=VkKeyboardColor.PRIMARY, payload={"type": "Медка"})
    keyboard.add_line()
    keyboard.add_callback_button(lang.military, color=VkKeyboardColor.PRIMARY, payload={"type": "Военка"})
    keyboard.add_callback_button(lang.school, color=VkKeyboardColor.PRIMARY, payload={"type": "Школа"})
    keyboard.add_line()
    keyboard.add_callback_button(lang.table, color=VkKeyboardColor.PRIMARY, payload={"type": "Таблица"})
    keyboard.add_line()
    keyboard.add_callback_button(lang.back, color=VkKeyboardColor.PRIMARY, payload={"type": "Назад"})
    return keyboard.get_keyboard()


def Governor(lang):
    keyboard = VkKeyboard(one_time=False)
    keyboard.add_callback_button(lang.indexes, color=VkKeyboardColor.PRIMARY, payload={"type": "Индексы"})
    keyboard.add_callback_button(lang.market, color=VkKeyboardColor.PRIMARY, payload={"type": "Рынок"})
    keyboard.add_line()
    keyboard.add_callback_button(lang.farm, color=VkKeyboardColor.PRIMARY, payload={"type": "Фарм"})
    keyboard.add_callback_button(lang.wars, color=VkKeyboardColor.PRIMARY, payload={"type": "Войны"})
    keyboard.add_line()
    keyboard.add_callback_button(lang.info, color=VkKeyboardColor.PRIMARY, payload={"type": "Инфа"})
    keyboard.add_line()
    keyboard.add_callback_button(lang.help, color=VkKeyboardColor.PRIMARY, payload={"type": "Помощь"})
    keyboard.add_callback_button('WP', color=VkKeyboardColor.PRIMARY, payload={"type": "WP"})
    return keyboard.get_keyboard()


def Empty():
    return json.dumps({'one_time': False, 'buttons': []})


def Info(reg_id):
    keyboard = VkKeyboard(inline=True)
    keyboard.add_callback_button('Раскрыть', color=VkKeyboardColor.PRIMARY, payload={"type":  int(reg_id)})
    return keyboard.get_keyboard()


def Hide(reg_id):
    keyboard = VkKeyboard(inline=True)
    keyboard.add_callback_button('Скрыть', color=VkKeyboardColor.PRIMARY, payload={"type": -int(reg_id)})
    return keyboard.get_keyboard()


def chooseLanguage(source):
    if source == 'vk':
        keyboard = VkKeyboard(inline=True)
        keyboard.add_callback_button('Ru', color=VkKeyboardColor.PRIMARY, payload={'type': 'ru'})
        keyboard.add_callback_button('En', color=VkKeyboardColor.PRIMARY, payload={'type': 'en'})
        return keyboard.get_keyboard()


def Wp():
    keyboard = VkKeyboard(one_time=False)
    keyboard.add_callback_button('Цены', color=VkKeyboardColor.PRIMARY, payload={"type": "WpЦены"})
    keyboard.add_line()
    keyboard.add_callback_button('RR', color=VkKeyboardColor.PRIMARY, payload={"type": "RR"})
    return keyboard.get_keyboard()


def Marriage():
    keyboard = VkKeyboard(inline=True)
    keyboard.add_callback_button('Да', color=VkKeyboardColor.PRIMARY, payload={'type': 'yes'})
    keyboard.add_callback_button('Нет', color=VkKeyboardColor.PRIMARY, payload={'type': 'no'})
    return keyboard.get_keyboard()


