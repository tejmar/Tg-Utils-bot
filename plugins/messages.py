import core
import random
import telegram
PLUGINVERSION = 2
# Always name this variable as `plugin`
# If you dont, module loader will fail to load the plugin!
plugin = core.Plugin()
@plugin.command(command="/first_message",
                description="Replies to first message in chat",
                inline_supported=False,
                hidden=False)
def fmsg(bot, update, user, args):
    try:
        bot.sendMessage(update.message.chat.id, "Here is first message in this chat", reply_to_message_id=1)
    except telegram.error.BadRequest:
        return core.message('Seems like first message of this chat was deleted.', failed=True)

@plugin.command(command="/random_message",
                description="Replies to random message in chat",
                inline_supported=False,
                hidden=False)
def rmsg(bot, update, user, args):
    try:
        bot.sendMessage(update.message.chat.id, "Random message", reply_to_message_id=random.randint(1, update.message.message_id))
    except telegram.error.BadRequest:
        return core.message("I tried to reply to random message, but it seems to be deleted! Try using command again", failed=True)
