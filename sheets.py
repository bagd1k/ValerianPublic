from pygsheets import *
import rr
import time

google = authorize()


def fillPerks():
    for name in ['Ordo Inquisition', 'Редукс Систем Кригсссссс!']:
        sheet = google.open(name)
        if name == 'Ordo Inquisition':
            table = sheet.worksheet('title', 'testy')
            accounts = rr.parseParties([284108, 295076])
            table.clear('A2', 'A200', 'userEnteredValue')
            table.clear('E2', 'H200', 'userEnteredValue')
            links = list(map(lambda acc: [f'=HYPERLINK("{acc[0]}"; "{acc[1]}")'], accounts))
            stats = list(map(lambda acc: acc[2:6], accounts))
            table.update_values(f'A2:A{len(accounts) + 2}', links)
            table.update_values(f'E2:H{len(accounts) + 2}', stats)
        # elif name == 'Редукс Систем Кригсссссс!':
        #     for number in range(4, 36):
        #         table = sheet.worksheet('title', 'Первая Бригада')
        #         try:
        #             link = table.cell(f'D{number}').formula.split('("')[1].split('"')[0]
        #         except IndexError:
        #             print(number)
        #             continue
        #         parsed = rr.getProfileById(link.replace("#", ''))
        #         print(parsed)
        #         table.update_values(crange=f'H{number}:K{number}', values=[parsed[2:]])
        #         table.update_value(f'D{number}', f'=HYPERLINK("{link}"; "{parsed[0]}")')
        #     print()
        #     return 0
    time.sleep(60*60*24)
    return fillPerks()
