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
<a href="%(link)s">Imgur</a>
"""
PLUGINVERSION = 2
# Always name this variable as `plugin`
# If you dont, module loader will fail to load the plugin!
plugin = core.Plugin(name="Imgur")
HEADERS = {"User-Agent": "OctoBot/1.0"}
LOGGER = logging.getLogger("Imgur")


def imgur_search(term, number, count=1):
    import requests

    url = "https://api.imgur.com/3/gallery/search/{{sort}}/{{window}}/{{page}}"

    querystring = {"q":term}

    headers = {'Authorization': 'Client-ID ' + settings.IMGUR_CID}

    pics = requests.request("GET", url, headers=headers, params=querystring).json()

    if not pics == []:
        resp = []
        LOGGER.debug(pics)
        for pic in pics["data"]:
            LOGGER.debug(pic)
            pic["title"] = html.escape(pic["title"][:1024])
            pic["link"] = html.escape(pic["link"])
            if "type" in pic and pic["type"] == "image/gif":
                key = catalog_provider.CatalogKey(text=message % pic, 
                                                  image=pic["link"],
                                                  thumbnail=pic["link"],
                                                  is_gif=True)
            elif "images" in pic:
                key = catalog_provider.CatalogKey(text=message % pic, 
                                                  image=pic["images"][0]["link"],
                                                  thumbnail=pic["images"][0]["link"])
            else:
                key = catalog_provider.CatalogKey(text=message % pic, 
                                                  image=pic["link"],
                                                  thumbnail=pic["link"])
            resp.append(key)
        return resp[number:], len(pics["data"])
    else:
        raise IndexError("Not found")

catalog_provider.create_catalog(plugin, imgur_search, ["/imgur"], "Searches images on Imgur")
