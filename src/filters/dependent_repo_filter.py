import re

import requests
from loguru import logger

from src.util.rate_limit import token_rate_limit
from src.util.constants import TOKENS
from src.util.util import get_ver_major


def has_requirements_txt(dependent_repo_full_name):
    base_url = 'https://api.github.com/repos/{}/contents/{}'
    url = base_url.format(dependent_repo_full_name, 'requirements.txt')
    token = str(token_rate_limit(TOKENS)[0])
    if token is not None:
        GITHUB_HEADERS = {
            'Accept': 'application/vnd.github.v3+json',
            'Authorization': 'token ' + token
        }
        resp = requests.get(url, headers=GITHUB_HEADERS)
        if resp.status_code != 200:
            url = base_url.format(dependent_repo_full_name, 'requirements-dev.txt')
            resp = requests.get(url, headers=GITHUB_HEADERS)
    else:
        raise ValueError('Running out github access limit')
    return resp


def extract_used_dependency_version(str_requirements_txt_content, dependency_name):
    regex = '{}==(\\d+\\.(?:\\d+\\.)*\\d+)'
    version_regex = re.compile(regex.format(dependency_name))
    se = version_regex.search(str_requirements_txt_content)
    version = None if se is None else se.group().split('==')[1]
    return version


def repo_has_test_covered(dependent_repo_full_name, str_requirements_txt_content):
    repo_name = dependent_repo_full_name.split('/')[1]
    if repo_name != 'pytest':
        return 'pytest' in str_requirements_txt_content
    else:
        return True


def find_target_version(dependency_generic_object):  # repo_obj is the Generic object from Libraries.io Search result
    ls_versions = dependency_generic_object.versions
    latest_major_version = get_ver_major(ls_versions[len(ls_versions) - 1].number)
    target_version = ''
    for i in reversed(dependency_generic_object.versions):
        if latest_major_version - get_ver_major(i.number) == 1:
            target_version = i.number
            break
    logger.debug('Found the latest of the second last major version number {}'.format(target_version))
    return target_version


