import requests
from bs4 import BeautifulSoup
from loguru import logger


def query_dependent_repos(dependency_full_name, path=None):
    if path is None:
        path = ''
    url = 'https://github.com/{}/network/dependents{}'.format(dependency_full_name, path)
    next_exists = True
    result = []
    count = 1
    limit = 2

    while next_exists:
        r = requests.get(url)
        if 'You have exceeded a secondary rate limit' not in r.text:
            soup = BeautifulSoup(r.content, "html.parser")
            # logger.debug(
                # 'Scraping on page {} - contains {} dependent repos'.format(count, url, len(soup.findAll("div", {
                #     "class": "Box-row"}))))
            result = result + [
                "{}/{}".format(
                    t.find('a', {"data-repository-hovercards-enabled": ""}).text,
                    t.find('a', {"data-hovercard-type": "repository"}).text,
                )
                for t in soup.findAll("div", {"class": "Box-row"})
            ]
            next_exists = False
            if soup.find("div", {"class": "paginate-container"}) is not None:
                for u in soup.find("div", {"class": "paginate-container"}).findAll('a'):
                    if u.text == "Next":
                        next_exists = True
                        count += 1
                        url = u["href"]
        else:
            next_exists = False
            logger.error('Secondary rate limit reached')

        if count >= limit:
            break

    # return 1st is result list, second is page extension
    return result, url.replace('https://github.com/{}/network/dependents'.format(dependency_full_name), '')
