import time

import requests
import re
import dex
from lxml import html
from lxml import etree

import datetime
import api
import db

c = ''
sessions = {}


class Handler(object):
    def __init__(self, email, password, proxies=None, bot=False):
        if bot:
            self.session = self.makeBotSession(email, proxies)
        else:
            self.session = self.makeSession(email, password, proxies)

    def get(self, link, data='', auth=None):
        if self.checkValid(self.session):
            response = self.session.get(link, data=data)
            return response
        else:
            if auth[0] != '+79779325127':
                self.session = self.makeBotSession(auth[0], auth[1])
                response = self.session.get(link, data=data)
            else:
                self.session = self.makeSession(auth[0], auth[1], auth[2], auth[0] != '+79779325127')
                response = self.session.get(link, data=data)
        return response

    def post(self, link, data='', auth=None):
        if self.checkValid(self.session):
            response = self.session.post(link, data=data)
        else:
            if auth[0] != '+79779325127':
                self.session = self.makeBotSession(auth[0], auth[1])
                response = self.session.post(link, data=data)
            else:
                self.session = self.makeSession(auth[0], auth[1], auth[2], auth[0] != '+79779325127')
                response = self.session.post(link, data=data)
        return response

    @staticmethod
    def checkValid(session):
        if "$('.vkvk').attr('url', 'https://oauth.vk.com/authorize" in session.get('https://rivalregions.com/').text:
            return 0
        return 1

    @staticmethod
    def makeSession(email, password, proxies=None, _id=None):
        if proxies is None:
            proxies = {'https': 'https://fcmetalurglpO0:B3i7VgX@93.88.77.125:34512/',
                       'http': 'http://fcmetalurglpO0:B3i7VgX@93.88.77.125:34512/'}
        try:
            session = requests.Session()
            session.trust_env = False
            session.proxies = proxies
            session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                              '(KHTML, like Gecko) Chrome/81.0.4044.142 Safari/537.36'})
            info = db.getAcc(email)
            if email != '+79779325127' and len(info[4]) != 0:
                session.cookies.update(info[4])
            else:
                1
            rrAuth = session.get(
                'https://oauth.vk.com/authorize?client_id=3524629&display=page&scope=notify,friends&'
                'redirect_uri=https://rivalregions.com/main/vklogin&response_type=code&state=')
            data = {
                'ip_h': re.search('ip_h" value="(.+)"', rrAuth.text).group(1),
                'lg_h': re.search('lg_h" value="(.+)"', rrAuth.text).group(1),
                'to': re.search('to" value="(.+)"', rrAuth.text).group(1),
                '_origin': re.search('_origin" value="(.+)"', rrAuth.text).group(1),
                'expire': '0',
                'email': email,
                'pass': password
            }
            vk_auth = session.post('https://login.vk.com/?act=login&soft=1', data=data, allow_redirects=True)
            try:
                vk_auth = session.post(re.search('location.href = "(.+)"', vk_auth.text).group(1))
                user_id = re.search('id" value="(.+)"', vk_auth.text).group(1)
            except Exception:
                user_id = re.search('id" value="(.+)"', vk_auth.text).group(1)
            h = re.search('hash" value="(.+)"', vk_auth.text).group(1)
            token = re.search('access_token" value="(.+)"', vk_auth.text).group(1)
            session.get(
                f'https://rivalregions.com/?id={user_id}&id={user_id}&gl_number=ru&gl_photo=&gl_photo_medium=&'
                f'gl_photo_big=&tmz_sent=3&wdt_sent=984&register_locale=ru&stateshow=&access_token=' +
                token + '&hash=' + h)
            if [email] in db.getAccounts():
                print('aff', session.cookies.get_dict(domain='.vk.com'), _id)
                db.saveSession(session.cookies.get_dict(domain='rivalregions.com'), email, _id)
                db.saveVk(session.cookies.get_dict(domain='.vk.com'), email, _id)
            return session
        except IndexError:
            api.send('Беды с доступом к РР')
            return 0

    def makeBotSession(self, login, proxies):
        info = db.getAcc(login)
        print(info)
        try:
            session = requests.Session()
            info = db.getAcc(login)
            if len(info[3]) == 0:
                print(1)
                return self.makeSession(info[0], info[1], info[2], info[5])
            session.cookies.update(info[3])
            db.saveVk(session.cookies.get_dict(domain='.vk.com'), info[0], info[5])
            session.proxies = proxies
            session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                                                  '(KHTML, like Gecko) Chrome/81.0.4044.142 Safari/537.36'})
            if "$('.vkvk').attr('url', 'https://oauth.vk.com/authorize" in session.get(
                    'https://rivalregions.com/').text:
                return self.makeSession(info[0], info[1], info[2], info[5])
            return session
        except IndexError as e:
            print(e)
            return self.makeSession(info[0], info[1], info[2], info[5])

    def getCookies(self):
        return requests.utils.dict_from_cookiejar(self.session.cookies)


