import core
import requests
import logging
from bs4 import BeautifulSoup
from urllib.parse import urljoin, quote
PLUGINVERSION = 2
# Always name this variable as `plugin`
# If you dont, module loader will fail to load the plugin!
plugin = core.Plugin("Qt5 Documentation")
LOGGER = logging.getLogger("Qt5 Docs")
URL = "http://doc.qt.io/qt-5/%s.html"
@plugin.command(command="/qt",
                description="Looks up query in Qt5 documentation",
                inline_supported=True,
                hidden=False,
                required_args=1)
def qt_search(bot, update, user, args):
    r = requests.get(URL % args[0])
    if r.ok:
        soup = BeautifulSoup(r.text, "html.parser")
        desc = soup.find(class_="descr")
        img = desc.find("img")
        if img is not None:
            img = urljoin("http://doc.qt.io/qt-5/", quote(img["src"]))
        LOGGER.debug(img)
        name = soup.find_all("h1")[2].text
        message = '<b>%s</b>\n%s\n<a href="%s">Continue in Qt documentation</a>' % (name, desc.find("p").text, r.url)
        return core.message(message, photo=img, parse_mode="HTML")
    else:
        return core.message(text="Not found!", failed=True)
