import base64
import json

from loguru import logger

from src.dependent.dep_filter import find_target_version, has_content, \
    extract_dependency_version, has_pytest, pkg_management_validation
from src.dependent.dep_scraper import scraping_dependent_pkg
from src.dependency.search_dep import search_dependency_by_rank
from src.util.util import repo_full_name, write_if_not_exist, mapping_resp_to_generic
from src.dependent.code_search import dep_appearance


def test_phase_one():
    dependencies = search_dependency_by_rank()
    dependency = dependencies[2]
    dependency_name = dependency.name
    dependency_full_name = repo_full_name(dependency.repository_url)
    target_version = find_target_version(dependency)
    logger.debug('Target dependency full name - {}'.format(dependency_full_name))

    prop_dependents = []
    suffix = ''
    counter = 1
    while len(prop_dependents) < 5:
        logger.debug('Scraping on page round {}'.format(counter))
        dependents_tuple = scraping_dependent_pkg(dependency_full_name, suffix)
        suffix = dependents_tuple[1]

        for d in dependents_tuple[0]:
            if write_if_not_exist(dependency_name, d):
                has_req = False
                has_test = False
                ver_match = False
                has_pkg_management = pkg_management_validation(d)
                appearance = dep_appearance(dependency_name, d)

                if has_pkg_management.status_code == 200:
                    has_req = True
                    res_obj = mapping_resp_to_generic(has_pkg_management)
                    pkg_management_decoded_content = base64.b64decode(res_obj.content).decode()
                    # req_txt_content = json.loads(has_pkg_management.content)
                    # pkg_management_decoded_content = base64.b64decode(req_txt_content['content']).decode('utf-8')
                    found_version = extract_dependency_version(pkg_management_decoded_content, dependency_name)
                    logger.debug('{} is using {} version {}'.format(d, dependency_name, found_version))
                    has_test = has_pytest(d, pkg_management_decoded_content)
                    ver_match = target_version == found_version
                    write_if_not_exist('{}-{}'.format(dependency_name, found_version),
                                       '{} | {} | {}'.format(d, res_obj.name, appearance))

                if has_req and has_test and ver_match and appearance > 3:
                    logger.debug('Found usable dependent {}'.format(d))
                    prop_dependents.append(d)
                    write_if_not_exist('usable', dependency_name + '||' + d)

        counter += 1

    print(prop_dependents)
    assert len(prop_dependents) == 5