rr = Handler('', '', None, False)


def getIndexOfReg(reg_id, typeOf):
    tree = html.fromstring(rr.get(f'https://rivalregions.com/listed/country/-2/0/{typeOf}', data={'c': c}).text)
    return tree.xpath(f'//tr[@user="{reg_id}"]/td/text()')[1]


def getPrices(response=''):
    types = [["3", 'Нефть: '], ["4", 'Руда: '], ["11", 'Уран: '], ["15", 'Алмазы: ']]
    rr.get(link='https://rivalregions.com/storage', data={'c': c})
    for resource in types:
        tree = html.fromstring(rr.post(link=f'https://rivalregions.com/storage/market/{resource[0]}',
                                       data={'c': c}).text)
        price = tree.xpath('//span[@class="storage_buy_summ"]/text()')
        response += resource[1] + price[0] + '\n'
    return response


def getPrices2(response=None):
    if response is None:
        response = []
    types = [["3", 'Нефть: '], ["4", 'Руда: '], ["15", 'Алмазы: '], ["11", 'Уран: ']]
    rr.get(link='https://rivalregions.com/storage', data={'c': c})
    for resource in types:
        tree = html.fromstring(rr.post(link=f'https://rivalregions.com/storage/market/{resource[0]}',
                                       data={'c': c}).text)
        price = tree.xpath('//span[@class="storage_buy_summ"]/text()')
        response.append(price[0].replace('.', ''))
    return response


def getStatePrices(response=''):
    types = [['1000', 'Золото: '], ["1003", 'Нефть: '], ["1004", 'Руда: '], ["1011", 'Уран: '], ["1015", 'Алмазы: ']]
    rr.get('https://rivalregions.com/leader/storage', data={'c': c})
    for resource in types:
        tree = html.fromstring(rr.post(f'https://rivalregions.com/storage/market/{resource[0]}',
                                       data={'c': c}).text)
        price = tree.xpath('//span[@class="storage_see dot pointer hov2 imp"]/text()')
        response += resource[1] + price[0] + '\n'
    return response.replace('R', '')


def getRedBorder():
    tree = html.fromstring(rr.get('https://rivalregions.com/listed/country/-2/0/homes', data={'c': c}).text)
    merged = dict(zip(tree.xpath('//td[@rat]/@rat'), tree.xpath('//td[@rat]/text()')))
    for key, value in merged.items():
        if value == '2':
            last = key
        elif value == '1':
            return int(last.split('.')[0])


def getRegion(regId):
    text = rr.get(f'https://rivalregions.com/map/details/{regId}', data={'c': c}).text
    if len(text) > 100:
        tree2 = html.fromstring(rr.get(f'https://rivalregions.com/map/details/{regId}', data={'c': c}).text)
        if 'Жилой фонд' in str(tree2.xpath(f'//span[@action]/text()')[10]):
            buildings = tree2.xpath(f'//span[@action]/text()')[3:11]
        else:
            buildings = tree2.xpath(f'//span[@action and @action != "listed/space"]/text()')[3:12]
        electricity = countElectricity(buildings[:-1])
        damage = tree2.xpath(f'//span[@action="listed/damage"]/text()')
        tree = html.fromstring(rr.get('https://rivalregions.com/listed/country/-2/0/homes', data={'c': c}).text)
        return [tree.xpath(f'//tr[@user="{regId}"]/td/text()'), damage, electricity, buildings]
    return None


