# -*- coding: utf-8 -*-
import json
import random
import re
import time
import hashlib
from typing import Dict, Any

import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.utils import get_random_id
from PIL import Image, ImageFont, ImageDraw

import db
import form
import rr
import keyboards
import dex
import locales
import wp

stats = {}
lastCalls: Dict[Any, Any] = {}
actions = {'обнять': 'acc', 'выебать': 'acc', 'изнасиловать': 'acc', 'делать секс': 'dat',
           'отдаться': 'dat', 'отсосать': 'dat', 'отлизать': 'dat', 'трахнуть': 'acc', 'мобилизовать': 'acc',
           'мобилизировать': 'acc'}
actionsMale = ['обнял', 'выебал', 'изнасиловал', 'сделал секс', 'отдался', 'отсосал', 'отлизал', 'трахнул',
               'мобилизовал', 'мобилизировал']
actionsFemale = ['обняла', 'выебала', 'изнасиловала', 'сделала секс', 'отдалась', 'отсосала', 'отлизала', 'трахнула',
                 'мобилизовала', 'мобилизировала']


class MyVkLongPoll(VkBotLongPoll):
    def listen(self):
        while True:
            try:
                for event in self.check():
                    yield event
            except Exception as e:
                print('error', e)


class Event(object):
    def __init__(self, source, text, from_id, peer_id, payload, attachments, message_id, event_id, reply_message,
                 fwd_messages, from_name, cmId, action):
        self.source = source
        self.text = text
        self.from_id = from_id
        self.peer_id = peer_id
        self.payload = payload
        self.attachments = attachments
        self.message_id = message_id
        self.event_id = event_id
        self.reply_message = reply_message
        self.fwd_messages = fwd_messages
        self.from_name = from_name
        self.cmId = cmId
        self.action = action


def formObject(source, event):
    if source == 'vk':
        if event.type == VkBotEventType.MESSAGE_NEW:
            event = event.object['message']
            text = event['text'] if event['text'] != '' else ' '
            from_id = event['from_id']
            peer_id = event['peer_id']
            cmId = event['conversation_message_id']
            if 'reply_message' in event:
                reply_message = event['reply_message']['from_id']
            else:
                reply_message = 0
            if event['fwd_messages']:
                fwd_messages = event['fwd_messages'][0]['from_id']
            else:
                fwd_messages = 0
            if 'payload' in event:
                payload = event['payload']['type']
            else:
                payload = 0
            if 'action' in event:
                action = event['action']['type']
            else:
                action = None
            attachments = event['attachments']
            message_id = event['conversation_message_id'] if 'conversation_message_id' in event else 0
            return Event(source, text, from_id, peer_id, payload, attachments, message_id, 0, reply_message,
                         fwd_messages,
                         getUserName(from_id), cmId, action)
        if event.type == VkBotEventType.MESSAGE_EVENT:
            text = ''
            event = event.object
            from_id = event['user_id']
            peer_id = event['peer_id']
            if 'payload' in event:
                payload = event['payload']['type']
            else:
                payload = 0
            event_id = event['event_id']
            message_id = event['conversation_message_id'] if 'conversation_message_id' in event else 0
            return Event(source, text, from_id, peer_id, payload, [], 0, event_id, 0, 0,
                         getUserName(from_id), message_id, 0)


def vkAuth(
        token=""):
    vk_session = vk_api.VkApi(token=token)
    return MyVkLongPoll(vk_session, group_id=1), vk_session.get_api()


longpoll, vk = vkAuth()


def send(event, text='', domain=1, attachment=None, kb=None, source='vk'):
    if source == 'vk':
        if event != 0 and event.from_id in lastCalls.keys() and time.time() - lastCalls[event.from_id] < 5:
            vk.messages.send(peer_id=event.peer_id, message='Подождите ещё немного', random_id=get_random_id(),
                             v='5.131', dont_parse_links=1)
        else:
            if isGovernor(str(domain)):
                if kb == keyboards.Main(locales.Russian):
                    kb = keyboards.Governor(locales.Russian)
                elif kb == keyboards.Main(locales.English):
                    kb = keyboards.Governor(locales.English)
            elif domain > 2e9:
                kb = keyboards.Empty()
            vk.messages.send(peer_id=int(domain), message=text, attachment=attachment,
                             random_id=get_random_id(), keyboard=kb, v='5.131', dont_parse_links=1)
            lastCalls.update({event.from_id: time.time()} if event != 0 else {0: 0})


