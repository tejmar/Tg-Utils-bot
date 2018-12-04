"""
Know Your Meme command
"""
import requests
import logging
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
import core


TEMPLATE = """%(name)s
Origin:%(origin)s

%(summary)s
"""

PLUGINVERSION = 2
# Always name this variable as `plugin`
# If you dont, module loader will fail to load the plugin!
plugin = core.Plugin("KnowYourMeme.com search")
logger = logging.getLogger("KnowYourMeme.com")

@plugin.command(command="/meme",
                description="Looks up for definition of query on knowyourmeme.com",
                inline_supported=True,
                required_args=1,
                hidden=False)
def meme(bot: Bot, update: Update, user, args):  # pylint: disable=W0613
    """
    Example usage:
    User:/meme noot
    Bot: [Picture]
    Bot: Noot Noot
    Origin:YouTube
    “Noot Noot” is the sound made by the titular character from the British-Swiss children’s TV series Pingu.  Due to its frequent utterance throughout the series, the soundbite of the catchphrase has been incorporated into a variety of pop music mash-ups and photoshopped images on Tumblr.
    [Button to view full definition]
    """
    memes = requests.get("http://rkgk.api.searchify.com/v1/indexes/kym_production/instantlinks",
                         params={
                             "query": " ".join(args),
                             "fetch": "*"
                         }).json()
    if memes["matches"] > 0:
        meme = memes["results"][0]
        logger.debug(meme)
        if not "summary" in meme:
            meme["summary"] = ""
        message = TEMPLATE % meme
        keyboard = [
            [InlineKeyboardButton(
                "Definition on KnowYourMeme.com", url="http://knowyourmeme.com" + meme["url"])]
        ]
        markup = InlineKeyboardMarkup(keyboard)
        return core.message(text=message, inline_keyboard=markup, photo=meme["icon_url"])
    else:
        return core.message(text='Not found!', failed=True)
