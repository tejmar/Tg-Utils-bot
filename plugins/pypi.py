import re
import core
import html
import requests
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
PLUGINVERSION = 2
MESSAGE = """
<b>%(name)s</b> by <i>%(author)s</i> (%(author_email)s)
Platform: <b>%(platform)s</b>
Version: <b>%(version)s</b>
License: <b>%(license)s</b>
Summary: <i>%(summary)s</i>
"""
def cleanhtml(raw_html):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext
def escape_definition(definition):
    for key, value in definition.items():
        if isinstance(value, str):
            definition[key] = html.escape(cleanhtml(value))
    return definition

# Always name this variable as `plugin`
# If you dont, module loader will fail to load the plugin!
plugin = core.Plugin()
@plugin.command(command="/pypi",
                description="Searches for package in PyPI(the place where pip gets its files)",
                inline_supported=True,
                hidden=False,
                required_args=1)
def pypi_search(bot, update, user, args):
    r = requests.get("https://pypi.python.org/pypi/%s/json" % args[0], headers={"User-Agent":"OctoBot/1.0"})
    if r.ok:
        pypi = r.json()["info"]
        kbd = InlineKeyboardMarkup([
            [
            InlineKeyboardButton("Package on PyPI", url=pypi["package_url"]),
            ],
            [
            InlineKeyboardButton("Package home page", url=pypi["home_page"]),
            ]
        ])
        return core.message(MESSAGE % escape_definition(pypi), parse_mode="HTML", inline_keyboard=kbd)
    else:
        return core.message(text="Cant find %s in pypi" % args[0], failed=True)
