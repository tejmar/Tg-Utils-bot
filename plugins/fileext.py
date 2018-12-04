import core
from pprint import pprint
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
import requests
from bs4 import BeautifulSoup
import html

from collections import OrderedDict
PLUGINVERSION = 2
# Always name this variable as `plugin`
# If you dont, module loader will fail to load the plugin!
plugin = core.Plugin()
@plugin.command(command="/extension",
                description="Looks up for file extension on filext.com",
                inline_supported=True,
                hidden=False,
                required_args=1)
def get_ext(bot, update, user, args):
    """
    Usage: /extension any_extension_name
    Example: /extension png
    """
    info = _get_extension(args[0])
    message = ""
    for key, value in info.items():
        if not key.startswith("_"):
            message += "\n<b>%s</b>: <i>%s</i>" % (key, value)
    keyboard = [[InlineKeyboardButton(text="Related links:", callback_data="none")]]
    if "_links" in info:
        for item in info["_links"]:
            text, link = list(item.items())[0]
            keyboard.append([InlineKeyboardButton(text=text, url=link)])
        return core.message(text=message, parse_mode="HTML", inline_keyboard=InlineKeyboardMarkup(keyboard))
    else:
        return core.message(text=message, parse_mode="HTML")

def _get_extension(extension):
    r = requests.get("http://filext.com/file-extension/" + extension,
                     headers={"User-Agent":"Telegram @core_bot/1.0"})
    if r.ok:
        if not "did not return any results in the FILEXT.com database" in r.text:
            data = OrderedDict({"_links":[OrderedDict({"Extension on filext.com":r.url})]})
            soup = BeautifulSoup(r.text, "html.parser")
            notes = soup.find(id="extension-notes")
            for info in soup.find_all(id="file-type"):
                t = info.get_text().split(":")
                data[t[0].strip()] = " ".join(t[1:]).strip()
            data["Description"] = notes.div.text[1:].strip()
            info = soup.find(id="extended-info")
            for strong in info.find_all("strong"):
                div = strong.parent
                t = div.get_text().split(": ")
                if not t[0] == "Related links":
                    if not t[0].startswith("\n"):
                        data[t[0].strip()] = " ".join(t[1:]).strip()
                else:
                    for a in div.find_all("a"):
                        data["_links"].append({a.text:a["href"]})
            return data
        else:
            return {"Error":"Not found"}
    else:
        return {"Error":"Filext.com is not available right now!"}



if __name__ == '__main__':
    pprint(_get_extension("PNG"))
    pprint(_get_extension("DPG"))
    pprint(_get_extension("asdasdad"))

