from pprint import pformat
from io import BytesIO

import core
import settings

PLUGINVERSION = 2
# Always name this variable as `plugin`
# If you dont, module loader will fail to load the plugin!
plugin = core.Plugin()


@plugin.command(command="//msgdump",
                hidden=True)
def dump(bot, update, user, args):
    text = pformat(update.message.to_dict())
    text_obj = BytesIO()
    text_obj.name = "%s.txt" % update.update_id
    text_obj.write(bytes(text, "utf-8"))
    text_obj.seek(0)
    return core.message(file=text_obj)


@plugin.command(command="//delmsg",
                inline_supported=False,
                hidden=True)
def msgdel(bot, update, user, args):
    if user.id == settings.ADMIN:
        update.message.reply_to_message.delete()


@plugin.command(command="//exec",
                hidden=True)
def docode(bot, update, user, args):
    if user.id == settings.ADMIN:
        return core.message(eval(" ".join(args)))


@plugin.command(command="//plugins", hidden=True)
def coreplug_list(bot, *_):
    message = []
    for plugin in bot.modloader.plugins:
        txt = ''
        if plugin.state == core.constants.OK:
            txt += "✅"
        else:
            txt += "⛔"
        txt += plugin.name
        message.append(txt)
    message = sorted(message)
    message.reverse()
    return core.message("\n".join(message))


@plugin.command(command="//sideload", hidden=True)
def coreplug_load(self, bot, update, user, args):
    args = " ".join(args)
    if user.id == settings.ADMIN:
        self.logger.info("Reload requested.")
        update.message.reply_text("Loading " + args)
        self.load_plugin(args)
        return self.coreplug_list()
    else:
        return core.message("Access Denied.")
