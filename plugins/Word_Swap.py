"""
Word swap module
"""
import re
import logging
import html
import difflib

from telegram import Bot, Update
from telegram.ext import Filters, MessageHandler, Updater

import core
PLUGINVERSION = 2
from difflib import Differ

def appendBoldChanges(s1, s2):
    """
    Adds <b></b> tags to words that are changed
    https://stackoverflow.com/a/10775310
    """
    l1 = s1.split(' ')
    l2 = s2.split(' ')
    dif = list(Differ().compare(l1, l2))
    return " ".join(['<b>'+i[2:]+'</b>' if i[:1] == '+' else i[2:] for i in dif 
                                                           if not i[:1] in '-?'])
# Always name this variable as `plugin`
# If you dont, module loader will fail to load the plugin!
plugin = core.Plugin(name="Word Swapper")


@plugin.command(command=["s/", "/s/"],
                description="Swaps word in message",
                inline_supported=True,
                hidden=False)
def wordsw(bot: Bot, update: Update, user, args):
    """
    Example usage:
    User A
    Hi

    User B
    [In reply to User A]
    /s/Hi/Bye

    OctoBot
    Hello, User A
    Did you mean:
    Bye
    """
    try:
        msg = update.message
        txt = msg.text
        if msg.reply_to_message is not None:
            if not msg.reply_to_message.from_user.name == bot.getMe().name:
                offset = (1 if txt.startswith("/") else 0)
                groups = [b.replace("\/", "/") for b in re.split(r"(?<!\\)/", txt)]
                find = groups[1+offset]
                replacement = groups[2+offset]
                if len(groups) > 3+offset:
                    flags = groups[3+offset]
                else:
                    flags = ""
                find_re = re.compile("{}{}".format("(?{})".format(flags.replace("g", "")) if flags.replace("g", "") != "" else "", find))
                mod_msg = html.escape(find_re.sub(replacement, msg.reply_to_message.text, count=100))
                mod_msg = appendBoldChanges(msg.reply_to_message.text, mod_msg)
                text = core.locale.get_localized(core.locale.locale_string("did_you_mean", "word_swap"), update.message.chat.id) % (
                        msg.reply_to_message.from_user.first_name,
                        mod_msg
                )
                return core.message(text=text, parse_mode="HTML")
    except IndexError: pass
    except re.error: return core.message(text="Invalid regex!", failed=True)
