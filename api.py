# -*- coding: utf-8 -*-
import json
import re
import time
import requests

import telebot
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.utils import get_random_id
from PIL import Image, ImageFont, ImageDraw

import db
import form
import rr
import keyboards
import dex

stats = {}


class MyVkLongPoll(VkBotLongPoll):
    def listen(self):
        while True:
            try:
                for event in self.check():
                    yield event
            except Exception as e:
                print('error', e)


class Event(object):
    def __init__(self, source, text, from_id, peer_id, payload, attachments, message_id, event_id):
        self.source = source
        self.text = text
        self.from_id = from_id
        self.peer_id = peer_id
        self.payload = payload
        self.attachments = attachments
        self.message_id = message_id
        self.event_id = event_id


def formObject(source, event):
    if source == 'vk':
        if event.type == VkBotEventType.MESSAGE_EVENT:
            event = event.object
            from_id = event['user_id']
            peer_id = event['peer_id']
            if 'payload' in event:
                payload = event['payload']['type']
            else:
                payload = 0
            message_id = event['conversation_message_id'] if 'conversation_message_id' in event else 0
            event_id = event['event_id']
            return Event(source, ' ', from_id, peer_id, payload, [], message_id, event_id)
        event = event.message
        text = event['text'] if event['text'] != '' else ' '
        from_id = event['from_id']
        peer_id = event['peer_id']
        if 'payload' in event:
            payload = event['payload']
        else:
            payload = 0
        attachments = event['attachments']
        message_id = event['conversation_message_id']
        return Event(source, text, from_id, peer_id, payload, attachments, message_id, 0)
    if source == 'tg':
        print(event)
        text = event.text if event.text is not None else ' '
        from_id = event.from_user.id
        peer_id = event.chat.id
        if hasattr(event, 'callback_data'):
            payload = event.callback_data
        else:
            payload = 0
        attachments = event.photo
        message_id = event.id
        return Event(source, text, from_id, peer_id, payload, attachments, message_id)


def vkAuth(token=""):
    vk_session = vk_api.VkApi(token=token)
    return MyVkLongPoll(vk_session, group_id=196158761), vk_session.get_api()


longpoll, vk = vkAuth()
bot = telebot.TeleBot('')


def send(text='', domain=160819338, attachment=None, kb=None, source='vk'):
    if source == 'vk':
        if domain > 2000000000:
            kb = keyboards.Empty()
        if isGovernor(str(domain)) and kb == keyboards.Main():
            kb = keyboards.Governor()
        vk.messages.send(peer_id=domain, message=text, attachment=attachment,
                         random_id=get_random_id(), keyboard=kb, v='5.107', dont_parse_links=1)
    elif source == 'tg':
        bot.send_message(domain, text, reply_markup=kb)


