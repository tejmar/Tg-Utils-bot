"""
Reddit module
"""
import logging

from telegram import Bot, Update
import praw, prawcore
from settings import REDDITID, REDDITUA, REDDITSECRET

import core
LOGGER = logging.getLogger("Reddit")
REDDIT = praw.Reddit(client_id=REDDITID,
                     client_secret=REDDITSECRET,
                     user_agent=REDDITUA
                    )

plugin = core.Plugin("Reddit")


@plugin.command(command="/r/",
                description="Shows top posts from subreddit",
                inline_supported=True,
                hidden=False)
def posts(bot: Bot, update: Update, user, args): # pylint: disable=W0613
    """
    /r/subreddit
    """
    try:
        sub = update.message.text.split("/")[2]
        if not sub == '':
            subreddit = REDDIT.subreddit(sub)
            message = "Hot posts in <b>/r/%s</b>:\n\n" % sub
            for post in subreddit.hot(limit=10):
                message += ' • <a href="%s">%s</a>\n' % (post.shortlink, post.title)
            return core.message(text=message, parse_mode='HTML')
    except (praw.exceptions.PRAWException, prawcore.exceptions.PrawcoreException):
        pass