def getBuildingInRegion(regId, typeOf):
    tree2 = html.fromstring(rr.get(f'https://rivalregions.com/map/details/{regId}', data={'c': c}).text)
    if 'Жилой фонд' in str(tree2.xpath(f'//span[@action]/text()')[10]):
        buildings = tree2.xpath(f'//span[@action]/text()')[3:11]
    else:
        buildings = tree2.xpath(f'//span[@action and @action != "listed/space"]/text()')[3:12]
    for building in buildings:
        if typeOf in building:
            return re.search("(\\d+)", building).group(0)


def getIdByName(name):
    try:
        tree = html.fromstring(rr.get('https://rivalregions.com/map', data={'c': c}).text)
        return tree.xpath(f'.//div[contains(text(),"{str(name)}")]')[0].attrib['m']
    except IndexError:
        try:
            tree = html.fromstring(rr.get('https://rivalregions.com/map/index/0/0/2', data={'c': c}).text)
            return tree.xpath(f'.//div[contains(text(),"{str(name)}")]')[0].attrib['m']
        except IndexError:
            try:
                tree = html.fromstring(rr.get('https://rivalregions.com/map/index/0/0/1', data={'c': c}).text)
                return tree.xpath(f'.//div[contains(text(),"{str(name)}")]')[0].attrib['m']
            except IndexError:
                return IndexError


def getPrice(typeOf):
    rr.get('https://rivalregions.com/leader/storage', data={'c': c})
    tree = html.fromstring(rr.post(f'https://rivalregions.com/storage/market/{typeOf}', data={'c': c}).text)
    return tree.xpath('//span[@class="storage_see dot pointer hov2 imp"]/text()')[0].split(' R')[0]


def getGoldRemained(state, response=f'Топ регионов с наибольшими запасами золота:\n'):
    text = rr.get(f'https://rivalregions.com/listed/stateresources/{state}', data={'c': c}).text
    if len(text) > 100:
        tree = html.fromstring(rr.get(f'https://rivalregions.com/listed/stateresources/{state}', data={'c': c}).text)
        regions = dict(zip(tree.xpath('//td/@action')[0::2], map(float, tree.xpath('//td/text()')[6::8])))
        regions = {k: v for k, v in sorted(regions.items(), reverse=True, key=lambda item: item[1])}
        ids = list(regions.keys())
        gold = list(map(int, list(regions.values())))
        empty = sum(list(map(lambda x: x == 0, gold)))
        for i in range(10 if len(gold) > 10 else len(gold)):
            response += f'https://rivalregions.com/#{ids[i]} -- {gold[i]}\n'
        return response + f'Выкопанных регионов: {empty}'
    return None


