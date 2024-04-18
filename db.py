# -*- coding: utf-8 -*-

from pymongo import *

db = MongoClient("mongodb://localhost:27017/Valerian?retryWrites=true&w=majority").Valerian

governors = db.Governors
accounts = db.Accounts
people = db.People
queue = db.Queue
tasks = db.Tasks
time = db.Time
wars = db.Wars
users = db.Users
langs = db.Langs
mailings = db.Mailings
chats = db.Chats
earnings = db.Earnings
groups = db.Groups
accs = db.Accs
deps = db.Deps
marriages = db.Marriages
taxes = db.Taxes
blacklistDeps = db.blacklistDeps


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
    if reg_id not in getGovernorRegions(user_id):
        governors.update_one({'id': str(user_id)}, {'$addToSet': {'regions': {'$each': [reg_id]}}})
        return True
    governors.update_one({'id': str(user_id)}, {'$pull': {'regions': str(reg_id)}})
    return False


def getGovernorRegions(user_id):
    return governors.find_one({'id': str(user_id)})['regions']


def addToTime(user_id):
    time.insert_one({'user_id': user_id})


def isWaits(user_id):
    return bool(time.count_documents({'user_id': user_id}, limit=1))


def removeWaiting(user_id):
    time.delete_one({'user_id': user_id})


def addUser(source, _id, profile):
    if not isUser(source, _id):
        if source == 'vk':
            users.insert_one({'vk_id': _id, 'tg_id': None, 'profile': profile})
            return 1
        if source == 'tg':
            users.insert_one({'vk_id': None, 'tg_id': _id, 'profile': profile})
            return 1
    else:
        if source == 'vk':
            users.update_one({'vk_id': _id}, {'$set': {'tg_id': None, 'profile': profile}})
            return 2
        if source == 'tg':
            users.insert_one({'vk_id': None, 'tg_id': _id, 'profile': profile})
            return 2


def isUser(source, _id):
    _id = int(_id)
    if source == 'vk':
        ids = []
        [ids.append(user['vk_id']) for user in users.find()]
        return _id in ids
    if source == 'tg':
        ids = []
        [ids.append(user['tg_id']) for user in users.find()]
        return _id in ids


def getProfile(source, _id):
    if source == 'vk':
        user = users.find({'vk_id': _id})[0]
        if 'profile' in user:
            return user['profile']
        return None
    if source == 'tg':
        user = users.find({'tg_id': _id})[0]
        if 'profile' in user:
            return user['profile']
        return None


def addLangUser(source, _id, lang):
    if not isLangUser(source, _id):
        if source == 'vk':
            langs.insert_one({'vk_id': _id, 'tg_id': None, 'lang': lang})
            return 1
        if source == 'tg':
            langs.insert_one({'vk_id': None, 'tg_id': _id, 'lang': lang})
            return 1
    else:
        if source == 'vk':
            langs.update_one({'vk_id': _id}, {'$set': {'tg_id': None, 'lang': lang}})
            return 2
        if source == 'tg':
            langs.update_one({'tg_id': _id}, {'$set': {'vk_id': None, 'lang': lang}})
            return 2


def isLangUser(source, user_id):
    if source == 'vk':
        ids = []
        [ids.append(user['vk_id']) for user in langs.find()]
        return user_id in ids
    if source == 'tg':
        ids = []
        [ids.append(user['tg_id']) for user in langs.find()]
        return user_id in ids


def getLang(source, user_id):
    if source == 'vk':
        user = langs.find({'vk_id': user_id})[0]
        if 'lang' in user:
            return user['lang']
        return None
    if source == 'tg':
        user = langs.find({'tg_id': user_id})[0]
        if 'lang' in user:
            return user['lang']
        return None


def createMailing(user_id, accessCode, tag):
    mailings.insert_one({'owners': [user_id], 'code': accessCode, 'tag': tag, 'members': [user_id]})


def addUserToMailing(user_id, accessCode):
    if user_id in mailings.find_one({'code': accessCode})['members']:
        mailings.update_one({'code': accessCode}, {'$pull': {'members': user_id}})
        return False
    mailings.update_one({'code': accessCode}, {'$addToSet': {'members': {'$each': [user_id]}}})
    return True


def getMailingTags():
    tags = []
    [tags.append(mailing['tag']) for mailing in mailings.find(projection={'_id': False, 'tag': True})]
    return tags


def isTagExists(tag):
    if tag in getMailingTags():
        return True
    return False


def getMembersByTag(tag):
    return mailings.find_one({'tag': tag})['members']


def isCodeExists(code):
    codes = []
    [codes.append(mailing['code']) for mailing in mailings.find(projection={'_id': False, 'code': True})]
    if code in codes:
        return True
    return False


def getMailingOwners(tag):
    return mailings.find_one({'tag': tag})['owners']


def addOwnerToMailing(user_id, tag):
    if user_id in getMailingOwners(tag):
        mailings.update_one({'id': str(user_id)}, {'$pull': {'owners': str(user_id)}})
        return False
    mailings.update_one({'tag': tag}, {'$addToSet': {'owners': {'$each': [user_id]}}})
    return True


def addChat(chat_id):
    chats.insert_one({'id': chat_id, 'greeting': None, 'muted': []})


