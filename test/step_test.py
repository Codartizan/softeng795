import base64
import json

from loguru import logger

from src.filters.dependent_repo_filter import find_target_version, has_requirements_txt, \
    extract_used_dependency_version, repo_has_test_covered
from src.filters.dependent_repos import query_dependent_repos
from src.filters.projects_init_filter import query_most_used_dependencies
from src.util.util import get_repo_full_name, write_if_not_exist


def test_phase_one():
    dependencies = query_most_used_dependencies()
    dependency = dependencies[1]
    dependency_name = dependency.name
    dependency_full_name = get_repo_full_name(dependency.repository_url)
    target_version = find_target_version(dependency)
    logger.debug('Target dependency full name - {}'.format(dependency_full_name))

    prop_dependents = []
    suffix = ''
    counter = 1
    while len(prop_dependents) < 5:
        logger.debug('Scraping on page round {}'.format(counter))
        dependents_tuple = query_dependent_repos(dependency_full_name, suffix)
        suffix = dependents_tuple[1]

        for d in dependents_tuple[0]:
            if write_if_not_exist(dependency_name, d):
                has_req = False
                has_test = False
                ver_match = False
                has_req_txt_file_resp = has_requirements_txt(d)
                req_txt_decoded_content = ''
                if has_req_txt_file_resp.status_code == 200:
                    has_req = True

                if has_req:
                    req_txt_content = json.loads(has_req_txt_file_resp.content)
                    req_txt_decoded_content = base64.b64decode(req_txt_content['content']).decode('utf-8')
                    found_version = extract_used_dependency_version(req_txt_decoded_content, dependency_name)
                    ver_match = target_version == found_version

                if ver_match:
                    has_test = repo_has_test_covered(d, req_txt_decoded_content)

                if has_req and has_test and ver_match:
                    logger.debug('Found usable dependent {}'.format(d))
                    prop_dependents.append(d)
                    write_if_not_exist('usable', dependency_name + '||' + d)

                counter += 1

    print(prop_dependents)
    assert len(prop_dependents) == 5
