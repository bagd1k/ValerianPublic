from pygsheets import *
import rr
import time

google = authorize()


def fillPerks():
    for name in ['2', '2']:
        sheet = google.open(name)
        if name == 'Ordo Inquisition':
            table = sheet.worksheet('title', 'testy')
            accounts = rr.parseParties([1, 2])
            table.clear('A2', 'A200', 'userEnteredValue')
            table.clear('E2', 'H200', 'userEnteredValue')
            links = list(map(lambda acc: [f'=HYPERLINK("{acc[0]}"; "{acc[1]}")'], accounts))
            stats = list(map(lambda acc: acc[2:6], accounts))
            table.update_values(f'A2:A{len(accounts) + 2}', links)
            table.update_values(f'E2:H{len(accounts) + 2}', stats)
    time.sleep(60*60*24)
    return fillPerks()
