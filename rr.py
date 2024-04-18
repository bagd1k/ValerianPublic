import requests
import re

import db
from lxml import html
from lxml import etree
import time
import datetime
import api
import asyncio
import aiohttp

import dex

c = '1'
CNair = '1'
cMoe = '1'

cookies = {
    'a': 'b'
}

cookiesNair = {
    'a': 'b'
}

cookiesMoe = {
    'a': 'b'
}


class ApiHandler(requests.Session):
    def __init__(self):
        super().__init__()
        self.headers.update({'Authorization': 'Bearer a'})


apiHandler = ApiHandler()


class Handler2(object):
    def __init__(self):
        self.session = self.makeSession()

    def get(self, link, data=''):
        if self.checkValid(self.session):
            response = self.session.get(link, data=data)
            return response

    def post(self, link, data=''):
        if self.checkValid(self.session):
            response = self.session.post(link, data=data)
            return response

    @staticmethod
    def checkValid(session):
        if "$('.vkvk').attr('url', 'https://oauth.vk.com/authorize" in session.get('https://rivalregions.com/').text:
            return 0
        return 1

    @staticmethod
    def makeSession():
        try:
            session = requests.Session()
            session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                              '(KHTML, like Gecko) Chrome/81.0.4044.142 Safari/537.36'})
            session.cookies.update(cookiesNair)
            return session
        except IndexError:
            api.send('Беды с доступом к РР')
            return 0


class HandlerMoe(object):
    def __init__(self):
        self.session = self.makeSession()

    def get(self, link, data=''):
        if self.checkValid(self.session):
            response = self.session.get(link, data=data)
            return response

    def post(self, link, data=''):
        if self.checkValid(self.session):
            response = self.session.post(link, data=data)
            return response

    @staticmethod
    def checkValid(session):
        if "$('.vkvk').attr('url', 'https://oauth.vk.com/authorize" in session.get('https://rivalregions.com/').text:
            return 0
        return 1

    @staticmethod
    def makeSession():
        try:
            session = requests.Session()
            proxies = {
                'http': 'http://a',
                'https': 'http://a'
            }
            session.proxies.update(proxies)
            session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                              '(KHTML, like Gecko) Chrome/81.0.4044.142 Safari/537.36'})
            session.cookies.update(cookiesMoe)
            return session
        except IndexError:
            api.send('Беды с доступом к РР')
            return 0


rr = Handler2()
nair = Handler2()
moe = HandlerMoe()


def getAccLocation(acc):
    tree = html.fromstring(rr.get(acc.replace('#', '')).text)
    location = tree.xpath('//div/@action')
    for loc in location:
        if 'map/details' in loc:
            return loc


def getIndex(typeOf):
    text = ''
    response = apiHandler.get('https://api.rivalregions.com/client/v1/getBuildingsNeeded')
    buildings = dict(response.json()[typeOf])
    for key, value in buildings.items():
        text += f'{key}: {value}\n'
    return text


def getIndexOfReg(reg_id, typeOf):
    tree = html.fromstring(rr.get(f'https://rivalregions.com/listed/country/-2/0/{typeOf}', data={'c': c}).text)
    return tree.xpath(f'//tr[@user="{reg_id}"]/td/text()')[1]


def getPricesRss(lang, response=''):
    types = [["3", f'{lang.oil}: '], ["4", f'{lang.ore}: '], ["11", f'{lang.uranium}: '], ["15", f'{lang.diamonds}: '],
             ["21", f'{lang.oxygen}: '], ["24", f'{lang.helium}: '], ["26", f'{lang.rivalium}: '],
             ["13", f'{lang.antiradine}: '], ['25', f'{lang.lss}: ']]
    rr.get(link='https://rivalregions.com/storage', data={'c': CNair})
    for resource in types:
        tree = html.fromstring(rr.post(link=f'https://rivalregions.com/storage/listed/{resource[0]}',
                                       data={'c': CNair}).text)
        price = tree.xpath('//span[@class="storage_buy_summ"]/text()')
        response += resource[1] + price[0] + '\n'
    return response


