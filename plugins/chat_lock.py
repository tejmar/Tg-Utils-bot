"""
Echo plugin example
"""
import core
import random, string

def randomword(length):
   letters = string.ascii_lowercase
   return ''.join(random.choice(letters) for i in range(length))

global locked
locked = []
PLUGINVERSION = 2
# Always name this variable as `plugin`
# If you dont, module loader will fail to load the plugin!
plugin = core.Plugin()
@plugin.message(regex=".*") # You pass regex pattern
def lock_check(bot, update):
    if update.message.chat_id in locked:
        for admin in update.message.chat.get_administrators():
            if admin.user.username == update.message.from_user.username:
                return
        update.message.delete()
    return

@plugin.command(command="/chat_lock",
                description="Locks chat",
                inline_supported=True,
                hidden=False)
def lock(bot, update, user, args):
    if update.message.chat_id in locked:
        return core.message("Chat is already locked")
    if update.message.chat.type != "private":
        for admin in update.message.chat.get_administrators():
            if admin.user.username == update.message.from_user.username:
                for admin in update.message.chat.get_administrators():
                    if admin.user.username == bot.get_me().username:
                        locked.append(update.message.chat_id)
                        return core.message("Chat locked")
                return core.message("I am not admin of this chat...")
        return core.message(text="Hey! You are not admin of this chat!", photo="https://pbs.twimg.com/media/C_I2Xv1WAAAkpiv.jpg")
    else:
        return core.message("Why would you lock a private converstaion?")

@plugin.command(command="/unlock",
                description="Unlocks chat",
                inline_supported=True,
                hidden=False)
def unlock(bot, update, user, args):
    if update.message.chat_id in locked:
        for admin in update.message.chat.get_administrators():
            if admin.user.username == update.message.from_user.username:
                locked.remove(update.message.chat_id)
                return core.message("Chat unlocked")
    else:
        return core.message("This chat wasnt locked at all")