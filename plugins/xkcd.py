"""
xkcd module by @Protoh
"""
from telegram import Bot, Update
from urllib.parse import quote
import requests

import core
PLUGINVERSION = 2
# Always name this variable as `plugin`
# If you dont, module loader will fail to load the plugin!
plugin = core.Plugin(name="xkcd")

TEXT = """
*title:* %(safe_title)s
*number:* %(num)s
*date*`(yyyy-mm-dd for christ's sake)`*:* %(year)s-%(month)s-%(day)s
*alt:* _%(alt)s_
*link:* xkcd.com/%(num)s
"""

@plugin.command(command="/xkcd",
                description="Sends xkcd comics in the chat! usage: '/xkcd', '/xkcd <number>', or '/xkcd <query>'",
                inline_supported=True,
                hidden=False)
def xkcd(bot: Bot, update: Update, user, args): # pylint: disable=W0613
    """
    Example usage:
    User:
    /xkcd 1

    OctoBot:
    title: Barrel - Part 1
    number: 1
    date(yyyy-mm-dd for christ's sake): 2006-01-01
    alt: Don't we all.
    link: xkcd.com/1
    """
    argument = " ".join(args)
    id = ""
    if not argument:
        id = -1
    else:
        if argument.isdigit():
            id = argument
        else:
            queryresult = requests.get('https://relevantxkcd.appspot.com/process?',params={"action":"xkcd","query":quote(argument)}).text
            id = queryresult.split(" ")[2].lstrip("\n")
    data = ""
    if id == -1:
        data = requests.get("https://xkcd.com/info.0.json").json()
    else:
        r = requests.get("https://xkcd.com/{}/info.0.json".format(id))
        if r.ok:
            data = r.json()
        else:
            return core.message("xkcd n.{} not found!".format(id), failed=True)
    #msg.reply_photo(photo = data['img']) Cause telegram makes preview of comic, we dont need it anymore
    data['month'] = data['month'].zfill(2)
    data['day'] = data['day'].zfill(2)
    return core.message(TEXT % data, parse_mode="MARKDOWN")