def fetcher(event):
    original = event.text
    event.text = event.text.lower()
    if not db.isChatExists(event.peer_id) and event.peer_id > 2e9:
        db.addChat(event.peer_id)
    if event.peer_id > 2e9 and db.isMuted(event.from_id, event.peer_id) and \
            event.from_id not in getConvAdmins(event.peer_id):
        deleteMutedMessage(event.cmId, event.peer_id)
    if event.action == 'chat_invite_user' and db.getGreeting(event.peer_id):
        send(event, db.getGreeting(event.peer_id), event.peer_id)
    if event.reply_message or event.fwd_messages:
        if event.text in actions:
            if event.reply_message in [event.from_id, event.from_name] or \
                    event.fwd_messages in [event.from_id, event.from_name]:
                send(event, 'Найди уже себе партнёра...', event.peer_id, source=event.source)
                return 1
            numOfAction = list(actions.keys()).index(event.text)
            activeOne = getUserName(event.from_id, source=event.source) if event.source == 'vk' else event.from_name
            passiveOne = getUserName(event.reply_message, actions[event.text], source=event.source) \
                if event.reply_message else getUserName(event, event.fwd_messages, actions[event.text],
                                                        source=event.source)
            if getSex(event.from_id, event.source):
                send(event, f'{activeOne} {actionsMale[numOfAction]} {passiveOne}', event.peer_id, source=event.source)
            else:
                send(event, f'{activeOne} {actionsFemale[numOfAction]} {passiveOne}', event.peer_id,
                     source=event.source)
    if event.source == 'vk':
        if event.text.startswith(tuple(['!greeting', '!приветствие'])) and event.peer_id > 2e9 \
                and event.from_id in getConvAdmins(event.peer_id):
            db.setGreeting(event.peer_id, original.split(maxsplit=1)[1])
            send(event, 'Приветствие установлено!', event.peer_id)
        if event.text.startswith(tuple(['!kick', 'кик'])) and event.from_id \
                in getConvAdmins(event.peer_id) and event.peer_id > 2e9:
            if event.reply_message and event.reply_message not in getConvAdmins(event.peer_id):
                send(event, kick(event.peer_id, event.reply_message), event.peer_id)
            elif event.fwd_messages and event.fwd_messages not in getConvAdmins(event.peer_id):
                send(event, kick(event.peer_id, event.fwd_messages), event.peer_id)
            else:
                try:
                    if int(re.search("id(\\d+)", event.text).group(1)) not in getConvAdmins(event.peer_id):
                        send(event, kick(event.peer_id, re.search("id(\\d+)", event.text).group(1)), event.peer_id)
                except AttributeError:
                    pass
        if event.text.startswith(tuple(['!mute', 'мут'])) and event.from_id in \
                getConvAdmins(event.peer_id) and event.peer_id > 2e9:
            if event.reply_message and event.reply_message not in getConvAdmins(event.peer_id):
                response = db.muteUser(event.reply_message, event.peer_id)
                send(event, 'Пользователь замучен!' if response else 'Пользователь размучен!', event.peer_id)
            elif event.fwd_messages and event.fwd_messages not in getConvAdmins(event.peer_id):
                response = db.muteUser(event.fwd_messages, event.peer_id)
                send(event, 'Пользователь замучен!' if response else 'Пользователь размучен!', event.peer_id)
            else:
                try:
                    if int(re.search("id(\\d+)", event.text).group(1)) not in getConvAdmins(event.peer_id):
                        response = db.muteUser(int(re.search("id(\\d+)", event.text).group(1)), event.peer_id)
                        send(event, 'Пользователь замучен!' if response else 'Пользователь размучен!', event.peer_id)
                except AttributeError:
                    pass
        elif event.text.startswith("!create"):
            if len(event.text.split()) == 2:
                tag = event.text.split()[1].replace('!', '')
                if not db.isTagExists(tag):
                    accessCode = hashlib.md5(f'{event.from_id}{time.time()}huy'.encode()).hexdigest()[:8]
                    db.createMailing(event.from_id, accessCode, tag)
                    send(event, f'Рассылка с тэгом !{tag} создана! Код доступа:\n{accessCode}', event.from_id)
                else:
                    send(event, f'Тэг уже занят!', event.from_id)
            else:
                send(event, 'Не указан тег!', event.peer_id)
        elif event.text.startswith("!followers"):
            if len(event.text.split()) == 2:
                tag = event.text.split()[1].replace('!', '')
                if db.isTagExists(tag) and event.from_id in db.getMailingOwners(tag):
                    followers = list(map(lambda x: f'@id{x}', db.getMembersByTag(tag)))
                    for i in range(len(followers)):
                        try:
                            if db.isUser('vk', followers[i][3:]):
                                followers[i] += ' ' + \
                                                rr.getRegionName(
                                                    rr.getAccLocation(
                                                        f'https://rivalregions.com/#slide/profile/{followers[i][3:]}')
                                                )
                        except Exception as e:
                            print(e)
                    space = ' '
                    followers = list(map(
                        lambda x: x.replace(x.split(' ')[0],
                                            f'@id{x.split(space)[0][3:]} ({getName(x.split(space)[0][3:])})'),
                        followers))
                    insertStr = '\n'.join(followers)
                    send(event, f'Подписчики рассылки с тэгом !{tag}:\n{insertStr}', event.from_id)
                else:
                    send(event, f'Тэг не найден!', event.from_id)
            else:
                send(event, 'Не указан тег!', event.peer_id)
        elif event.text.startswith("!join"):
            if len(event.text.split()) == 2:
                accessCode = event.text.split()[1]
                if db.isCodeExists(accessCode):
                    response = db.addUserToMailing(event.from_id, accessCode)
                    send(event, 'Вы подписались!' if response else 'Вы отписались!', event.from_id)
                else:
                    send(event, 'Неверный код!', event.from_id)
            else:
                send(event, 'Не указан код!', event.peer_id)
        if event.text.startswith('!share'):
            if len(event.text.split()) == 3:
                tag = event.text.split()[1]
                if event.from_id in db.getMailingOwners(tag):
                    user_id = int(re.search("(\\d+)", event.text.split()[2]).group(1))
                    response = db.addOwnerToMailing(user_id, tag)
                    send(event, f'Вам расшарили доступ к рассылке !{tag} !' if response else
                    f'У вас забрали доступ к рассылке !{tag} !', user_id)
    if event.text == '!wp' or event.payload == 'WP':
        send(event, 'WP Functions', kb=keyboards.Wp(), domain=event.peer_id)
    if event.text == 'wp цены' or event.payload == "WpЦены":
        send(event, form.formatPricesWp(wp.getPrices()), domain=event.peer_id)
    if event.text.startswith('!earnings'):
        if len(event.text.split()) > 1:
            reg_id = event.text.split()[1]
            response = db.addEarnings(reg_id, event.source, event.peer_id)
            send(event, 'Рассылка доходов подключена' if response else 'Рассылка доходов отключена',
                 source=event.source,
                 domain=event.peer_id)
    if len(original.split()) > 1:
        tag = original.split()[0].replace('!', '')
        if tag in db.getMailingTags() and event.from_id in db.getMailingOwners(tag):
            mailing(event.token, original.split(maxsplit=1)[1:], db.getMembersByTag(tag))
            send(event, 'Разослано!', event.from_id)
    if event.text in ['lang', 'язык', '!lang', '!язык']:
        send(event, 'Choose your language:', kb=keyboards.chooseLanguage(event.source),
             source=event.source, domain=event.peer_id)
    if db.isLangUser(event.source, event.from_id):
        langToResponse = locales.Russian if db.getLang(event.source, event.from_id) == 'ru' else locales.English
    else:
        langToResponse = locales.Russian
    if event.text == '!rr' or event.payload == 'RR':
        send(event, 'RR Functions', kb=keyboards.Main(lang=langToResponse), domain=event.peer_id)
    if event.message_id == 1:
        send(event, langToResponse.greetingVk if event.source == 'vk' else langToResponse.greetingTg, event.peer_id,
             kb=keyboards.Main(langToResponse), source=event.source)
    if event.text == '!мобилизация':
        rate = random.randint(0, 100)
        regions = ['в ДНР', "в ЛНР", "в Запорожье", "в Херсон"]
        text = f'Ваш шанс на мобилизацию равен {rate}%\n'
        if rate == 0:
            text += 'Вы -- Богдан Яковлев'
        elif 0 < rate < 50:
            text += 'Повезло-повезло'
        elif 50 <= rate < 100:
            text += f'Счастливого путешествия {random.choice(regions)}!'
        else:
            text += 'Вы -- Роман Епифанов'
        send(event, text, event.peer_id)
    if event.text in ['!жф', '!hf'] or \
            (event.text in ['жф', 'hf'] and isPrivate(event)) or event.payload == 'ЖФ':
        send(event, f'{langToResponse.homes}:\n' + rr.getIndex('houses'), event.peer_id,
             kb=keyboards.Indexes(langToResponse),
             source=event.source)
    elif event.text in ['!медка', '!hospitals'] or \
            (event.text in ['медка', "hospitals"] and isPrivate(event)) or event.payload == 'Медка':
        send(event, f'{langToResponse.medicine}:\n' + rr.getIndex('hospital'), event.peer_id,
             kb=keyboards.Indexes(langToResponse), source=event.source)
    elif event.text in ['!военка', '!military'] or \
            (event.text in ['военка', 'military'] and isPrivate(event)) or event.payload == 'Военка':
        send(event, f'{langToResponse.military}:\n' + rr.getIndex('war'), event.peer_id,
             kb=keyboards.Indexes(langToResponse), source=event.source)
    elif event.text in ['!школа', '!school'] or \
            (event.text in ['школа', 'school'] and isPrivate(event)) or event.payload == 'Школа':
        send(event, f'{langToResponse.school}\n' + rr.getIndex('school'), event.peer_id,
             kb=keyboards.Indexes(langToResponse), source=event.source)
    elif event.text in ['!таблица', '!table'] or \
            (event.text in ['таблица', 'table'] and isPrivate(event)) or event.payload == 'Таблица':
        makeTable(langToResponse)
        if event.source == 'vk':
            upload = vk_api.VkUpload(vk)
            img = 'upload.jpg'
            photo = upload.photo_messages(img)
            owner_id = photo[0]['owner_id']
            photo_id = photo[0]['id']
            access_key = photo[0]['access_key']
            attachment = f'photo{owner_id}_{photo_id}_{access_key}'
            send(event, langToResponse.table, event.peer_id,
                 kb=keyboards.Indexes(langToResponse),
                 source=event.source, attachment=attachment)
    elif event.text in ['!помощь', '!help'] or (event.text in ['помощь', 'help'] and isPrivate(event)) \
            or event.payload == 'Помощь':
        send(event, langToResponse.greetingTg if event.source == 'tg' else langToResponse.greetingVk, event.peer_id,
             kb=keyboards.Main(langToResponse), source=event.source)
    elif event.text in ['цены', 'price'] or \
            (event.text in ['!цены', '!price'] and isPrivate(event)) or event.payload == 'Рынок':
        send(event, langToResponse.market, event.peer_id,
             kb=keyboards.Prices(langToResponse), source=event.source)
    elif event.text in ['!госырынок', '!statemarket'] or \
            (event.text in ['госырынок', 'statemarket'] and isPrivate(event)) or event.payload == 'Гос':
        send(event, rr.getStatePrices(lang=langToResponse), event.peer_id,
             kb=keyboards.Prices(langToResponse), source=event.source)
    elif event.text == 'назад' and isPrivate(event) or event.payload == 'Назад':
        send(event, langToResponse.menu, event.peer_id,
             kb=keyboards.Main(langToResponse), source=event.source)
    elif event.text == 'рынок' and isPrivate(event) or event.payload == 'Рынок':
        send(event, langToResponse.market, event.peer_id,
             kb=keyboards.privateMarket(langToResponse), source=event.source)
    elif event.text == 'рыночек' and isPrivate(event) or event.payload == 'Рыночек':
        send(event, langToResponse.market, event.peer_id,
             kb=keyboards.privateMarket(langToResponse), source=event.source)
    elif event.text == 'ресурсы' and isPrivate(event) or event.payload == 'Ресурсы':
        send(event, rr.getPricesRss(langToResponse), event.peer_id,
             kb=keyboards.privateMarket(langToResponse), source=event.source)
    elif event.text == 'ресурсы' and isPrivate(event) or event.payload == 'Оружие':
        send(event, rr.getPricesWeapons(langToResponse), event.peer_id,
             kb=keyboards.privateMarket(langToResponse), source=event.source)
    elif event.text == 'индексы' and isPrivate(event) or event.payload == 'Индексы':
        send(event, langToResponse.indexes, event.peer_id,
             kb=keyboards.Indexes(langToResponse), source=event.source)
    elif event.text.startswith('!налог') and isPrivate(event) and event.text != '!налог':
        resp = db.addStateForTaxes(re.search("(\\d+)", event.text).group(1), event.from_id)
        send(event, 'Добавлено!' if resp else 'Удалено!', event.peer_id)
    elif event.text == '!налог' and isPrivate(event):
        if event.from_id != 1:
            result = 0
            units = '\nВаши источники налога:\n'
            for element in db.getAllTaxes(event.from_id):
                _id = int(element['state_id'])
                if _id > 1 or _id == 2 or _id == 3:
                    result += rr.getPartyWage(_id)
                    units += f'https://rivalregions.com/#slide/party/{_id}\n'
                else:
                    result += rr.getStateRegionsAmount(_id)
                    units += f'https://rivalregions.com/#state/details/{_id}\n'
            send(event, f'Ваш налог составляет {result * 100}kkk. \n {units}'
                        f'\nПлатить сюда: https://rivalregions.com/#slide/profile/1', event.from_id)
        else:
            for user in db.getTaxesUsers():
                result = 0
                units = f'\nИсточники налога @id{user}:\n'
                for element in db.getAllTaxes(user):
                    _id = int(element['state_id'])
                    if _id > 2 or _id == 1:
                        result += rr.getPartyWage(_id)
                        units += f'https://rivalregions.com/#slide/party/{_id}\n'
                    else:
                        result += rr.getStateRegionsAmount(_id)
                        units += f'https://rivalregions.com/#state/details/{_id}\n'
                send(event, f'{units}\nНалог составляет {result * 100}kkk. ', event.from_id)
    elif event.text.startswith('!рег') or event.text.startswith('!reg'):
        if re.search("(\\d+)", event.text) is not None:
            if rr.getRegion(re.search("(\\d+)", event.text).group(1)) is None:
                send(event, 'У вас айди битый!', event.peer_id,
                     kb=keyboards.Main(langToResponse), source=event.source)
            else:
                resp = db.addRegToGovernor(event.from_id, re.search("(\\d+)", event.text).group(1))
                send(event, 'Регион добавлен!' if resp else 'Регион удалён!', event.peer_id,
                     kb=keyboards.Main(langToResponse), source=event.source)
        else:
            send(event, 'У вас айди битый!', event.peer_id,
                 kb=keyboards.Main(langToResponse), source=event.source)
    elif event.text in ['!инфа', 'инфа', 'info', '!info'] and isGovernor(str(event.from_id)) or event.payload == 'Инфа':
        for region in db.getGovernorRegions(event.from_id):
            send(0, form.governorInfo(rr.getRegion(region)), event.peer_id,
                 kb=keyboards.Info(region), source=event.source)
    elif event.text.startswith(tuple(['!farm', '!фарм'])) or \
            (event.text.startswith(tuple(['фарм', 'farm'])) and isPrivate(event)) or event.payload == 'Фарм':
        if len(event.text.split(' ')) == 1 or event.text == '':
            send(event, rr.getGoldRemained('1'), event.peer_id, source=event.source)
        elif re.search("(\\d+)", event.text) is not None:
            send(event, rr.getGoldRemained(re.search("(\\d+)", event.text).group(1)), event.peer_id,
                 source=event.source)
        else:
            send(event, 'У вас айди битый!', event.peer_id, source=event.source)
    elif event.text.startswith(tuple(['wars', 'войны'])) or \
            (event.text.startswith(tuple(['!wars', '!войны'])) and isPrivate(event)) or event.payload == 'Войны':
        if len(event.text.split(' ')) == 1 or event.text == ' ':
            send(event, rr.getWars('1'), event.peer_id, source=event.source)
        elif re.search("(\\d+)", event.text) is not None:
            send(event, rr.getWars(re.search("(\\d+)", event.text).group(1)), event.peer_id, source=event.source)
    elif event.text.startswith("стат") or event.text.startswith('perk'):
        stats[event.peer_id] = event.text.split()
        try:
            stat1 = int(stats[event.peer_id][1])
            stat2 = int(stats[event.peer_id][2])
        except Exception:
            send(event, 'У вас статы битые!', event.peer_id)
        if stat1 < 0 or stat2 < 0 or stat1 > 999 or stat2 > 999 or not (stat2 > stat1):
            send(event, 'У вас статы битые!', event.peer_id)
        else:
            if db.isUser(event.source, event.from_id):
                discount = rr.getDiscount(db.getProfile(event.source, event.from_id))
                send(event, f'{dex.getPerksPrice(int(stats[event.peer_id][1]), int(stats[event.peer_id][2]))}\n'
                            f'{dex.getPerksTime(int(stats[event.peer_id][1]), int(stats[event.peer_id][2]), discount)}',
                     event.peer_id, source=event.source)
            else:
                send(event, f'{dex.getPerksPrice(int(stats[event.peer_id][1]), int(stats[event.peer_id][2]))}'
                            f'\nДля расчёта времени привяжите свой аккаунт командой !main\n'
                            f'!main https://rivalregions.com/#slide/profile/your_id', event.peer_id,
                     source=event.source)
    elif event.payload == '1488':
        if not db.isWaits(event.from_id):
            db.addToTime(event.from_id)
            send(event, 'Пришлите ссылку на ваш аккаунт', event.peer_id, source=event.source)
    if db.isWaits(event.peer_id):
        db.removeWaiting(event.from_id)
        if 'https' in event.text:
            if len(event.text) != 0:
                discount = rr.getDiscount(event.text)
            else:
                discount = rr.getDiscount(event.attachments[0]['link']['url'])
            send(event, f'{dex.getPerksTime(int(stats[event.peer_id][1]), int(stats[event.peer_id][2]), discount)}\n',
                 event.peer_id, source=event.source)
    elif (event.text.startswith("фаба") and isPrivate(event)) or event.text.startswith("!фаба"):
        levels = event.text.split()
        if (not int(levels[1]) < 0) and (not int(levels[2]) > 300):
            send(event, f'{dex.getFactory(int(levels[1]), int(levels[2]))}', event.peer_id, source=event.source)
        else:
            send(event, f'У вас левела битые!', event.peer_id, source=event.source)
    elif event.text.startswith('!кб') and isGovernorForCb(event.from_id):
        info = rr.getCashback(re.split('!кб ', event.text)[1].replace('m.', '').replace('#', ''))
        if info[0].strip() == 'Госпиталь':
            typeOf = 1
        elif info[0].strip() == 'Военная база':
            typeOf = 2
        elif info[0].strip() == 'Школа':
            typeOf = 3
        elif info[0].strip() == 'ПВО':
            typeOf = 4
        elif info[0].strip() == 'Порт':
            typeOf = 5
        elif info[0].strip() == 'Электростанция':
            typeOf = 6
        elif info[0].strip() == 'Космодром':
            typeOf = 7
        elif info[0].strip() == 'Аэропорт':
            typeOf = 8
        elif info[0].strip() == 'Жилой фонд':
            typeOf = 9
        else:
            typeOf = 0
        regId = rr.getIdByName(info[1])
        current = rr.getBuildingInRegion(regId, info[0].strip())
        built = re.search(r"\+\d+", info[2]).group(0)
        required = rr.getSpent(re.split('!кб ', event.text)[1].replace('m.', '').replace('#', '')) - int(current)
        send(event, f'@all\nГубер: @id{event.from_id} \nРег: {info[1]} \nУровень: {current} \
            \nЗдание: {info[0].strip()} \nПостроено: {built} \nНужно: {required} \
            \nCсылка: https://rivalregions.com/parliament/donew/build_{typeOf}/{required}/{regId} \
            \nМоб: https://m.rivalregions.com/parliament/donew/build_{typeOf}/{required}/{regId}',
             2000000008)
        send(event, 'Запрос отправлен!', event.peer_id, source=event.source)
    elif event.text.startswith("стройка"):
        typeOf = event.text.split(' ')[1]
        before = int(event.text.split(' ')[2])
        now = int(event.text.split(' ')[3])
        send(event, dex.getPrice(typeOf, before, now), event.peer_id, source=event.source)
    elif event.text.startswith("гр"):
        splitted = event.text.split(' ')
        send(event, form.formDeep(dex.deepExploration(int(splitted[2]), int(splitted[3]), splitted[1])))
    elif event.text == "!гр" and event.from_id == 1:
        rr.makeDeep()
        send(event, 'Сделано!', event.from_id)
    elif event.text.startswith("!хуета") and event.from_id in [1, 1, 1]:
        troops, IFV, AT, heavyArmor, scouts = list(map(int, event.text.split(' ')[1:]))
        damageToTroops = troops * 6 + IFV * 16 + heavyArmor * 10
        damageToLightArmor = troops + IFV * 10 + AT * 20 + heavyArmor * 15
        damageToHeavyArmor = troops + IFV * 5 + AT * 35 + heavyArmor * 10
        damageToScouts = troops * 2 + scouts * 6
        send(event,
             f'Урон по пехоте = {damageToTroops}\nУрон по ЛТ = {damageToLightArmor}\nУрон по ТТ = {damageToHeavyArmor}\n'
             f'Урон по разведке = {damageToScouts}\n\n'
             f'Необходимо войск чтобы покрыть урон:\n'
             f'Автоматы = {damageToTroops // 10 + (1 if damageToTroops % 10 != 0 else 0)}\n'
             f'БМП = {damageToLightArmor // 40 + (1 if damageToLightArmor % 25 != 0 else 0)}\n'
             f'ПТ = {damageToLightArmor // 20 + (1 if damageToLightArmor % 20 != 0 else 0)}\n'
             f'ТТ = {damageToHeavyArmor // 50 + (1 if damageToHeavyArmor % 50 != 0 else 0)}\n'
             f'Разведка = {damageToScouts // 10 + (1 if damageToScouts % 10 != 0 else 0)}\n', event.peer_id)
    elif type(event.payload) == int and not event.payload == '1488' and not event.payload == 0:
        edit(event)
    elif event.payload in ['ru', 'en']:
        db.addLangUser(event.source, event.from_id, event.payload)
        langToResponse = locales.Russian if db.getLang(event.source, event.from_id) == 'ru' else locales.English
        send(event, source=event.source,
             text=langToResponse.greetingVk if event.source == 'vk' else langToResponse.greetingTg,
             domain=event.from_id, kb=keyboards.Main(langToResponse))
    elif str(event.payload).startswith('https://rivalregions.com/#war/details/'):
        print(1)
    elif event.text.startswith(tuple(['!main', '!основа'])):
        _id = re.search("(\\d+)", event.text.split(' ')[1])
        if _id is not None:
            _id = _id.group(0)
            res = db.addUser(event.source, event.from_id, _id)
            if res == 1:
                send(event, 'Аккаунт добавлен!', event.from_id, source=event.source)
            elif res == 2:
                send(event, 'Аккаунт обновлён!', event.from_id, source=event.source)
        else:
            send(event, 'У вас айди битый!', event.peer_id, source=event.source)
    if event.peer_id > 2e9:
        if event.text.split(' ')[0] == 'брак':
            second = int(re.search("(\\d+)", event.text).group(1))
            if db.isMarried(event.peer_id, event.from_id):
                send(event, 'Вы уже состоите в браке :(', event.peer_id)
            elif db.isMarried(event.peer_id, second):
                send(event, f'[id{second}|{getName(second)}] уже состоит в браке :(', event.peer_id)
            else:
                db.addMarriage(event.peer_id, event.from_id, second)
                send(event, f'[id{second}|{getName(second)}], Вы согласны?', event.peer_id, kb=keyboards.Marriage())
        if event.text == 'браки':
            text = 'Браки этой беседы:\n'
            for pair in db.getMarriages(event.peer_id):
                text += f'[id{pair[0]}|{getName(pair[0])}] и [id{pair[1]}|{getName(pair[1])}]\n'
            if text == 'Браки этой беседы:\n':
                send(event, 'Браков пока нет :((', event.peer_id)
            else:
                send(event, text, event.peer_id)
    if event.payload == 'yes' and db.isPending(event.peer_id, event.from_id):
        db.confirmMarriage(event.peer_id, event.from_id)
    if event.event_id != 0 and event.source == 'vk':
        vk.messages.sendMessageEventAnswer(event_id=event.event_id, user_id=event.from_id, peer_id=event.peer_id,
                                           event_data=json.dumps({'type': 'show_snackbar', 'text': 'Cделано!'}))