def getPricesWeapons(lang, response=''):
    types = [["20", f'{lang.rockets}: '], ["2", f'{lang.tanks}: '], ["1", f'{lang.aircrafts}: '],
             ["14", f'{lang.missiles}: '], ["16", f'{lang.bombers}: '], ["18", f'{lang.battleships}: '],
             ["27", f'{lang.drones}: '], ["22", f'{lang.mTanks}: '], ["23", f'{lang.stations}: ']]
    rr.get(link='https://rivalregions.com/storage', data={'c': CNair})
    for resource in types:
        tree = html.fromstring(rr.post(link=f'https://rivalregions.com/storage/listed/{resource[0]}',
                                       data={'c': CNair}).text)
        price = tree.xpath('//span[@class="storage_buy_summ"]/text()')
        response += resource[1] + price[0] + '\n'
    return response


def getPrices(response=None):
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


def getStatePrices(lang, response=''):
    types = [['1000', f'{lang.gold}: '], ["1003", f'{lang.oil}: '], ["1004", f'{lang.ore}: '],
             ["1011", f'{lang.uranium}: '], ["1015", f'{lang.diamonds}: ']]
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
        for building in buildings:
            if building == ' ✘ ':
                buildings.remove(' ✘ ')
            if building == ' ✔ ':
                buildings.remove(' ✔ ')
        electricity = countElectricity(buildings[:-1])
        damage = tree2.xpath(f'//span[@action="listed/damage"]/text()')
        tree = html.fromstring(rr.get('https://rivalregions.com/listed/country/-2/0/homes', data={'c': c}).text)
        return [tree.xpath(f'//tr[@user="{regId}"]/td/text()'), damage, electricity, buildings]
    return None


def getRegionName(reg):
    reg_id = int(re.search("(\\d+)", reg).group(1))
    tree = html.fromstring(
        rr.get('https://rivalregions.com/listed/country/-2/0/homes', data={'c': CNair}).text)
    return tree.xpath(f'//tr[@user="{reg_id}"]/td/text()')[0]


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
    name = list(name)
    for i in range(len(name)):
        if ord(name[i]) == 160:
            name[i] = ' '
    name = ''.join(name)
    tree = html.fromstring(rr.get('https://rivalregions.com/listed/country/-2/0/school', data={'c': c}).text)
    print(tree.xpath(f'.//td[starts-with(text(),"{str(name)}")]'))
    return re.search("(\\d+)", tree.xpath(f'.//td[starts-with(text(),"{str(name)}")]')[0].attrib['action']).group(0)


def getNameById(_id):
    tree = html.fromstring(rr.get(f'https://rivalregions.com/listed/country/-2/0/school', data={'c': c}).text)
    return tree.xpath(f'//tr[@user="{_id}"]/td/text()')[0]


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


def getDiscount(link):
    if 'profile' not in link:
        link = f'https://rivalregions.com/slide/profile/{link}'
    tree = html.fromstring(rr.get(link.replace('m.', '').replace('#', '')).text)
    library = re.search("(\\d+)", tree.xpath('//span[@action="listed/houses/2"]/text()')[0]).group(1)
    residency = int(getIndexOfReg(getIdByName(str(tree.xpath('//span[@class="dot"]/text()')[1]).replace(' ', ' ')),
                                  'school'))
    return int(residency), int(library)


def getProfileById(_id):
    tree = html.fromstring(rr.get(f'https://rivalregions.com/slide/profile/{_id}').text)
    nick = tree.xpath('//h1[@class="white hide_for_name"]/text()')[0].split('Профиль: ')[1]
    if ']' in nick:
        nick = nick.split('] ')[1]
    return nick


def getLevelById(_id):
    tree = html.fromstring(rr.get(f'https://rivalregions.com/slide/profile/{_id}').text)
    return (re.search(r'\d+',
                      tree.xpath('//div[@style="position: absolute; width: 200px; text-align: center;"]/text()')[
                          0]).group(0))


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
    # response = list(map(lambda x: re.search("\d+", x[0]).group(0), response))
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


def getResidents(reg_id):
    residents = []
    links = html.fromstring(rr.get(f'https://rivalregions.com/listed/residency/{reg_id}/0/0',
                                   data={'c': c}).text).xpath('//tr')[1:]
    for i in range(25, 1000, 25):
        residents.extend([resident.attrib['user'] for resident in links])
        try:
            links = html.fromstring(rr.get(f'https://rivalregions.com/listed/residency/{reg_id}/0/{i}',
                                           data={'c': c}).text).xpath('//tr')
        except etree.ParserError as e:
            print(e, 123)
            return residents
    return residents


