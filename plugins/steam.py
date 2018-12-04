"""Steam module"""
import core
from telegram import Bot, Update
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from requests import get
import xmltodict
import settings


def getuser(url):
    if url.isdigit():
        r = xmltodict.parse(
            get("http://steamcommunity.com/profiles/%s/?xml=1" % url).text)
    else:
        r = xmltodict.parse(
            get("http://steamcommunity.com/id/%s/?xml=1" % url).text)
    return dict(r)


def get_inventory(sid):
    uinfo = get("https://backpack.tf/api/users/info/v1",
                params={
                    "key": settings.BACKPACK_TF_TOKEN,
                    "steamids": sid
                }).json()
    user = list(uinfo["users"].values())[0]
    if "inventory" in user:
        message = "🎒Inventory information\n"
        if "440" in user["inventory"]:  # TF2
            inv = user["inventory"]["440"]
            if "value" not in inv:
                inv["value"] = 0
            message += "├🎩TF2 Inventory:\n"
            message += f'│├🔑Keys:{inv["keys"]}\n'
            message += f'│├💰Value(refined):{inv["value"]}\n'
            message += f'│└🏋️Used slots:{inv["slots"]["used"]}/{inv["slots"]["total"]}\n'
        if "570" in user["inventory"]:  # Dota 2
            inv = user["inventory"]["570"]
            if "value" not in inv:
                inv["value"] = 0
            message += "├🦀Dota 2 Inventory:\n"
            message += f'│├🔑Keys:{inv["keys"]}\n'
            message += f'│└💰Value(USD):{inv["value"]}\n'
        if "730" in user["inventory"]:  # CS:GO
            inv = user["inventory"]["730"]
            if "value" not in inv:
                inv["value"] = 0
            message += "├🏳️‍🌈CS:GO Inventory:\n"
            message += f'\u00a0├🔑Keys:{inv["keys"]}\n'
            message += f'\u00a0└💰Value(USD):{inv["value"]}\n'
        return message
    else:
        return ''


PLUGINVERSION = 2
# Always name this variable as `plugin`
# If you dont, module loader will fail to load the plugin!
plugin = core.Plugin()


@plugin.command(command="/steam",
                description="Sends info about profile on steam. Use custom user link. Example:/steam gabelogannewell",
                inline_supported=True,
                hidden=False)
def steam(b: Bot, u: Update, user, args):
    """
    Example usage:
    User A: Where is pyro update?
    User B: Ask him
    User B: /steam gabelogannewell
    Bot: [Account userpic]
    Bot:
    User:Rabscuttle
    SteamID64:76561197960287930
    Last Online
    🛡️User is not VACed
    💱User is not trade banned
    🔓User account is not limited
    ⚠️User account visibility is limited
    """
    if len(args) >= 1:
        account = getuser(args[0])
        if "response" in account:
            return core.message("Cant find this user!", failed=True)
        else:
            message = ""
            user = account["profile"]
            message += "👤User:%s\n" % user["steamID"]
            message += "🆔SteamID64:%s\n" % user["steamID64"]
            if user["onlineState"].lower() == "offline":
                message += "🔴%s\n" % user["stateMessage"]
            else:
                message += "🔵%s\n" % user["stateMessage"].replace(
                    "<br/>", "\n🎮")
            message += "🛡️"
            if user["vacBanned"] == '0':
                message += "User is not VACed\n"
            else:
                message += "User is VACed\n"
            message += "💱"
            if user["tradeBanState"] == "None":
                message += "User is not trade banned\n"
            else:
                message += "User is trade banned\n"
            if user["isLimitedAccount"] == '0':
                message += "🔓User account is not limited\n"
            else:
                message += "🔒User account is limited\n"
            if user["privacyState"] == "public":
                message += "📅User is member since %s\n" % user["memberSince"]
            else:
                message += "⚠️User account visibility is limited\n"
            message += get_inventory(user["steamID64"])
            keyboard = [
                [InlineKeyboardButton(
                    "Steam profile", url="https://steamcommunity.com/profiles/" + user["steamID64"])]
            ]
            markup = InlineKeyboardMarkup(keyboard)

            return core.message(message, photo=user["avatarFull"], inline_keyboard=markup)
    else:
        return core.message("Custom link is not supplied!", failed=True)