def getUserName(_id, case='nom', source='vk'):
    print(_id)
    if source == 'vk':
        if _id > 0:
            response = vk.users.get(user_ids=_id, name_case=case)[0]
            return f"[id{_id}|{response['first_name']} {response['last_name']}]"
        else:
            return 'пылесос' if case == 'acc' else 'пылесосу'
    return _id


def getSex(_id, source):
    if source == 'vk':
        response = vk.users.get(user_ids=_id, fields='sex')[0]
        return int(response['sex']) - 1
    return True


def isPrivate(event):
    if event.source == 'vk':
        return event.peer_id < 2e9
    elif event.source == 'tg':
        return event.peer_id > 0


def getAdmins(event, chat_id):
    id_list = []
    if chat_id > 2e9:
        members = vk.messages.getConversationMembers(peer_id=chat_id)['items']
        [id_list.append(el['member_id']) for el in members if 'is_admin' in el]
        return id_list
    return id_list


def getName(user_id):
    resp = vk.users.get(user_ids=user_id, lang=0)[0]
    return f"{resp['first_name']} {resp['last_name']}"


def isGovernor(user_id):
    return user_id in db.getGovernors()


def isGovernorForCb(user_id):
    return user_id in getConvMembers(1)


def getConvMembers(chat_id):
    members = vk.messages.getConversationMembers(peer_id=chat_id)['items']
    id_list = []
    [id_list.append(el['member_id']) for el in members if el['member_id'] > 0]
    return id_list


