import core
import html

import textwrap
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import settings
import logging
PLUGINVERSION = 2
# Always name this variable as `plugin`
# If you dont, module loader will fail to load the plugin!
plugin = core.Plugin()
LOGGER = logging.getLogger(__file__)


@plugin.command(command="/start",
                inline_supported=False,
                hidden=True)
def start(bot, update, user, args):
    def _(x): return core.locale.get_localized(x, update.message.chat.id)
    if len(args) > 0:
        if args[0] == "help" and update.message.chat.type == "private":
            return core.message(bot.modloader.gen_help(update.message.chat.id), parse_mode="HTML")
    kbd = [
            [InlineKeyboardButton(
                text=_(bot.modloader.locales["help_button"]), url="http://t.me/%s?start=help" % bot.getMe().username)],
            [InlineKeyboardButton(
                text=_(bot.modloader.locales["news_button"]), url=settings.NEWS_LINK)],
            [InlineKeyboardButton(
                text=_(bot.modloader.locales["chat_button"]), url=settings.CHAT_LINK)],
        ]
    for extra_link in settings.EXTRA_LINKS:
        name, link = list(extra_link.items())[0]
        kbd.append([InlineKeyboardButton(text=name, url=link)])
    return core.message(_(bot.modloader.locales["start"]) % bot.getMe().first_name, inline_keyboard=InlineKeyboardMarkup(kbd))


@plugin.update()
def new_member(bot, update):
    if update.message:
        if update.message.new_chat_members:
            for member in update.message.new_chat_members:
                if member.id == bot.getMe().id:
                    def _(x): return core.locale.get_localized(x, update.message.chat.id)
                    kbd = InlineKeyboardMarkup(
                        [
                            [InlineKeyboardButton(
                                text=_(bot.modloader.locales["help_button"]), url="http://t.me/%s?start=help" % bot.getMe().username)],
                            [InlineKeyboardButton(
                                text=_(bot.modloader.locales["news_button"]), url=settings.NEWS_LINK)],
                            [InlineKeyboardButton(
                                text=_(bot.modloader.locales["chat_button"]), url=settings.CHAT_LINK)],
                        ]
                    )
                    return core.message(_(bot.modloader.locales["start"]) % bot.getMe().first_name, inline_keyboard=kbd)

@plugin.command(command="/help", hidden=True, inline_supported=False)
def coreplug_help(bot, update, user, args):
    def _(x): return core.locale.get_localized(x, update.message.chat.id)
    if args:
        LOGGER.debug(args)
        for plugin in bot.modloader.plugins:
            for command_ in plugin.commands:
                cmd_alias = command_.command
                if isinstance(cmd_alias, str):
                    cmd_alias = [cmd_alias]
                for command in cmd_alias:
                    LOGGER.debug(command)
                    if "/" + args[0].lower() == command.lower():
                        info = {"command": "/" + args[0], "description": command_.description,
                                "docs": _(bot.modloader.locales["not_available"])}
                        if command_.execute.__doc__:
                            info["docs"] = html.escape(
                                textwrap.dedent(command_.execute.__doc__))
                        return core.message(_(bot.modloader.locales["help_format"]) % info, parse_mode="HTML")
        return core.locale.get_localized(bot.modloader.locales["unknown_help_command"], update.message.chat.id)
    else:
        if update.message.chat.type == "private":
            return core.message(bot.modloader.gen_help(update.message.chat.id), parse_mode="HTML")
        else:
            keyboard = InlineKeyboardMarkup([[InlineKeyboardButton(
                text=_(bot.modloader.locales["help_button_into_pm"]), url="http://t.me/%s?start=help" % bot.getMe().username)]])
            return core.message(_(bot.modloader.locales["help_button_into_pm_text"]), inline_keyboard=keyboard)
