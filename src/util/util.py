# This file provides general utilities
import semver


# This is function return an int type of major version of a semantic version
# input must contain at least one semantic versioning delimiter "."
def get_ver_major(ver):
    try:
        major = semver.VersionInfo.parse(ver).major
    except ValueError:
        major = ver.split('.')[0]
    return int(major)


def get_repo_full_name(github_url):
    base_url = 'https://github.com/'
    return github_url.removeprefix(base_url)


def write_if_not_exist(filename, content):
    with open('/Users/tshi/PycharmProjects/softeng795/docs/{}.txt'.format(filename), 'a+') as file:
        file.seek(0)  # set position to start of file
        lines = file.read().splitlines()  # now we won't have those newlines
        if content in lines:
            return False
        else:
            file.write(content + "\n")
            return True
