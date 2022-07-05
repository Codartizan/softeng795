import base64
import json

import requests
from loguru import logger

from src.util.constants import TOKENS
from src.util.generic import Generic
from src.util.token_limit import token_limit

base_url = 'https://api.github.com/search/code?q={}+in:file+repo:{}'


def dep_appearance(keyword, str_owner_repo):
    """
    Check if dependency keyword appears in repo more than twice. Only count *.py files
    :param keyword:
    :param str_owner_repo:
    :return:
    """
    url = base_url.format(keyword, str_owner_repo)
    token = token_limit(TOKENS)
    count = 0
    if token is not None:
        GITHUB_HEADERS = {
            'Accept': 'application/vnd.github.v3+json',
            'Authorization': 'token ' + base64.b64decode(token).decode()
        }
        resp = requests.get(url, headers=GITHUB_HEADERS)
        if resp.status_code == 200:
            items = json.loads(resp.text)['items']
            logger.debug('{} appears in {} {} times'.format(keyword, str_owner_repo, len(items)))
            for i in items:
                item = json.loads(json.dumps(i), object_hook=Generic.from_dict)
                if item.name != 'setup.py':
                    if item.name.endswith('.py'):
                        count += 1
        else:
            logger.error(resp.text)
    return count