def getWars(state, response='Активные войны:\n'):
    if len(rr.get(f'https://rivalregions.com/listed/statewars/{state}', data={'c': c}).text) != 0:
        tree = html.fromstring(rr.get(f'https://rivalregions.com/listed/statewars/{state}', data={'c': c}).text)
        wars = tree.xpath('//td/@action')[3::4]
        sides = list(filter(lambda side: 'map/' in side, tree.xpath('//div/@action')))
        time = list(filter(lambda size: len(size) <= 6,
                           re.findall(': (\\d+),', rr.get(
                               f'https://rivalregions.com/listed/statewars/{state}',
                               data={'c': c}).text)))
        buffer = list(map(lambda x: f'{x.split(".")[0]}{"k" * (len(x.split(".")) - 1)}',
                          tree.xpath('//td[@class="list_avatar pointer imp small"]/text()')))
        for i in range(len(wars)):
            emoji = '⚔' if str(state) in sides[2 * i] else '🔥' if '0' in sides[2 * i] else '🛡️'
            response += f'https://rivalregions.com/#{wars[i]} {buffer[i]} ' \
                        f'{datetime.timedelta(seconds=int(time[i]))} {emoji} \n'
        return response if len(wars) > 0 else 'Войн нет!'
    elif len(rr.get(f'https://rivalregions.com/war/bloc/{state}', data={'c': c}).text) != 0:
        tree = html.fromstring(rr.get(f'https://rivalregions.com/war/bloc/{state}', data={'c': c}).text)
        wars = tree.xpath('//td/@action')[3::4]
        sides = list(filter(lambda side: 'map/' in side, tree.xpath('//div/@action')))
        time = list(filter(lambda size: len(size) <= 6, re.findall(': (\\d+),',
                                                                   rr.get(f'https://rivalregions.com/war/bloc/{state}',
                                                                          data={'c': c}).text)))
        buffer = list(map(lambda x: f'{x.split(".")[0]}{"k" * (len(x.split(".")) - 1)}',
                          tree.xpath('//td[@class="list_avatar pointer imp small"]/text()')))
        for i in range(len(wars)):
            emoji = '⚔' if str(state) in sides[2 * i] else '🔥' if '0' in sides[2 * i] else '🛡️'
            response += f'https://rivalregions.com/#{wars[i]} {buffer[i]} ' \
                        f'{datetime.timedelta(seconds=int(time[i]))} {emoji} \n'
        return response if len(wars) > 0 else 'Войн нет!'
    else:
        return 'Нет такого блока или госа!'


def getProfile(info, response=''):
    login, password, proxies = info[0], info[1], info[2]
    accSession = Handler(login, password, proxies, False)
    tree = html.fromstring(accSession.get('https://rivalregions.com/slide/profile/', auth=info).text)
    response += tree.xpath('//h1[@class="white hide_for_name"]/text()')[0] + '\n' + 'Навыки: '
    for perk in range(1, 4):
        response += tree.xpath('//span[@action="listed/perk/' + str(perk) + '"]/text()')[0] + ('/' if perk != 3 else '')
    response += '\nРегион: ' + getRegion(re.search("(\d+)",
                          tree.xpath('//div[starts-with(@action, "map/details/")]')[0].attrib['action']).group(1))[0][0]
    response += '\n' + tree.xpath('//div[@style="position: absolute; width: 200px; text-align: center;"]/text()')[0]
    tree = html.fromstring(accSession.get('https://rivalregions.com/#overview', auth=info).text)
    response += '\nБаланс: ' + tree.xpath('//span[@id="m"]/text()')[0] + ' R'
    response += '\n' + tree.xpath('//span[@id="g"]/text()')[0] + ' G'
    return response


def getMoney(info):
    login, password, proxies = info[0], info[1], info[2]
    accSession = Handler(login, password, proxies, False)
    tree = html.fromstring(accSession.get('https://rivalregions.com/#overview', auth=info).text)
    response = tree.xpath('//span[@id="m"]/text()')[0]
    return response.replace('.', '')


def getGold(info):
    login, password, proxies = info[0], info[1], info[2]
    accSession = Handler(login, password, proxies, False)
    tree = html.fromstring(accSession.get('https://rivalregions.com/#overview', auth=info).text)
    response = tree.xpath('//span[@id="g"]/text()')[0]
    return response.replace('.', '')


def upPerk(info, typeOf):
    login, password, proxies = info[0], info[1], info[2]
    accSession = Handler(login, password, proxies, True)
    _c = getCForBot(accSession, info)
    if int(typeOf) in [1, 2, 3]:
        accSession.post(f'https://rivalregions.com/perks/up/{typeOf}/2',
                        data={'c': _c}, auth=info)
    elif int(typeOf) in [4, 5, 6]:
        accSession.post(f'https://rivalregions.com/perks/up/{int(typeOf) - 3}/1',
                        data={'c': _c}, auth=info)
    return "Done"


def getCForBot(accSession, info):
    _c = db.getAcc(info[0])[6]
    if len(_c) < 10:
        _c = re.search("c_html = '(.+)'", accSession.get('https://rivalregions.com/', auth=info).text).group(1)
        db.insertC(info[0], _c)
    return _c


