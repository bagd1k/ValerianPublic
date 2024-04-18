import api
import rr
import re


def formatIncomes(data, chat_id):
    response = 'Доходы за сегодня:\n'
    for res in data[2:]:
        response += f'{res}\n'
    try:
        return api.send(0, text=response, domain=chat_id)
    except Exception as e:
        print(e)
        pass


def governorInfo(region, response='', full=False):
    regex = "(\\d+)"
    if region is None:
        return 'Error'
    if region[0][1] != '1':
        response += f'{region[0][0]}\nИндекс ЖФ: {region[0][1]}\n'
    else:
        response += f'{region[0][0]}\nИндекс ЖФ: {region[0][1]} \nДо жёлтой зоны ещё  \
               {str(rr.getRedBorder() - int(re.search(regex, region[3][-1]).group(1)))}  ЖФ\n'
    response += f'Начальный урон:\nАтаки: {region[1][0]}\nДефа: {region[1][1]}\n'
    response += f'Электра: {"+" if region[2] > 0 else ""}{region[2]}\n\n'
    if full:
        for build in region[3]:
            response += f'{build}\n'
    return response


def formatIndexes(response, typeOf):
    print(response)
    indexes = list(response.values())[0]
    response = f'{typeOf}\n'
    for num, index in indexes.items():
        response += f'{num}: {index}\n'
    return response


def formatPricesWp(goods: dict, response='Цены без учёта доставки!\n'):
    for good, price in goods.items():
        response += f'{good}: {price}\n'
    return response


def formDeep(rss):
    response = 'ГР будет стоить:\n'
    response += f'{rss[0]/10**9}kkk R \n'
    response += f'{rss[1]/10**9}kkk G \n'
    response += f'{rss[2]} pcs \n'
    return response
