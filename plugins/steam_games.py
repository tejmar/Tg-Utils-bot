import core
import requests
import logging
from bs4 import BeautifulSoup
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import html
PLUGINVERSION = 2
# Always name this variable as `plugin`
# If you dont, module loader will fail to load the plugin!
plugin = core.Plugin("Steam Games")
logger = logging.getLogger("Steam Games")
STEAM_APPS_URL = "http://api.steampowered.com/ISteamApps/GetAppList/v0002/?key=STEAMKEY&format=json"
STEAM_APP_INFO_URL = "https://store.steampowered.com/api/appdetails?appids=%s&cc=en"

STEAM_APPS = requests.get(STEAM_APPS_URL).json()["applist"]["apps"]
logger.info("Loaded %s apps", len(STEAM_APPS))


def find_game_info(query):
    logger.debug("Searching for %s" % query)
    if query.isdigit():
        app_info = list(requests.get(STEAM_APP_INFO_URL %
                                     query).json().values())[0]
        if app_info["success"]:
            return app_info["data"]
        else:
            return False
    else:
        for app in STEAM_APPS:
            if query.lower() in app["name"].lower():
                app_info = list(requests.get(STEAM_APP_INFO_URL %
                                             app["appid"]).json().values())[0]
                if app_info["success"] and app_info["data"]["type"] == "game":
                    return app_info["data"]
                else:
                    logger.debug("skipping %s", app)
                    continue
        return None


@plugin.command(command="/steamgame",
                description="Search steam game info, or get information by ID",
                inline_supported=True,
                hidden=False)
def search_game(bot, update, user, args):
    game = find_game_info(" ".join(args))
    if game is None:
        return core.message(text="Not found!")
    elif not game:
        return core.message(text="The provided appid doesn't contain valid app.")
    else:
        message = "<b>%s</b> by <i>" % html.escape(game["name"])
        message += html.escape(", ".join(game["developers"]))
        message += "</i> published by <i>%s</i>\n\n" % html.escape(
            ", ".join(game["publishers"]))
        message += html.escape(BeautifulSoup(game["short_description"], "html.parser").text)
        message += "\n\n<b>Purchase options:</b>\n"
        for purchase_option in game["package_groups"][0]["subs"]:
            message += html.escape(purchase_option["option_text"]) + "\n"
        markup = [
            [
                InlineKeyboardButton(
                    "This app on Steam", url="https://store.steampowered.com/app/%s" % game["steam_appid"])
            ],
        ]
        if game["website"]:
            markup.append([InlineKeyboardButton("Website", url=game["website"])])
        return core.message(message, photo=game["header_image"], inline_keyboard=InlineKeyboardMarkup(markup), parse_mode="HTML")