def makeTable(lang):
    img = Image.new('RGB', (340, 290), color='black')
    font = ImageFont.truetype("font.ttf", 20)
    draw = ImageDraw.Draw(img)
    xAxis = 10
    for typeOf in ['hospital', 'war', 'school', 'houses']:
        if typeOf == 'houses':
            header = lang.homes
        elif typeOf == 'hospital':
            header = lang.medicine
        elif typeOf == 'war':
            header = lang.military
        else:
            header = lang.school
        draw.text(
            (xAxis, 10),
            f'{header}\n{rr.getIndex(typeOf)}',
            (255, 255, 255),
            font=font,
            spacing=8
        )
        xAxis += 82
    img.save('upload.jpg')
    return 1


def edit(event):
    print(event.__repr__)
    vk.messages.edit(
        peer_id=event.peer_id,
        message=form.governorInfo(rr.getRegion(abs(event.payload)), full=(True if int(event.payload) > 0 else False)),
        conversation_message_id=event.cmId,
        keyboard=(keyboards.Hide(abs(event.payload)) if int(event.payload) > 0 else keyboards.Info(abs(event.payload))))


async def parser(state_id, delay, number):
    while True:
        regions = await rr.getPopulationOfState(state_id)
        time.sleep(delay)
        delta = rr.getDelta(regions, await rr.getPopulationOfState(state_id), number)
        if len(delta) > 0:
            delta = str(delta).replace("'", '').replace('m.', '').replace('{', '').replace('}', '').replace(': ', ' - ')
            delta = delta.replace('[', '').replace(']', '').replace(',', '\n'). \
                replace('https://rivalregions.com/#map/details', '\n https://rivalregions.com/#map/details')
            str_delay = delay_string(delay)
            if state_id == 1:
                send(0, text=f"Дельта за {str_delay}:\n {delta}", domain=1, source='tg')
                send(0, text=f"Дельта за {str_delay}:\n {delta}", domain=1, source='tg')
            else:
                send(0, text=f"Дельта за {str_delay}:\n {delta}", domain=1, source='vk')
                send(0, text=f"Дельта за {str_delay}:\n {delta}", domain=1, source='vk')