def isChatExists(chat_id):
    chatIds = []
    [chatIds.append(chat['id']) for chat in chats.find(projection={'_id': False, 'id': True})]
    return chat_id in chatIds


def muteUser(user_id, chat_id):
    if isMuted(user_id, chat_id):
        chats.update_one({'id': chat_id}, {'$pull': {'muted': user_id}})
        return False
    chats.update_one({'id': chat_id}, {'$addToSet': {'muted': {'$each': [user_id]}}})
    return True


def isMuted(user_id, chat_id):
    if user_id in chats.find_one({'id': chat_id})['muted']:
        return True
    return False


def setGreeting(chat_id, greeting):
    chats.update_one({'id': chat_id}, {'$set': {'greeting': greeting}})


def getGreeting(chat_id):
    return chats.find_one({'id': chat_id})['greeting']


def addEarnings(reg_id, source, chat_id):
    earningsIds = []
    [earningsIds.append(earning['id']) for earning in earnings.find(projection={'_id': False, 'id': True})]
    if reg_id not in earningsIds:
        earnings.insert_one({'id': reg_id, 'source': source, 'chat_id': chat_id})
        return True
    earnings.delete_one({'id': reg_id})
    return False


def getEarnings():
    return earnings.find()


def saveLogs():
    return 0


def addGroup(group_id: int, token: str, response: str):
    groups.insert_one({'group_id': group_id, 'token': token, 'response': response, 'is_verified': False})


def isGroupVerified(group_id: int):
    return groups.find_one({'group_id': group_id})['is_verified']


def verifyGroup(group_id: int):
    groups.update_one({'group_id': group_id}, {'$set': {'is_verified': True}})


def getResponseCode(group_id: int):
    return groups.find_one({'group_id': group_id})['response']


def getToken(group_id: int):
    return groups.find_one({'group_id': group_id})['token']


def updateGroup(group_id: int, token: str, response: str):
    groups.update_one({'group_id': group_id}, {'$set': {'is_verified': False, 'token': token, 'response': response}})


def isGroupExists(group_id: int):
    groupIds = []
    [groupIds.append(group['group_id']) for group in groups.find(projection={'_id': False, 'group_id': True})]
    return group_id in groupIds


def addAccToTrace(acc_id: str):
    accs.insert_one({'acc_id': acc_id})


def getAccsToTrace():
    accIds = []
    for acc in accs.find():
        accIds.append(acc['acc_id'])
    return accIds


def addDepAcc(_id, stamp, typeOf, amount):
    if not isInDep(_id, stamp):
        deps.insert_one({'id': _id, 'stamp': stamp, 'type': typeOf, 'amount': amount})
    else:
        print('1488228')


def isInDep(_id, stamp):
    return deps.find_one({'id': _id, 'stamp': stamp})


def addMarriage(chat_id, firstPartner, secondPartner):
    marriages.insert_one({'chat_id': chat_id, 'firstPartner': firstPartner, 'secondPartner': secondPartner,
                          'is_pending': True})


def getMarriages(chat_id):
    response = []
    for marriage in marriages.find({'chat_id': chat_id}, projection={'_id': False, 'chat_id': False}):
        values = list(marriage.values())
        if not values[2]:
            response.append(values[:2])
    return response


def isMarried(chat_id, user_id):
    response = []
    for marriage in marriages.find({'chat_id': chat_id}, projection={'_id': False, 'chat_id': False}):
        values = list((marriage.values()))
        if not values[2]:
            response.append(values[0])
            response.append(values[1])
    return user_id in response


def isPending(chat_id, secondPartner):
    for marriage in marriages.find({'chat_id': chat_id, 'secondPartner': secondPartner}, projection={'_id': False, 'chat_id': False}):
        return marriage['is_pending']


def confirmMarriage(chat_id, user_id):
    marriages.update_one({'chat_id': chat_id, 'secondPartner': user_id}, {'$set': {'is_pending': True}})


def addAccs(acces):
    for acc in acces:
        print(acc)
        if not bool(accs.count_documents({'acc_id': acc}, limit=1)):
            accs.insert_one({'acc_id': acc})


def addStateForTaxes(state_id, user_id):
    if state_id not in isInTaxes(state_id):
        taxes.insert_one({'state_id': state_id, 'user_id': user_id})
        return True
    taxes.delete_one({'state_id': state_id, 'user_id': user_id})
    return False


def addPartyForTaxes(party_id, user_id):
    if party_id not in isInTaxes(party_id):
        taxes.insert_one({'state_id': party_id, 'user_id': user_id})
        return True
    taxes.delete_one({'state_id': party_id, 'user_id': user_id})
    return False


def isInTaxes(_id):
    ids = []
    [ids.append(state['state_id']) for state in taxes.find(projection={'_id': False, 'state_id': True})]
    return ids


def getAllTaxes(user_id):
    return taxes.find({'user_id': user_id}, projection={'_id': False, 'user_id': False})


def getTaxesUsers():
    return taxes.distinct('user_id')


def addToBlacklist(_id):
    blacklistDeps.insert_one({'acc_id': _id})


def getBlacklist():
    return list(map(lambda x: x['acc_id'], list(blacklistDeps.find(projection={'_id': False}))))
