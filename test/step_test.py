import unittest
import base64
import json

from loguru import logger

from src.filters.dependent_repo_filter import find_target_version, has_requirements_txt, \
    extract_used_dependency_version, repo_has_test_covered
from src.filters.dependent_repos import query_dependent_repos
from src.filters.projects_init_filter import query_most_used_dependencies
from src.util.util import get_repo_full_name


class step_test(unittest.TestCase):
    dependencies = query_most_used_dependencies()
    dependency = dependencies[0]
    dependency_name = dependency.name
    dependency_full_name = get_repo_full_name(dependency.repository_url)
    target_version = find_target_version(dependency)
    logger.debug('Target dependency full name - {}'.format(dependency_full_name))

    prop_dependents = []
    suffix = ''
    counter = 0
    while len(prop_dependents) < 5:
        logger.debug('Scraping on page {}'.format(counter))
        dependents_tuple = query_dependent_repos(dependency_full_name, suffix)
        suffix = dependents_tuple[1]

        for d in dependents_tuple[0]:
            is_usable = False
            has_req_txt_file_resp = has_requirements_txt(d)
            found_version = ''
            if has_req_txt_file_resp.status_code == 200:
                req_txt_content = json.loads(has_req_txt_file_resp.content)
                req_txt_decoded_content = base64.b64decode(req_txt_content['content']).decode('utf-8')
                found_version = extract_used_dependency_version(d, req_txt_decoded_content, dependency_name)
                is_usable = True and repo_has_test_covered(d, req_txt_decoded_content)

            is_usable = True if target_version == found_version else False

            if is_usable:
                logger.debug('Found usable dependent {}'.format(d))
                prop_dependents.append(d)

        counter += 1

    print(prop_dependents)
