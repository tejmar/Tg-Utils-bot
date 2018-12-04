from telegram import Bot, Update, InlineKeyboardMarkup, InlineKeyboardButton
from requests import get
import bs4
import html
import core
import re
import logging


def cleanhtml(raw_html):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext

searchurl = "https://wiki.archlinux.org/index.php/%s"
message = """
<b>%(title)s</b>

<i>%(extract)s</i>

<a href="wiki.archlinux.org/index.php/%(title)s">Article on ArchWiki</a>
"""
PLUGINVERSION = 2
# Always name this variable as `plugin`
# If you dont, module loader will fail to load the plugin!
plugin = core.Plugin()
HEADERS = {"User-Agent": "OctoBot/1.0"}
LOGGER = logging.getLogger("ArchWiki")


def get_definition(term):
    definition = get(searchurl % term,
                     headers=HEADERS)
    LOGGER.debug(definition.url)
    if definition.ok:
        soup = bs4.BeautifulSoup(definition.text, "html.parser")
        definition = {}
        definition["extract"] = soup.find(id="mw-content-text").find_all("p")[1].text.strip("\n")
        definition["title"] = soup.find(id="firstHeading").text
        definition = escape_definition(definition)
        return message % definition
    else:
        LOGGER.debug(definition.text)
        raise IndexError("Not found")


def escape_definition(definition):
    for key, value in definition.items():
        if isinstance(value, str):
            definition[key] = html.escape(cleanhtml(value))
    return definition


@plugin.command(command="/aw",
                description="Searches for query in Arch Wiki",
                inline_supported=True,
                required_args=1,
                hidden=False)
def wikipedia(_: Bot, ___: Update, user, args):
    term = " ".join(args)
    try:
        definition = get_definition(term)
    except IndexError:
        return core.message("Nothing found!", failed=True)
    else:
        return core.message(definition, parse_mode="HTML")