def doWork(info):
    login, password, proxies = info[0], info[1], info[2]
    accSession = Handler(login, password, proxies, True)
    _c = getCForBot(accSession, info)
    toughness = int(getToughness(accSession, info))
    if toughness > 50:
        number = 20
    elif toughness > 40:
        number = 18
    else:
        number = 16
    accSession.get(f'https://rivalregions.com/main/energy_fill?c={_c}',
                   data={'c': _c}, auth=info)
    accSession.post(f'https://rivalregions.com/factory/go/{number}', data={'c': _c}, auth=info)
    accSession.get(f'https://rivalregions.com/main/energy_fill?c={_c}',
                   data={'c': _c}, auth=info)
    accSession.get(f'https://rivalregions.com/storage/newproduce/17/{number * 10}?c={_c}'
                   , auth=info)
    return 0


def getDiscount(link):
    if 'profile' not in link:
        link = f'https://rivalregions.com/slide/profile/{link}'
    tree = html.fromstring(rr.get(link.replace('m.', '').replace('#', '')).text)
    library = re.search("(\\d+)", tree.xpath('//span[@action="listed/houses/2"]/text()')[0]).group(1)
    residency = int(getIndexOfReg(getIdByName(str(tree.xpath('//span[@class="dot"]/text()')[1]).replace(' ', ' ')),
                                  'school'))
    return int(residency), int(library)


def getProfileById(info):
    response = []
    text = rr.get(info).text
    tree = html.fromstring(text)
    if 'Неактивные' in text:
        return 'Inactive'
    nick = tree.xpath('//h1[@class="white hide_for_name"]/text()')[0].split('Профиль: ')[1]
    if ']' in nick:
        nick = nick.split('] ')[1]
    response.append(nick)
    response.append(tree.xpath('//span[@class="dot"]/text()')[-1])
    response.append(re.search(r'\d+',
                              tree.xpath(
                                  '//div[@style="position: absolute; width: 200px; text-align: center;"]/text()')[0])
                    .group(0))
    for perk in range(1, 4):
        response.append(tree.xpath('//span[@action="listed/perk/' + str(perk) + '"]/text()')[0])
    return response


def getCashback(link):
    if not rr:
        return 0
    tree = html.fromstring(rr.get(link, data={'c': c}).text)
    info = tree.xpath('//div[@class="float_left offer_show_type small"]/text()')[0].replace(':', '').split(', ')
    return info


def parseParties(_ids):
    response = []
    for _id in _ids:
        table = etree.HTML(rr.get(f'https://rivalregions.com/info/parties/{_id}').text).find("body/table")
        rows = iter(table)
        next(rows)
        for row in rows:
            toAppend = []
            for i, col in enumerate(row):
                if len(col.getchildren()) > 0:
                    for a in col.getchildren():
                        toAppend.append(a.get('href'))
                        toAppend.append(a.text)
                elif i in [2, 7, 8, 9]:
                    toAppend.append(col.text)
            response.append(toAppend)
    response.sort(key=lambda x: int(x[2]), reverse=True)
    print(response)
    return response


def parseState(_id):
    table = etree.HTML(rr.get(f'https://rivalregions.com/info/regions/{_id}').text).find("body/table")
    rows = iter(table)
    next(rows)
    response = []
    for row in rows:
        toAppend = []
        for i, col in enumerate(row):
            if len(col.getchildren()) > 0:
                for a in col.getchildren():
                    toAppend.append(a.text)
            if i in range(5, 14):
                toAppend.append(int(col.text))
        response.append(toAppend)
    return response


def getToughness(accSession, info):
    tree = html.fromstring(accSession.get('https://rivalregions.com/slide/profile/', auth=info).text)
    return tree.xpath('//span[@action="listed/perk/3"]/text()')[0]


