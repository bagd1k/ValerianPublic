import api
import threading
import telebot
import sheets
import form
import rr
import schedule
import time


def VkListen():
    while True:
        try:
            for event in api.longpoll.listen():
                api.fetcher(api.formObject('vk', event))
        except Exception as e:
            print(e)
            pass


def TgListen():
    bot = telebot.TeleBot('1612340554:AAEnAQPOk1_JkwwKLBtHTbjrpTVxF_9khho')

    def handle_messages(messages):
        for message in messages:
            try:
                api.fetcher(api.formObject('tg', message))
            except Exception as e:
                print(e)
                pass

    bot.set_update_listener(handle_messages)
    bot.polling()


def earningsThread():
    threading.Thread(target=form.formatIncomes, args=(rr.getStateEarnings(2), 2)).start()
    threading.Thread(target=form.formatIncomes, args=(rr.getStateEarnings(301), 301)).start()


def scheduleThread():
    while 1:
        schedule.run_pending()
        time.sleep(1)


schedule.every().day.at("17:55").do(earningsThread)


vk = threading.Thread(target=VkListen).start()
tg = threading.Thread(target=TgListen).start()
tasks = threading.Thread(target=api.doTasks).start()
rareTasks = threading.Thread(target=api.doRareTasks).start()
perks = threading.Thread(target=sheets.fillPerks).start()
sched = threading.Thread(target=scheduleThread).start()



