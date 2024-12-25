import jwt
import hashlib
import os
import requests
import uuid
from urllib.parse import urlencode, unquote
from utils.logger_config import logger


access_key = os.environ['ACCESS_KEY']
secret_key = os.environ['SECRET_KEY']
server_url = os.environ['SERVER_URL']


def get_accounts():
    payload = {
        'access_key': access_key,
        'nonce': str(uuid.uuid4()),
    }

    jwt_token = jwt.encode(payload, secret_key)
    authorization = 'Bearer {}'.format(jwt_token)
    headers = {
    'Authorization': authorization,
    }
    res = requests.get(server_url + '/v1/accounts', headers=headers)
    return res.json()


def post_order(decision, order_amount):
    params = {}

    if decision == 'buy':
        params = {
        'ord_type': 'price',
        'side': 'bid',
        'price': order_amount,
        'market': 'KRW-BTC',
        }
    elif decision == 'sell':
        params = {
        'ord_type': 'market',
        'side': 'ask',
        'volume': str(order_amount),
        'market': 'KRW-BTC',
        }

    query_string = unquote(urlencode(params, doseq=True)).encode("utf-8")
    m = hashlib.sha512()
    m.update(query_string)
    query_hash = m.hexdigest()

    payload = {
        'access_key': access_key,
        'nonce': str(uuid.uuid4()),
        'query_hash': query_hash,
        'query_hash_alg': 'SHA512',
    }

    jwt_token = jwt.encode(payload, secret_key)
    authorization = 'Bearer {}'.format(jwt_token)
    headers = {
    'Authorization': authorization,
    }

    if decision == 'buy':
        res = requests.post(server_url + '/v1/orders', json=params, headers=headers)
    else:
        res = requests.post(server_url + '/v1/orders?' + urlencode(params), headers=headers)
    logger.info(f"post_order API 응답: {res.json()}")
    return res.json()