def getSpent(law):
    tree = html.fromstring(rr.get(law, data={'c': c}).text)
    info = tree.xpath('//div[@class="float_left offer_show_type small"]/span/@title')
    typeOf = tree.xpath('//div[@class="float_left offer_show_type small"]'
                        '/text()')[0].replace(':', '').split(', ')[0].strip()
    start = getBuildingInRegion(getIdByName(getCashback(law)[1]), typeOf)
    return dex.countCbHouses(int(info[0].split(' ')[0].replace('.', '')), typeOf, start)


def getStateEarnings(_id):
    response = []
    tree = html.fromstring(rr.get('https://rivalregions.com/listed/earned/states', data={'c': c}).text)
    state = tree.xpath(f'//tr[@user={_id}]/td')
    for res in state:
        response.append(res.text)
    return response


def countElectricity(buildings):
    electricity = 0
    for building in buildings:
        print(building)
        if 'Электростанция' in building:
            electricity += int(re.search(r'\d+', building).group(0)) * 10
        else:
            electricity -= int(re.search(r'\d+', building).group(0)) * 2
    return electricity


def getFactory(_id):
    tree = html.fromstring(rr.get(f'https://rivalregions.com/factory/index/{_id}', data={'c': c}).text)
    indexes = getResIndexes(tree.xpath('//span[@class="factory_whose"]/text()')[0])
    level = int(re.search(r'\d+', tree.xpath('//span[@class="imp"]/text()')[0]).group(0))
    typeOf = tree.xpath('//span[@class="imp"]/text()')[0]
    if "Урановая шахта" in typeOf:
        indexes = indexes[3]
    elif "Золотоносная шахта" in typeOf:
        indexes = indexes[0]
    elif "Нефтяная вышка" in typeOf:
        indexes = indexes[1]
    elif "Рудный карьер" in typeOf:
        indexes = indexes[2]
    elif "Алмазная шахта" in typeOf:
        indexes = indexes[4]
    salary = int(re.search(r'\d+', tree.xpath('//h2[@class="white imp"]/text()')[0]).group(0))
    return dex.countMostIncome(level, salary, indexes)


def getResIndexes(name):
    _id = getIdByName(name)
    text = rr.get(f'https://rivalregions.com/map/details/{_id}', data={'c': c}).text
    return list(map(int, re.findall(r'/(\d+)[\s+(|,]', text)))


def sendMoney(info, n, _id=160819338):
    login, password, proxies = info[0], info[1], info[2]
    accSession = Handler(login, password, proxies, True)
    print(info, n)
    accSession.post('https://rivalregions.com/storage/donate', auth=info, data={
        'whom': _id,
        'type': 0,
        'n': n,
        'c': getCForBot(accSession, info)
    })


def getIncomes():
    tree = html.fromstring(rr.get(f'https://rivalregions.com/log/index/money', data={'c': c}).text)
    donations = tree.xpath('//tr[@class="list_link"]')
    for donate in donations:
        if donate[2].xpath('text()')[0] == 'Пожертвование: ':
            if '+' in donate[1].xpath('text()')[0]:
                summa = re.search(r"\d+", donate[1].xpath('text()')[0].replace(' ', '').replace('.', '')).group(0)
                author = re.search(r"\d+", donate[2][0].attrib['action']).group(0)  
                print(summa, author)


def getFactoryId(info):
    login, password, proxies = info[0], info[1], info[2]
    accSession = Handler(login, password, proxies, True)
    res = accSession.get('https://rivalregions.com/slide/profile').text
    _id = re.search(r'action="factory/index/(\d+)', res).group(1)
    return _id


def renewAuto(info):
    login, password, proxies = info[0], info[1], info[2]
    accSession = Handler(login, password, proxies, True)
    for i in range(3):
        accSession.get('https://rivalregions.com/main', data={'c': c})
    accSession.get(f'https://rivalregions.com/storage/newproduce/17/{int(getGold(info))*10}'
                   f'?c={getCForBot(accSession, info)}', data={'c': c})
    accSession.post('https://rivalregions.com/work/autoset/', data={
        'c': getCForBot(accSession, info),
        'mentor': 0,
        'factory': getFactoryId(info),
        'type': 0,
        'lim': 0
    })







