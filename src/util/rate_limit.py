import requests
import json
from generic import Generic
from loguru import logger

url = 'https://api.github.com/rate_limit'


def token_rate_limit(tokens):
    token = None
    for t in tokens:
        headers = {
            'Accept': 'application/vnd.github.v3+json',
            'Authorization': 'token ' + t
        }
        resp = requests.get(url, headers=headers)
        if resp.status_code == 200:
            body = json.loads(json.dumps(resp.json()), object_hook=Generic.from_dict)
            if body.rate.remaining > 0:
                token = t
                break
            else:
                logger.info('Token {} is running out limit'.format(t))
    return token
