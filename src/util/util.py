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
