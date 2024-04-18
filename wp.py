import requests
import re
import json


class Handler(object):
    def __init__(self, email, password):
        self.session, self.csrf = self.login(email, password)

    def get(self, link, data=''):
        if self.checkValid(self.session):
            response = self.session.get(link, data=data)
            return response
        else:
            self.session = self.login('1', '1')
            response = self.session.get(link, data=data)
            return response

    def post(self, link, data=''):
        if self.checkValid(self.session):
            response = self.session.post(link, data=data)
            return response
        else:
            self.session = self.login('1', '1')
            response = self.session.post(link, data=data)
            return response

    @staticmethod
    def checkValid(session):
        if "Логин через" in session.get('https://test.wildpolitics.online/').text:
            return 0
        return 1

    @staticmethod
    def login(email, password):
        s = requests.Session()
        s.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                          '(KHTML, like Gecko) Chrome/81.0.4044.142 Safari/537.36'})
        r = s.get('https://test.wildpolitics.online/accounts/login/')
        s.post('https://test.wildpolitics.online/accounts/login/', data={
            'csrfmiddlewaretoken': re.search('csrfmiddlewaretoken" value="(.+)"', r.text).group(1),
            'login': email,
            'password': password,
            'remember': 'on'
        })
        return s, s.cookies.items()[0][1]


def getPrices():
    bot = Handler('1', '1')
    offers = json.loads(bot.post('https://test.wildpolitics.online/get_offers/', data={
        'csrfmiddlewaretoken': bot.csrf,
        'undefined': '',  # ???
        'action': 'sell',
        'range': 'undefined',
        'owner': 'all',
        'groups': 'null',
        'good': 'null'
    }).text)['offers_list']
    cheapest = {}
    for offer in offers:
        if offer['good'] not in cheapest.keys():
            cheapest.update({offer['good']: offer['price']})
        else:
            if offer['price'] < cheapest.get(offer['good']):
                offer['good'] = offer['price']
    return cheapest

