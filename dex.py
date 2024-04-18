import datetime
import math

import rr


def mathRound(num):
    return int(num + (0.5 if num > 0 else -0.5))


def getPrice(typeOf, before, now, forBot=False):
    cash = gold = oil = ore = diamonds = uranium = 0
    if typeOf in ['медка', 'вб', 'школа']:
        for x in range(before, now):
            cash += (300*(x+1)) ** 1.5
            gold += (2160*(x+1)) ** 1.5
            oil += (160*(x+1)) ** 1.5
            ore += (90*(x+1)) ** 1.5
    elif typeOf in ['пво', 'порт', 'аэро']:
        for x in range(before, now):
            cash += (1000*(x+1)) ** 1.5
            gold += (180*(x+1)) ** 1.5
            oil += (10*(x+1)) ** 1.5
            ore += (10*(x+1)) ** 1.5
            diamonds += (10*(x+1)) ** 0.7
    elif typeOf in ['эс', 'электра']:
        for x in range(before, now):
            cash += (2000*(x+1)) ** 1.5
            gold += (90*(x+1)) ** 1.5
            oil += (25*(x+1)) ** 1.5
            ore += (25*(x+1)) ** 1.5
            diamonds += (5*(x+1)) ** 0.7
            uranium += (20*(x+1)) ** 1.5
    elif typeOf in ['космо']:
        for x in range(before, now):
            cash += (6000*(x+1)) ** 1.5
            gold += (180*(x+1)) ** 1.5
            oil += (10*(x+1)) ** 1.5
            ore += (25*(x+1)) ** 1.5
            diamonds += (10*(x+1)) ** 0.7
            uranium += (30*(x+1)) ** 1.5
    elif typeOf in ['жф']:
        for x in range(before, now):
            cash += (30*(x+1)) ** 1.5
            gold += (216*(x+1)) ** 1.5
            oil += (16*(x+1)) ** 1.5
            ore += (9*(x+1)) ** 1.5
    result = f'Постройка здания "{typeOf}" с {before} до {now} будет  стоить:\n'

    def addDots(number, n=3):
        number = str(number)[::-1]
        return ('.'.join(number[i:i + n] for i in range(0, len(number), n)))[::-1]

    result2 = []
    for res in [[cash, 'R'], [gold, 'G'], [oil, 'bbl'], [ore, 'kg'], [diamonds, 'pcs'],  [uranium, 'g']]:
        result += f'{addDots(round(res[0]))} {res[1]}\n' if res[0] != 0 else ''
        result2.append(round(res[0]))
    return result if not forBot else result2


def getPerksPrice(before, now):
    response = 0
    for level in range(before, now):
        response += mathRound(level / 10) * 10 + 10
    return f'Прокачка от {before} навыка до {now} будет стоить {response} G'


def getPerksTime(before, now, discount):
    time = 0
    const = ((1-(discount[0] if discount[0] != 11 else 20)/50)*0.72)
    for i in range(before+1, now+1):
        multi = 1
        if now <= 100:
            multi = 2
        elif now <= 50:
            multi = 4
        time += const*(i**2)/multi
    return f'И займёт {str(datetime.timedelta(seconds=round(time * (1-discount[1]/100) * (100 / 200))))}'


def getFactory(before, now):
    price = int((before*5+now*5+5)*((now-before)/2)) + (495 if before == 0 else 0)
    return f'Прокачка от {before} уровня фабы до {now} будет стоить {price} G'


def countCbHouses(border, typeOf,  start):
    cash = 0
    start = int(start)
    if typeOf in ['Военная база', 'Госпиталь', 'Школа']:
        while cash < border:
            cash += (300 * (start + 1)) ** 1.5
            start += 1
    elif typeOf in ['ПВО', 'Порт', 'Аэропорт']:
        while cash < border:
            cash += (1000 * (start + 1)) ** 1.5
            start += 1
    elif typeOf in ['Электростанция']:
        while cash < border:
            cash += (2000 * (start + 1)) ** 1.5
            start += 1
    elif typeOf in ['Космодром']:
        while cash < border:
            cash += (6000 * (start + 1)) ** 1.55
            start += 1
    elif typeOf in ['Жилой фонд']:
        while cash < border:
            cash += (30 * (start + 1)) ** 1.5
            start += 1
    return start


def countBuildsForDamage(regions, required, prices):

    types = {1: 'медка', 2: 'вб', 3: 'школа', 4: 'пво', 5: 'порт', 6: 'эс', 7: 'космо', 8: 'аэро'}
    greatSum = 0
    rss = [0, 0, 0, 0, 0, 0]
    for region in regions:
        final = {}
        summa = 0
        if region[1] >= required:
            continue
        else:
            while region[1] < required:
                resources = getPrice('вб', region[3], region[3]+1, forBot=True)
                less = sum(map(lambda n: int(n[1]) * int(prices[n[0]]), enumerate(resources[2:]))) + resources[0]
                less1 = 100*10**12
                for i, building in enumerate(region[2:], start=1):
                    for j, build in enumerate(region[2:], start=1):
                        if i == 2 or j == 2 or building == 0 or build == 0:
                            continue
                        if i == j:
                            build += 1
                        resources = getPrice(types[i], building, building+1, forBot=True)
                        less2 = sum(map(lambda n: int(n[1]) * int(prices[n[0]]), enumerate(resources[2:]))) + resources[0]
                        resources = getPrice(types[j], build, build+1, forBot=True)
                        less2 += sum(map(lambda n: int(n[1]) * int(prices[n[0]]), enumerate(resources[2:]))) + resources[0]
                        if less2 < less1:
                            less1 = less2
                            min1 = i
                            min2 = j
                if less > less1:
                    for el in resources:
                        for elem in rss:
                            elem += el
                    less = less1
                    final[types[min1]] = final.setdefault(types[min1], 0) + 1
                    final[types[min2]] = final.setdefault(types[min2], 0) + 1
                    region[min1+1] += 1
                    region[min2+1] += 1
                else:
                    for el in resources:
                        for elem in rss:
                            elem += el
                    final[types[2]] = final.setdefault(types[2], 0) + 1
                    region[3] += 1
                summa += less
                region[1] += 100000
        greatSum += summa
        print(sum(list(final.values())))
        print(region[0], final, summa)
    print(greatSum)
    print(rss)
    return greatSum


def countMostIncome(level, salary, index):
    prod = 0.2 * (100 ** 0.8) * ((index / 10)**0.8) * (level ** 0.8) * ((100000 / 10) ** 0.6) * salary/100
    print(prod)


def deepExploration(base, target, typeOf):
    multiplier = 0
    cash = 0
    gold = 0
    diamond = 0
    if typeOf == 'голд':
        multiplier = 4
    elif typeOf == 'уран':
        multiplier = 40
    elif typeOf in ['алые', 'алмазы']:
        multiplier = 70
    elif typeOf == 'нефть':
        multiplier = 4
    elif typeOf == 'руда':
        multiplier = 5
    for i in range(1, target + 1 - base):
        tmp = math.ceil(
            multiplier * (base + i) * 50000
        )
        cash += math.ceil(tmp * 0.95)
        gold += math.ceil(tmp * 2)
        diamond += math.ceil(tmp * 1.0E-5)
    return [cash, gold, diamond]




