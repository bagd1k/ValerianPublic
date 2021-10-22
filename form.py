import api
import rr
import re


def formatIncomes(data, _id):
    response = 'Доходы за сегодня:\n'
    for res in data[2:]:
        response += f'{res}\n'
    if _id == 2:
        return api.send(response, 2000000008)
    if _id == 301:
        return api.send(response, 2000000006)


def governorInfo(region, response='', full = False):
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


def formatIndexes(response: dict, typeOf):
    indexes: dict = list(response.values())[0]
    response = f'{typeOf}\n'
    for num, index in indexes.items():
        response += f'{num}: {index}\n'
    return response


