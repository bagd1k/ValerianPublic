# -*- coding: utf-8 -*-

from pymongo import *
import api


db = MongoClient("mongodb+srv://bot:vasyA228@marine-ozyeg.mongodb.net/Marine?retryWrites=true&w=majority").Valerian

governors = db.Governors
deputies = db.Deputies
accounts = db.Accounts
people = db.People
queue = db.Queue
tasks = db.Tasks
time = db.Time
wars = db.Wars
users = db.Users


class Proxy(object):
    def __init__(self, proxy):
        self.http = f'http://{proxy}/'
        self.https = f'https://{proxy}/'


def addGovernor(user_id):
    governors.insert_one({'id': user_id, 'regions': []})


def getGovernors():
    ids = []
    [ids.append(governor['id']) for governor in governors.find(projection={'_id': False, 'id': True})]
    return ids


def addRegToGovernor(user_id, reg_id):
    if str(user_id) not in getGovernors():
        addGovernor(str(user_id))
    governors.update_one({'id': str(user_id)}, {'$addToSet': {'regions': {'$each': [reg_id]}}})


def getGovernorRegions(user_id):
    return governors.find_one({'id': str(user_id)})['regions']


def addAccount(user_id, data):
    if user_id not in getHolders():
        accounts.insert_one({'id': user_id})
    accounts.update_one({'id': user_id}, {'$set': {data[0]:
                                                       {'pass': data[1], 'proxy': Proxy(data[2]).__dict__,
                                                        'cookies': '', 'vk_cookies': '', 'c': ''}}})
    api.send('Ваш аккаунт внесён!', user_id)


def getAcc(user_id):
    ids = []
    [ids.append(x['_id']) for x in accounts.find(projection={'_id': True})]
    for _id in ids:
        if user_id in accounts.find_one({'_id': _id}):
            info = accounts.find_one({'_id': _id})[user_id]
            return user_id, info['pass'], info['proxy'], info['cookies'], info['vk_cookies'], _id, info['c']


def addTask(task, login):
    tasks.insert_one({'type': task, 'login': login})


def addToTime(user_id):
    time.insert_one({'user_id': user_id})


def isWaits(user_id):
    ids = []
    [ids.append(user['user_id']) for user in time.find(projection={'_id': False, 'user_id': True})]
    if user_id in ids:
        time.delete_one({'user_id': user_id})
        return True
    return False


def saveSession(cookies, login, _id):
    accounts.update_one({'_id': _id}, {'$set': {f'{login}.cookies': cookies}})


def saveVk(cookies, login, _id):
    accounts.update_one({'_id': _id}, {'$set': {f'{login}.vk_cookies': cookies}})


def getAccounts():
    ids = []
    [ids.append(user) for user in accounts.find(projection={'_id': False, 'id': False, 'cookies': False})]
    return list(map(lambda _id: [*_id], ids))


def getHolders():
    ids = []
    [ids.append(user['id']) for user in accounts.find()]
    return ids


def getAllAccountsByHolder(user_id):
    response = 'Список аккаунтов:\n'
    i = 1
    for login in accounts.find_one({'id': user_id}):
        if login not in ['id', '_id']:
            response += f'{i}: {login}\n'
            i += 1
    return response


def insertC(login, _c):
    for user_id in getHolders():
        if login in getAllAccountsByHolder(user_id):
            accounts.update_one({'id': user_id}, {'$set': {f'{login}.c': _c}})


def addUser(source, _id, profile):
    if not isUser(source, _id):
        if source == 'vk':
            users.insert_one({'vk_id': _id, 'tg_id': None, 'profile': profile})
            return 1
    else:
        if source == 'vk':
            users.update_one({'vk_id': _id}, {'$set': {'tg_id': None, 'profile': profile}})
            return 2


def isUser(source, _id):
    if source == 'vk':
        ids = []
        [ids.append(user['vk_id']) for user in users.find()]
        return _id in ids


def getProfile(source, _id):
    if source == 'vk':
        user = users.find({'vk_id': _id})[0]
        if 'profile' in user:
            return user['profile']
        return None


def saveLogs(event):
    return 0