def fetcher(event):
    print(event.text)
    original = event.text
    if '@ValerianRR_bot' in event.text:
        event.text = event.text.replace('@ValerianRR_bot', '')
    event.text = event.text.lower() if event.text[0] != '/' else event.text[1:].lower()
    if event.message_id == 1:
        send('????????????! ?? ???????????????? -- ?????? ?????? RR.\nvk.com/@rrvalerian-help', event.peer_id,
             kb=keyboards.Main(), source=event.source)
    if event.text in ['!????', '!hf'] or \
            (event.text in ['????', 'hf'] and isPrivate(event)) or event.payload == '????':
        send(form.formatIndexes(
            requests.get('https://leroque.herokuapp.com/api/indexes/homes').json(), '????'
        ), event.peer_id, kb=keyboards.Indexes(), source=event.source)
    elif event.text in ['!??????????', '!hospitals'] or \
            (event.text in ['??????????', "hospitals"] and isPrivate(event)) or event.payload == '??????????':
        send(form.formatIndexes(
            requests.get('https://leroque.herokuapp.com/api/indexes/hospital').json(), '??????????'
        ), event.peer_id, kb=keyboards.Indexes(), source=event.source)
    elif event.text in ['!????????????', '!military'] or \
            (event.text in ['????????????', 'military'] and isPrivate(event)) or event.payload == '????????????':
        send(form.formatIndexes(
            requests.get('https://leroque.herokuapp.com/api/indexes/military').json(), '????????????'
        ), event.peer_id, kb=keyboards.Indexes(), source=event.source)
    elif event.text in ['!??????????', '!school'] or \
            (event.text in ['??????????', 'school'] and isPrivate(event)) or event.payload == '??????????':
        send(form.formatIndexes(
            requests.get('https://leroque.herokuapp.com/api/indexes/school').json(), '??????????'
        ), event.peer_id, kb=keyboards.Indexes(), source=event.source)
    elif event.text in ['!??????????????', '!table'] or \
            (event.text in ['??????????????', 'table'] and isPrivate(event)) or event.payload == '??????????????':
        makeTable()
        upload = vk_api.VkUpload(vk)
        img = 'upload.jpg'
        photo = upload.photo_messages(img)
        owner_id = photo[0]['owner_id']
        photo_id = photo[0]['id']
        access_key = photo[0]['access_key']
        attachment = f'photo{owner_id}_{photo_id}_{access_key}'
        send('??????????????:', event.peer_id, kb=keyboards.Indexes(), source=event.source, attachment=attachment)
    elif event.text == '!????????????' or (event.text == '????????????' and isPrivate(event)) or event.payload == '????????????':
        send('vk.com/@rrvalerian-help', event.peer_id, kb=keyboards.Main()
             if not str(event.peer_id) in db.getGovernors() else keyboards.Governor(), source=event.source)
    elif event.text in ['????????', 'price'] or \
            (event.text in ['!????????', '!price'] and isPrivate(event)) or event.payload == '????????':
        send(rr.getPrices(), event.peer_id, kb=keyboards.Prices(), source=event.source)
    elif event.text in ['!??????', '!state'] or \
            (event.text in ['??????', 'state'] and isPrivate(event)) or event.payload == '??????':
        send(rr.getStatePrices(), event.peer_id, kb=keyboards.Prices(), source=event.source)
    elif event.text == '??????????' and isPrivate(event) or event.payload == '??????????':
        send('????????', event.peer_id, kb=keyboards.Main(), source=event.source)
    elif event.text == '??????????' and isPrivate(event) or event.payload == '??????????':
        send('??????????', event.peer_id, kb=keyboards.Prices(), source=event.source)
    elif event.text == '??????????????' and isPrivate(event) or event.payload == '??????????????':
        send('??????????????', event.peer_id, kb=keyboards.Indexes(), source=event.source)
    elif event.text.startswith('!??????') or event.text.startswith('!reg'):
        if re.search("(\\d+)", event.text) is not None:
            if rr.getRegion(re.search("(\\d+)", event.text).group(1)) is None:
                send('?? ?????? ???????? ??????????!', event.peer_id, kb=keyboards.Governor(), source=event.source)
            else:
                db.addRegToGovernor(event.from_id, re.search("(\\d+)", event.text).group(1))
                send('???????????? ????????????????!', event.peer_id, kb=keyboards.Governor(), source=event.source)
        else:
            send('?? ?????? ???????? ??????????!', event.peer_id, kb=keyboards.Governor(), source=event.source)
    elif event.text in ['!????????', '????????', 'info', '!info'] and isGovernor(str(event.from_id)) or event.payload == '????????':
        for region in db.getGovernorRegions(event.from_id):
            send(form.governorInfo(rr.getRegion(region)), event.peer_id,
                 kb=keyboards.Info(region), source=event.source)
    elif event.text.startswith(tuple(['!farm', '!????????'])) or \
            (event.text.startswith(tuple(['????????', 'farm'])) and isPrivate(event)) or event.payload == '????????':
        if len(event.text.split(' ')) == 1 or event.text == ' ':
            send(rr.getGoldRemained('3601'), event.peer_id, source=event.source)
        elif re.search("(\\d+)", event.text) is not None:
            send(rr.getGoldRemained(re.search("(\\d+)", event.text).group(1)), event.peer_id, source=event.source)
        else:
            send('?? ?????? ???????? ??????????!', event.peer_id, source=event.source)
    elif event.text.startswith(tuple(['wars', '??????????'])) or \
            (event.text.startswith(tuple(['!wars', '!??????????'])) and isPrivate(event)) or event.payload == '??????????':
        if len(event.text.split(' ')) == 1 or event.text == ' ':
            send(rr.getWars('3601'), event.peer_id, source=event.source)
        elif re.search("(\\d+)", event.text) is not None:
            send(rr.getWars(re.search("(\\d+)", event.text).group(1)), event.peer_id, source=event.source)
    elif event.text.startswith('!??????') and isPrivate(event):
        db.addAccount(event.from_id, list(map(lambda x: x.strip(), original.split('\n')[1:])))
    elif event.text.startswith('????????') and isPrivate(event):
        send(db.getAllAccountsByHolder(event.peer_id), source=event.source)
    elif event.text.startswith('????????'):
        user_id = event.text.split('???????? ')[1]
        send(rr.getProfile(db.getAcc(user_id)), event.peer_id, kb=keyboards.Inline(user_id, event.source),
             source=event.source)
    elif event.text in ['????????', '????????????', '??????????', '?????????? r', '???????? r', '???????????? r'] and len(event.payload) != 0:
        db.addTask('perk', event.payload.replace('{', '').replace('}', '').replace('"', ''))
    elif event.text in ['??????????'] and len(event.payload) != 0:
        db.addTask('work', event.payload.replace('{', '').replace('}', '').replace('"', ''))
    elif event.text in ['????????'] and len(event.payload) != 0:
        db.addTask('auto', event.payload.replace('{', '').replace('}', '').replace('"', ''))
    elif event.text.startswith("????????") or event.text.startswith('perk'):
        stats[event.peer_id] = event.text.split()
        try:
            stat1 = int(stats[event.peer_id][1])
            stat2 = int(stats[event.peer_id][2])
        except Exception:
            send('?? ?????? ?????????? ??????????!', event.peer_id)
        if stat1 < 0 or stat2 < 0 or stat1 > 999 or stat2 > 999 or not (stat2 > stat1):
            send('?? ?????? ?????????? ??????????!', event.peer_id)
        else:
            if db.isUser(event.source, event.from_id):
                discount = rr.getDiscount(db.getProfile(event.source, event.from_id))
                send(f'{dex.getPerksPrice(int(stats[event.peer_id][1]), int(stats[event.peer_id][2]))}\n'
                        f'{dex.getPerksTime(int(stats[event.peer_id][1]), int(stats[event.peer_id][2]), discount)}',
                        event.peer_id, kb=keyboards.anotherAcc(), source=event.source)
            else:
                send(f'{dex.getPerksPrice(int(stats[event.peer_id][1]), int(stats[event.peer_id][2]))}'
                     f'\n???????????? ???????????????????? ???????????', event.peer_id,
                     kb=keyboards.getTime(), source=event.source)
    elif event.payload == '1488':
        send('???????????????? ???????????? ???? ?????? ??????????????', event.peer_id, source=event.source)
        db.addToTime(event.peer_id)
    elif db.isWaits(event.peer_id):
        if len(event.text) != 0:
            discount = rr.getDiscount(event.text)
        else:
            discount = rr.getDiscount(event.attachments[0]['link']['url'])
        send(f'{dex.getPerksTime(int(stats[event.peer_id][1]), int(stats[event.peer_id][2]), discount)}\n',
             event.peer_id, source=event.source)
    elif (event.text.startswith("????????") and isPrivate(event)) or event.text.startswith("!????????"):
        levels = event.text.split()
        send(f'{dex.getFactory(int(levels[1]), int(levels[2]))}', event.peer_id, source=event.source)
    elif event.text.startswith('!????') and isGovernorForCb(event.from_id):
        info = rr.getCashback(re.split('!???? ', event.text)[1].replace('m.', '').replace('#', ''))
        if info[0].strip() == '??????????????????':
            typeOf = 1
        elif info[0].strip() == '?????????????? ????????':
            typeOf = 2
        elif info[0].strip() == '??????????':
            typeOf = 3
        elif info[0].strip() == '??????':
            typeOf = 4
        elif info[0].strip() == '????????':
            typeOf = 5
        elif info[0].strip() == '????????????????????????????':
            typeOf = 6
        elif info[0].strip() == '??????????????????':
            typeOf = 7
        elif info[0].strip() == '????????????????':
            typeOf = 8
        elif info[0].strip() == '?????????? ????????':
            typeOf = 9
        else:
            typeOf = 0
        regId = rr.getIdByName(info[1])
        current = rr.getBuildingInRegion(regId, info[0].strip())
        built = re.search(r"\+\d+", info[2]).group(0)
        required = rr.getSpent(re.split('!???? ', event.text)[1].replace('m.', '').replace('#', '')) - int(current)
        send(f'@all\n??????????: @id{event.from_id} \n??????: {info[1]} \n??????????????: {current} \
            \n????????????: {info[0].strip()} \n??????????????????: {built} \n??????????: {required} \
            \nC??????????: https://rivalregions.com/parliament/donew/build_{typeOf}/{required}/{regId} \
            \n??????: https://m.rivalregions.com/parliament/donew/build_{typeOf}/{required}/{regId}',
             2000000008)
        send('???????????? ??????????????????!', event.peer_id)
    elif event.text.startswith("??????????????"):
        typeOf = event.text.split(' ')[1]
        before = int(event.text.split(' ')[2])
        now = int(event.text.split(' ')[3])
        send(dex.getPrice(typeOf, before, now), event.peer_id)
    elif event.text.startswith(tuple(['!def', '!atk'])):
        side = 0 if event.text.split(' ')[0][1:] == 'atk' else 1
        link = re.search("(\\d+)", event.text.split(' ')[1]).group(0)
        if len(event.text.split(' ')) < 3:
            speed = 'hours'
        else:
            speed = 'hours' if event.text.split(' ')[2] != 'auto' else 'auto'
        requests.post(f"https://leroque.herokuapp.com/api/addWar/{side}/{link}/{speed}")
    elif type(event.payload) == int and not event.payload == '1488' and not event.payload == 0:
        edit(event)
    elif event.text.startswith(tuple(['!main', '!????????????'])):
        _id = re.search("(\\d+)", event.text.split(' ')[1])
        if _id is not None:
            _id = _id.group(0)
            res = db.addUser(event.source, event.from_id, _id)
            if res == 1:
                send('?????????????? ????????????????!', event.peer_id)
            elif res == 2:
                send('?????????????? ????????????????!', event.peer_id)
        else:
            send('?? ?????? ???????? ??????????!', event.peer_id)
    if event.text == '??????????????' and len(event.payload) != 0:
        db.addTask('money', event.payload.replace('{', '').replace('}', '').replace('"', ''))
    if event.event_id != 0:
        vk.messages.sendMessageEventAnswer(event_id=event.event_id, user_id=event.from_id, peer_id=event.peer_id,
                                           event_data=json.dumps({'type': 'show_snackbar', 'text': 'C????????????!'}))