async def getPopulationOfReg(reg_id, pop):
    async with aiohttp.ClientSession(cookies=cookies) as asyncRR:
        try:
            population = []
            response = await asyncRR.get(f'https://rivalregions.com/listed/region/{reg_id}/0/0', data={'c': c})
            links = html.fromstring(await response.text()).xpath('//tr')[1:]
            population.extend([resident.attrib['user'] for resident in links])
            for i in range(25, pop, 25):
                try:
                    await asyncio.sleep(0.1)
                    response = await asyncRR.get(f'https://rivalregions.com/listed/region/{reg_id}/0/{i}',
                                                 data={'c': c})
                    links = html.fromstring(await response.text()).xpath('//tr')
                    population.extend([resident.attrib['user'] for resident in links])
                except etree.ParserError:
                    if pop > 25 and len(population) <= 25:
                        await asyncio.sleep(0.1)
                        return await getPopulationOfReg(reg_id, pop)
                    else:
                        return population
        except etree.ParserError as e:
            print('gpor', e)
            time.sleep(0.1)
            return await getPopulationOfReg(reg_id, pop)
        return population


async def getPopulationOfState(state_id):
    table = etree.HTML(rr.get(f'https://rivalregions.com/info/regions/{state_id}').text).find("body/table")
    rows = iter(table)
    next(rows)
    regions: dict = {}
    tasks = []
    for row in rows:
        link = row[0][0].attrib['href']
        number = int(row[2].text)
        task = asyncio.ensure_future(getPopulationOfReg(re.search(r'\d+', link).group(0), number))
        tasks.append(task)
        regions.update({link: 0})
    pops = await asyncio.gather(*tasks)
    keys = list(regions.keys())
    for i in range(len(pops)):
        if pops[i] != etree.ParserError('Document is empty') and len(pops[i]) != 0:
            regions[keys[i]] = pops[i]
        else:
            regions[keys[i]] = await getPopulationOfReg(re.search(r'\d+', keys[i]).group(0), 0)
    return regions


def getDelta(previous, current, number):
    def makeLinks(listOfIds):
        return ' '.join(map(lambda x: f'https://rivalregions.com/#slide/profile/{x} '
                                      f'({getProfileById(x)}: {getLevelById(x)})', listOfIds))

    result = {}
    for region, population in previous.items():
        if region in current:
            if len(previous[region]) < len(current[region]) and len(current[region]) - len(previous[region]) >= number:
                name = getNameById(re.search(r'\d+', region).group(0))
                result.update({f'{region} ({name})': [len(current[region]) - len((previous[region])),
                                                      makeLinks(list(set(current[region]) - set(previous[region])))]})
    return result


def getWarsForBot(state_id):
    try:
        if len(rr.get(f'https://rivalregions.com/war/bloc/{state_id}', data={'c': c}).text) != 0:
            tree = html.fromstring(rr.get(f'https://rivalregions.com/war/bloc/{state_id}', data={'c': CNair}).text)
            remaining = list(map(int, list(filter(lambda size: len(size) <= 6,
                                                  re.findall('countdown\(\{until: (\\d+),', rr.get(
                                                      f'https://rivalregions.com/war/bloc/{state_id}',
                                                      data={'c': CNair}).text)))))
            if len(remaining) and min(remaining) > 3600 * 23.8:
                print(remaining)
                return tree.xpath('//td/@action')[3::4]
            return []
        return []
    except Exception as e:
        print('gwfb', e)
        time.sleep(0.5)
        return getWarsForBot(state_id)


def getWarsDelta(previous, current):
    if len(current) > len(previous):
        return current[-(len(current) - len(previous)):]
    return []


def getCurrentDeps(typeOf):
    tree = html.fromstring(nair.get(f'https://rivalregions.com/listed/institutes/{typeOf}').text)
    greatArm = tree.xpath('//tr[@user="3715"]/td[@rat]')[0].attrib['rat']
    return greatArm


def parseDeps(state, dep_id, limit):
    response = apiHandler.get(
        f'https://api.rivalregions.com/client/v1/getDepartmentsLog?stateId={state}&depId={dep_id}')
    accs = response.json()[state][dep_id]
    for acc in accs:
        stamp = acc['time']
        amount = acc['n']
        accId = acc['id']
        if not db.isInDep(accId, stamp) and amount == '10' and not accId in db.getBlacklist():
            if int(getCurrentDeps(dep_id)) <= limit + 10:
                time.sleep(1)
                db.addDepAcc(accId, stamp, 100 + int(dep_id), getCurrentDeps(dep_id))
                nair.post('https://rivalregions.com/storage/donate',
                          data={'whom': accId, 'type': '0', 'c': CNair,
                                'n': '50000000000'})
                print('sent', accId)
                api.send(0, f'sent to {accId} with ts {stamp} at dep {dep_id}', 160819338)
            else:
                db.addDepAcc(accId, stamp, dep_id, getCurrentDeps(dep_id))
            time.sleep(2)