def warParser(state_id, delay):
    while True:
        try:
            wars = rr.getWarsForBot(state_id)
            time.sleep(delay)
            delta = rr.getWarsDelta(wars, rr.getWarsForBot(state_id))
            if len(delta) > 0:
                response = ''
                for war_id in delta:
                    response += f'https://rivalregions.com/#{war_id}\n'
                    send(0, text=f"ААААА НОВАЯ ВОЙНА\n {response}", domain=1, source='vk')
                    send(0, text=f"ААААА НОВАЯ ВОЙНА\n {response}", domain=1, source='vk')
        except TypeError as e:
            print(e, 'wp')
            time.sleep(0.5)
            warParser(state_id, delay)


def getConvAdmins(chat_id):
    members = vk.messages.getConversationMembers(peer_id=chat_id)['items']
    id_list = []
    for el in members:
        if 'is_admin' in el:
            id_list.append(el['member_id'])
    id_list.append(1)
    return id_list


def kick(chat_id, user_id):
    if int(user_id) > 0 and chat_id > 2e9 and not chat_id == 1 and not int(user_id) == 1:
        if int(user_id) in getConvAdmins(chat_id):
            return 'Указанный @id' + str(user_id) + ' (пользователь) является администратором.'
        else:
            try:
                vk.messages.removeChatUser(chat_id=chat_id - 2e9, user_id=user_id)
                return '@id' + str(user_id) + ' (Пользователь) исключен!'
            except Exception:
                return 'Ошибка'
    else:
        return 'Пользователь не найден'


