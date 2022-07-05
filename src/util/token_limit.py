import requests
import json
import base64
from src.util.generic import Generic
from loguru import logger


def token_limit(tokens):
    """
    GitHub PAT has rate limit. This method is to find out a workable PAT from a given list
    :param tokens: a list of base64 encoded token string
    :return: PAT string
    """
    token = None
    for t in tokens:
        headers = {
            'Accept': 'application/vnd.github.v3+json',
            'Authorization': 'token ' + base64.b64decode(t).decode()
        }
        resp = requests.get('https://api.github.com/rate_limit', headers=headers)
        if resp.status_code == 200:
            body = json.loads(json.dumps(resp.json()), object_hook=Generic.from_dict)
            if body.rate.remaining > 0:
                logger.info('{} rate limit remaining: {}'.format(tokens.index(t), body.rate.remaining))
                token = t
                break
            elif body.rate.remaining == 0:
                logger.info('Token {} is running out limit'.format(t))
        elif resp.status_code == 401:
            logger.info('Token {} is expired'.format(t))
    return token
