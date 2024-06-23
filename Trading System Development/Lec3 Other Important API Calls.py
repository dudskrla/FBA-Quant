'''
1) Getting Position Information : get_positions(symbol='')
2) Closing Positions : del_positions(symbol='', quantity=0)
3) Getting Account Information : get_account()
'''

import json
import requests 

HEADERS = json.loads(open("./key.txt", 'r').read())
ENDPOINT = "https://paper-api.alpaca.markets"

def get_positions(symbol=''):
    '''

    1) Getting Position Information

    '''
    if len(symbol) > 1:
        position_url = ENDPOINT + "/v2/positions/{}".format(symbol)
    else:
        position_url = ENDPOINT + "/v2/positions"
    r = requests.get(position_url, headers=HEADERS)
    return r.json()


def del_positions(symbol='', quantity=0):
    '''

    2) Closing Positions

    '''
    if len(symbol) > 1:
        position_url = ENDPOINT + "/v2/positions/{}".format(symbol)
        params = {'qty': quantity}
    else:
        position_url = ENDPOINT + "/v2/positions"
        params = {}
    r = requests.delete(position_url, headers=HEADERS, json=params)
    return r.json()


def get_account():
    '''

    3) Getting Account Information

    '''
    account_url = ENDPOINT + "/v2/account"
    r = requests.get(account_url, headers=HEADERS)
    return r.json()