def delay_string(delay):
    delay_hours = delay // 3600
    delay_minutes = delay % 3600 // 60
    delay_seconds = delay % 60

    str_delay = ''

    if delay_hours:
        str_delay = str(delay_hours)
        if delay_hours % 10 in {2, 3, 4} and (delay_hours // 10) != 1:
            str_delay += " чаcа"
        elif delay_hours == 1 and (delay_hours // 10) != 1:
            str_delay += " час"
        else:
            str_delay += " часов"
        if delay_minutes:
            str_delay += ' '

    if delay_minutes:
        str_delay += str(delay_minutes)
        if delay_minutes % 10 in {2, 3, 4} and (delay_minutes // 10) != 1:
            str_delay += " минуты"
        elif delay_minutes == 1 and (delay_minutes // 10) != 1:
            str_delay += " минута"
        else:
            str_delay += " минут"

    if delay_seconds and not delay_hours:
        if delay_minutes:
            str_delay += ' '
        str_delay += str(delay_seconds)
        if delay_seconds % 10 in {2, 3, 4} and (delay_seconds // 10 != 1):
            str_delay += " секунды"
        elif delay_seconds == 1 and (delay_seconds // 10) != 1:
            str_delay += " секунда"
        else:
            str_delay += " секунд"
    return str_delay


def mailing(message, members):
    vk.messages.send(0, user_ids=members, message=message, random_id=get_random_id())


def deleteMutedMessage(cmId, peer_id):
    vk.messages.delete(delete_for_all=1, cmids=cmId, peer_id=peer_id)


def traceAccs(accs):
    while True:
        try:
            locs = {}
            for acc in accs:
                locs.update({acc: rr.getAccLocation(acc)})
            time.sleep(5)
            for acc in accs:
                if rr.getAccLocation(acc) != locs[acc]:
                    nick = rr.getProfileById(re.search("(\\d+)", acc).group(1))
                    send(0,
                         text=f'ААА ЕБЛАН ПРИЛЕТЕЛ\n({nick}) {acc}  в {rr.getRegionName(rr.getAccLocation(acc))} '
                              f'(https://rivalregions.com/#{rr.getAccLocation(acc)})',
                         domain=1, source='vk')
                    send(0,
                         text=f'ААА ЕБЛАН ПРИЛЕТЕЛ\n({nick}) {acc}  в {rr.getRegionName(rr.getAccLocation(acc))} '
                              f'(https://rivalregions.com/#{rr.getAccLocation(acc)})',
                         domain=1, source='vk')
                    send(0,
                         text=f'ААА ЕБЛАН ПРИЛЕТЕЛ\n({nick}) {acc}  в {rr.getRegionName(rr.getAccLocation(acc))} '
                              f'(https://rivalregions.com/#{rr.getAccLocation(acc)})',
                         domain=1, source='vk')
                    send(0,
                         text=f'ААА ЕБЛАН ПРИЛЕТЕЛ\n({nick}) {acc}  в {rr.getRegionName(rr.getAccLocation(acc))} '
                              f'(https://rivalregions.com/#{rr.getAccLocation(acc)})',
                         domain=1, source='vk')
        except Exception as e:
            print(e, 322)
            time.sleep(10)
            traceAccs(db.getAccsToTrace())
