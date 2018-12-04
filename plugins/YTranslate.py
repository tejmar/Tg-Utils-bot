"""
Yandex Translation API
"""
import logging
import html
from telegram import Bot, Update
from requests import post

import settings
import core
PLUGINVERSION = 2

LOGGER = logging.getLogger("YTranslate")
YAURL = "https://translate.yandex.net/api/v1.5/tr.json/translate"
plugin = core.Plugin(name="Yandex Translate")

YTL_TEMPLATE = """
<i>From %(from)s to %(to)s:</i>
<code>%(translation)s</code>
<b>Translated using </b><a href="translate.yandex.com">Yandex.Translate</a>
"""

def get_langs():
    return post("https://translate.yandex.net/api/v1.5/tr.json/getLangs", params={
        "key":settings.YANDEX_TRANSLATION_TOKEN,
        "ui":"en"
    }).json()

LANGS = get_langs()

@plugin.command(command=["/tl", "/translate"],
                description="Translates message to english. Example: [In Reply To Message] /tl",
                inline_supported=False,
                hidden=False)
def translate(bot: Bot, update: Update, user, args):  # pylint: disable=W0613
    """/tl"""
    if len(args) > 0:
        lang = args[0].lower()
        if len(lang.split("-")) > 1:
            from_, to = lang.split("-")
            if not from_ in LANGS["langs"]:
                return core.message("Unknown language - %s" % from_, failed=True)
            if not to in LANGS["langs"]:
                return core.message("Unknown language - %s" % to, failed=True)
            if not lang in get_langs()["dirs"]:
                return core.message("Yandex Translate API doesnt support this direction", failed=True)
    else:
        lang = "en"
    if len(args) > 1:
        text_to_tl = " ".join(args[1:])
    elif update.message.reply_to_message and not update.message.reply_to_message.from_user == bot.getMe():
        text_to_tl = update.message.reply_to_message.text
    else:
        return
    if not text_to_tl == "":
        yandex = post(YAURL, params={
                      "text": text_to_tl, "lang": lang,
                      "key":settings.YANDEX_TRANSLATION_TOKEN}).json()
        if "lang" in yandex:
            message = YTL_TEMPLATE % {
                "translation":html.escape(yandex["text"][0]),
                "from":LANGS["langs"][yandex["lang"].split("-")[0]],
                "to":LANGS["langs"][yandex["lang"].split("-")[1]]
            }
            return core.message(message, parse_mode="HTML", extra_args={"disable_web_page_preview":True})
        else:
            return core.message(yandex["message"], failed=True)
    else:
        return core.message("No text specified!", failed=True)