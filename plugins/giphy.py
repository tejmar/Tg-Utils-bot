from telegram_ui import catalog_provider
from requests import get
import bs4
import html
import core
import re
import logging
import settings

def cleanhtml(raw_html):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext


message = """
<b>%(title)s</b>
<a href="%(url)s">GIF on Giphy</a>
"""
PLUGINVERSION = 2
# Always name this variable as `plugin`
# If you dont, module loader will fail to load the plugin!
plugin = core.Plugin(name="Giphy")
HEADERS = {"User-Agent": "OctoBot/1.0"}
LOGGER = logging.getLogger("Giphy")


def giphy_search(term, number, count=1):
    gifs = get("https://api.giphy.com/v1/gifs/search",
                     params={
                        "api_key":settings.GIPHY_TOKEN,
                        "rating":"R",
                        "lang":"en",
                        "limit":count,
                        "offset":number-1,
                        "q":term
                     },
                     headers=HEADERS).json()
    if gifs["pagination"]["total_count"] != 0:
        resp = []
        for gif in gifs["data"]:
            gif["title"] = html.escape(gif["title"][:1024])
            gif["url"] = html.escape(gif["url"])
            LOGGER.debug(resp)
            key = catalog_provider.CatalogKey(text=message % gif, 
                                        image=gif["url"],
                                        thumbnail=gif["url"],
                                        is_gif=True)
            resp.append(key)
        return resp, gifs["pagination"]["total_count"]
    else:
        raise IndexError("Not found")

catalog_provider.create_catalog(plugin, giphy_search, ["/gif", "/giphy"], "Searches for GIF on giphy")