def goldExplorations():
    moe.post('https://rivalregions.com/parliament/donew/42/0/0', data={'tmp_gov': '0', 'c': cMoe})
    time.sleep(5)
    moe.post('https://rivalregions.com/parliament/donew/42/3/0', data={'tmp_gov': '0', 'c': cMoe})
    time.sleep(5)
    moe.post('https://rivalregions.com/parliament/donew/42/11/0', data={'tmp_gov': '0', 'c': cMoe})
    time.sleep(5)
    moe.post('https://rivalregions.com/parliament/donew/42/4/0', data={'tmp_gov': '0', 'c': cMoe})
    time.sleep(5)
    moe.post('https://rivalregions.com/parliament/donew/42/15/0', data={'tmp_gov': '0', 'c': cMoe})


def getMoney():
    tree = html.fromstring(nair.get('https://rivalregions.com#overview').text)
    response = tree.xpath('//span[@id="m"]/text()')[0]
    return response.replace('.', '')


def marketBot(typeOf, maxPrice):
    tree = html.fromstring(nair.get(f'http://rivalregions.com/storage/listed/{typeOf}/').text)
    offers = tree.xpath('//tr')
    for offer in offers[1:]:
        user = offer.attrib['user']
        amount = str(int(offer[3].attrib['rat']))
        price = offer[4].attrib['rat']
        intPrice = int(price.split('.')[0])
        if intPrice > maxPrice:
            break
        if intPrice < maxPrice and int(getMoney()) > 30 * 10 ** 12:
            print(price)
            resp = len(nair.post(f'http://rivalregions.com/storage/buy/{typeOf}/{user}/{str(amount)}/{price}',
                                 data={'c': CNair}).text)
            if resp > 10:
                time.sleep(0.5)
                nair.post('http://rivalregions.com/storage/donate',
                          data={'c': CNair, 'type': typeOf, 'n': amount, 'whom':
                              '16011.1'})


def getAllIds():
    ids = []
    for i in range(0, 10000, 25):
        tree = html.fromstring(rr.get(f'https://rivalregions.com/listed/region/0/0/{i}').text)
        accsTable = tree.xpath('//tbody[@id="list_tbody"]')[0] if i == 0 else tree
        for acc in accsTable:
            ids.append(acc.attrib['user'])
    return ids


def sellerBot(typeOf, minPrice):
    while True:
        tree = html.fromstring(rr.get(f'http://rivalregions.com/storage/listed/{typeOf}/').text)
        offers = tree.xpath('//tr')
        offer = offers[1]
        user = offer.attrib['user']
        price = offer[4].attrib['rat']
        intPrice = int(price.split('.')[0]) + ((int(price.split('.')[1]) / 10) if len(price.split('.')) > 1 else 0)
        print(intPrice)
        if intPrice < minPrice:
            time.sleep(10)
            pass
        elif user != '160819338':
            rr.post(f'https://rivalregions.com/storage/newsell/2/4388571/{intPrice - 0.1}', data={'c': c})
            time.sleep(300)
        else:
            time.sleep(10)


def getAllWarParticipants(war, side):
    response = []
    tree = html.fromstring(rr.get(f'https://rivalregions.com/war/damage/{war}/{side}/').text)
    for acc in tree.xpath('//tr')[1:]:
        response.append(f"https://rivalregions.com/#slide/profile/{acc.attrib['user']}")
    return response


def getPartyWage(party):
    tree = html.fromstring(rr.get(f'https://rivalregions.com/slide/party/{party}').text)
    wage = int(int(re.search(r'\d+', tree.xpath('//div[@class="float_left imp yellow"]/text()')[0]).group(0)) / 20)
    if wage:
        return wage
    else:
        return int(re.search(r'\d+', tree.xpath('//div[@class="float_left"]/text()')[0]).group(0))


def getStateRegionsAmount(state):
    tree = html.fromstring(rr.get(f'http://rivalregions.com/info/regions/{state}').text).find("body/table")
    rows = iter(tree)
    next(rows)
    return len(list(rows))


def makeDeep():
    moe.post('https://rivalregions.com/parliament/donew/34/15_14/1', data={'c': cMoe, 'tmp_gov': '15_14'})
    time.sleep(5)






