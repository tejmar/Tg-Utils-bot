import re
from core import message, Plugin
from requests import get
PLUGINVERSION = 2
plugin = Plugin(name='GitHub URL')

EXPR = re.compile(r'^(?:github|gh):([a-zA-Z0-9\-_]+)(?:/([a-zA-Z0-9\-_]+)'
                  r'(?:#(\d+)|@([a-zA-Z0-9.\-_]+))?(?:/([a-zA-Z0-9.\-_/]+))?)?$')
BASE_URL = 'https://github.com/{user}'
REPO_INFO_URL = 'https://api.github.com/repos/{user}/{repo}'
HELP = """<i>Usage:</i>
<code>(github|gh):&lt;username&gt;[/&lt;repository&gt;[@&lt;branch&gt;|#&lt;issue&gt;][/&lt;path&gt;]]</code>"""


def get_issue_type(url, issue):
    resp = get('{}/issues/{}'.format(url, issue), allow_redirects=False)
    if resp.is_redirect or resp.status_code // 100 == 3:
        return 'pull'
    return 'issues'


def get_path_type(user, repository, path):
    resp = get((REPO_INFO_URL + '/contents/{path}').format(user=user, repo=repository,
                                                           path=path))
    resp = resp.json()
    if isinstance(resp, list):
        return 'tree'
    return 'blob'


def get_default_branch(user, repository):
    return get(REPO_INFO_URL.format(user=user, repo=repository)).json()['default_branch']


def exists(url):
    return get(url).status_code != 404


def build_url(user, repository, issue, branch, path):
    url = BASE_URL.format(user=user)
    if repository is None:
        return url
    url += '/' + repository
    if issue is not None:
        url += '/{}/{}'.format(get_issue_type(url, issue), issue)
        return url
    if branch is not None:
        url += '/tree/' + branch
    if path is not None:
        if branch is None:
            url += '/{}/{}'.format(get_path_type(user, repository, path),
                                   get_default_branch(user, repository))
        url += '/' + path
    return url


@plugin.message(regex=r'^(?:github|gh):.*')
def github(bot, update):
    # TODO: multiline matches
    match = EXPR.match(update.message.text)
    if match is None:
        return message(text='<b>Can\'t parse message.</b>\n' + HELP, failed=True, parse_mode='HTML')
    try:
        url = build_url(*match.groups())
        if exists(url):
            return message(text=url)
        raise ValueError
    except (KeyError, ValueError):
        return message(text='<b>Not found</b>', failed=True, parse_mode='HTML')
