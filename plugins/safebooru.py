from telegram_ui import catalog_provider
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


message = """
<b>Rating:</b> <i>%(rating)s</i>
<b>Tags:</b> <i>%(tags)s</i>
<a href="https://safebooru.org/index.php?page=post&s=view&id=%(id)s">Image on safebooru</a>
"""
PLUGINVERSION = 2
# Always name this variable as `plugin`
# If you dont, module loader will fail to load the plugin!
plugin = core.Plugin(name="safebooru")
HEADERS = {"User-Agent": "OctoBot/1.0"}
LOGGER = logging.getLogger("safebooru")


def safebooru_search(term, number, count=1):
    image = get("https://safebooru.org/index.php",
                     params={
                        "page":"dapi",
                        "s":"post",
                        "q":"index",
                        "tags":term,
                        "limit":count,
                        "pid":number-1
                     },
                     headers=HEADERS)
    api_q = bs4.BeautifulSoup(image.text, "html.parser").posts
    if int(api_q.attrs["count"]) > 0:
        resp = []
        for post in api_q.find_all("post"):
            post.attrs["tags"] = html.escape(post.attrs["tags"][:1024])
            resp.append(catalog_provider.CatalogKey(text=message % post.attrs, 
                                               image="https:" + post.attrs["file_url"],
                                               thumbnail="https:" + post.attrs["preview_url"]))
        return resp, api_q.attrs["count"]
    else:
        raise IndexError("Not found")

catalog_provider.create_catalog(plugin, safebooru_search, ["/sb", "/safebooru"], "Searches for query on safebooru")