def isPrivate(event):
    if event.source == 'vk':
        return event.peer_id < 2000000000
    return True


def getAdmins(chat_id):
    id_list = []
    if chat_id > 2000000000:
        members = vk.messages.getConversationMembers(peer_id=chat_id)['items']
        [id_list.append(el['member_id']) for el in members if 'is_admin' in el]
        return id_list
    return id_list


def getName(user_id):
    resp = vk.users.get(user_ids=user_id, lang=0)[0]
    return resp['first_name'] + ' ' + resp['last_name']


def isGovernor(user_id):
    return user_id in db.getGovernors()


def isGovernorForCb(user_id):
    return user_id in getConvmembers(2000000009)


def getConvmembers(chat_id):
    members = vk.messages.getConversationMembers(peer_id=chat_id)['items']
    id_list = []
    [id_list.append(el['member_id']) for el in members if el['member_id'] > 0]
    return id_list


def doTasks():
    for task in db.tasks.find():
        if task['type'] == 'work':
            login = task['login'].split(':')[0]
            rr.doWork(db.getAcc(login))
        if task['type'] == 'perk':
            login, typeOf = task['login'].split(':')
            rr.upPerk(db.getAcc(login), typeOf)
    time.sleep(605)
    doTasks()


def doRareTasks():
    for task in db.tasks.find():
        if task['type'] == 'money':
            login = task['login'].split(':')[0]
            rr.sendMoney(db.getAcc(login), rr.getMoney(db.getAcc(login)))
        if task['type'] == 'auto':
            login = task['login'].split(':')[0]
            rr.renewAuto(db.getAcc(login))
    time.sleep(60*60*24)
    doRareTasks()


def makeTable():
    img = Image.new('RGB', (340, 290), color='black')
    font = ImageFont.truetype("font.ttf", 20)
    draw = ImageDraw.Draw(img)
    xAxis = 10
    for typeOf in ['hospital', 'military', 'school', 'homes']:
        if typeOf == 'homes':
            header = '    ????'
        elif typeOf == 'hospital':
            header = '  ??????????'
        elif typeOf == 'military':
            header = ' ????????????'
        elif typeOf == 'school':
            header = '  ??????????'
        else:
            header = 'placeholder'
        draw.text(
            (xAxis, 10),
            f"{form.formatIndexes(requests.get(f'https://leroque.herokuapp.com/api/indexes/{typeOf}').json(), header)}",
            (255, 255, 255),
            font=font,
            spacing=8
        )
        xAxis += 82
    img.save('upload.jpg')
    return 1


def edit(event):
    vk.messages.edit(
        peer_id=event.peer_id,
        message=form.governorInfo(rr.getRegion(abs(event.payload)), full=(True if int(event.payload) > 0 else False)),
        conversation_message_id=event.message_id,
        keyboard=(keyboards.Hide(abs(event.payload)) if int(event.payload) > 0 else keyboards.Info(abs(event.payload))))
