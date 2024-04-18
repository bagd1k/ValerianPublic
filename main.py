import api
import threading
import db
import form
import rr
import time
import schedule


def VkListen():
    while True:
        try:
            for event in api.longpoll.listen():
                api.fetcher(api.formObject('vk', event))
        except Exception as e:
            print(e)
            pass


def deps():
    while True:
        try:
            rr.parseDeps('1', '2', 6500)
            time.sleep(15)
        except Exception as e:
            print(e, 1005)
            time.sleep(15)
            pass


def depsBuildings():
    while True:
        try:
            rr.parseDeps('1', '1', 4000)
            time.sleep(15)
        except Exception as e:
            print(e, 1000)
            time.sleep(15)
            pass


def depsTanks():
    while True:
        try:
            rr.parseDeps('1', '9', 3000)
            time.sleep(15)
        except Exception as e:
            print(e, 1001)
            time.sleep(15)
            pass


def depsFleet():
    while True:
        try:
            rr.parseDeps('1', '11', 1200)
            time.sleep(15)
        except Exception as e:
            print(e, 1002)
            time.sleep(15)
            pass


def depsOil():
    while True:
        try:
            rr.parseDeps('1', '3', 6500)
            time.sleep(15)
        except Exception as e:
            print(e, 1003)
            time.sleep(15)
            pass


def depsUranium():
    while True:
        try:
            rr.parseDeps('1', '6', 1000)
            time.sleep(15)
        except Exception as e:
            print(e, 1004)
            time.sleep(15)
            pass


def depsDiamond():
    while True:
        try:
            rr.parseDeps('1', '5', 1200)
            time.sleep(15)
        except Exception as e:
            print(e, 1010)
            time.sleep(15)
            pass


def explore():
    while True:
        try:
            rr.goldExplorations()
            time.sleep(60*30)
        except Exception as e:
            print(e, 1006)
            pass


def market():
    while True:
        try:
            rr.marketBot(3, 150)
            time.sleep(3)
        except Exception:
            pass


def market2():
    while True:
        try:
            rr.marketBot(4, 145)
            time.sleep(3)
        except Exception:
            pass


def seller():
    rr.sellerBot(2, 6000)


def earningsThread():
    for stateEarn in db.getEarnings():
        form.formatIncomes(rr.getStateEarnings(stateEarn['id']), stateEarn['chat_id'])


def threadToRun():
    while True:
        schedule.run_pending()
        time.sleep(1)


schedule.every().day.at('20:55').do(earningsThread)
# threading.Thread(target=api.traceAccs, args=(db.getAccsToTrace(), )).start()
threading.Thread(target=VkListen).start()
threading.Thread(target=deps).start()
time.sleep(3)
threading.Thread(target=depsBuildings).start()
time.sleep(3)
threading.Thread(target=depsTanks).start()
time.sleep(3)
threading.Thread(target=depsFleet).start()
time.sleep(3)
threading.Thread(target=depsOil).start()
time.sleep(3)
threading.Thread(target=depsUranium).start()
time.sleep(3)
threading.Thread(target=depsDiamond).start()
time.sleep(3)
# threading.Thread(target=explore).start()  
# threading.Thread(target=market).start()
# threading.Thread(target=market2).start()
threading.Thread(target=threadToRun).start()
# threading.Thread(target=seller).start()
threadsWar = {}
# for state in [763]:
#     threadsWar.update({state: threading.Thread(target=api.warParser, args=(state, 10))})
#     threadsWar[state].start()



