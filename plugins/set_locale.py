import core
import os
import logging
import json
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
LOGGER = logging.getLogger("SetLocale")
PLUGINVERSION = 2
# Always name this variable as `plugin`
# If you dont, module loader will fail to load the plugin!
def switch_chat_locale(chat, locale):
    with open(os.path.normpath("plugdata/chat_locales.json")) as f:
        user_locales = json.load(f)
    with open(os.path.normpath("plugdata/chat_locales.json"), 'w') as f:
        user_locales[str(chat)] = locale
        json.dump(user_locales, f)

plugin = core.Plugin()
@plugin.command(command="/language",
                description="Changes bot language",
                inline_supported=False,
                hidden=False)
def locale_change(bot, update, user, args):
    with open(os.path.normpath("locale/locales.json"), encoding="utf-8") as f:
        locale_list = json.load(f)
    if len(args) > 0:
        if args[0] in locale_list.keys():
            switch_chat_locale(update.message.chat.id, args[0])
            return core.message("Your language now is <code>%s</code>" % args[0], parse_mode="HTML")
        else:
            return core.message(text="Unknown language: <code>%s</code>" % args[0], parse_mode='HTML')
    else:
        inkbd = []
        t = []
        for k, v in locale_list.items():
            if len(t) == 4:
                inkbd.append(t)
                t = []
            t.append(InlineKeyboardButton("%s\n%s" % (v, k), callback_data="sl:%s" % k))
        if t:
            inkbd.append(t)
        return core.message(text="Click on button with your locale flag to switch locale", inline_keyboard=InlineKeyboardMarkup(inkbd))

@plugin.inline_button(callback_name="sl")
def sw_lc_inline(bot, update, query):
    locale = query.data.split(":")[1]
    switch_chat_locale(query.message.chat.id, locale)
    lsuccess = core.locale.get_localized(core.locale.locale_string("language_set_ok", "core"), query.message.chat.id) % locale
    LOGGER.debug(lsuccess)
    query.answer(lsuccess)
    query.edit_message_text(lsuccess)
