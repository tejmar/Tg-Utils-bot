from telegram import Bot, Update, InlineKeyboardMarkup, InlineKeyboardButton
from requests import get
from telegram_ui import catalog_provider
import html
import core
import re
import logging


def cleanhtml(raw_html):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext

apiurl = "https://en.wikipedia.org/w/api.php"
message = """
<b>%(title)s</b>

<i>%(extract)s</i>

<a href="en.wikipedia.org/wiki/%(title)s">Article on Wikipedia</a>
"""
PLUGINVERSION = 2
# Always name this variable as `plugin`
# If you dont, module loader will fail to load the plugin!
plugin = core.Plugin(name="Wikipedia")
HEADERS = {"User-Agent": "OctoBot/1.0"}
LOGGER = logging.getLogger("Wiki")


def get_definition(term, number, count=1):
    definition = get(apiurl,
                     params={
                         "action": "query",
                         "format": "json",
                         "list": "search",
                         "srsearch": term,
                         "srinfo": "totalhits",
                         "srprop": ""
                     },
                     headers=HEADERS).json()
    if definition["query"]["search"]:
        if count + number > len(definition["query"]["search"]):
            maxdef = len(definition["query"]["search"])
        else:
            maxdef = count + number
        deflist = []
        for i in range(number-1, maxdef-1):
            defpath = definition["query"]["search"][i]
            deftxt = list(get(apiurl, params={
                "action": "query",
                "format": "json",
                "prop": "extracts",
                "list": "",
                "pageids": defpath["pageid"],
                "explaintext": 1,
                "exsentences": 4
            }).json()["query"]["pages"].values())[0]
            deftxt = escape_definition(deftxt)
            deflist.append(catalog_provider.CatalogKey(message % deftxt))
        return deflist, len(definition["query"]["search"])
    else:
        raise IndexError("Not found")


def escape_definition(definition):
    for key, value in definition.items():
        if isinstance(value, str):
            definition[key] = html.escape(cleanhtml(value))
    return definition

catalog_provider.create_catalog(plugin, get_definition, ["/wiki", "/wikipedia"], "Searches for query on Wikipedia")