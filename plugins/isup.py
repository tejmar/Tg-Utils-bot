import core
import requests
PLUGINVERSION = 2
# Always name this variable as `plugin`
# If you dont, module loader will fail to load the plugin!
plugin = core.Plugin()
@plugin.command(command="/isup",
                description="Checks if site is up or not",
                inline_supported=True,
                hidden=False)
def isup(bot, update, user, args):
    if args:
        try:
            r = requests.get("http://downforeveryoneorjustme.com/" + args[0])
        except (UnicodeDecodeError, UnicodeDecodeError):
            return core.message(text="There is some problems with isup.me. I cant provide you info on this site, sorry.", failed=True)
        if r.ok:
            r = r.text
            if "looks down" in r:
                return core.message(text="It's not just you! %s looks down from here. " % args[0])
            elif "It's just you" in r:
                return core.message(text="It's just you. %s is up. " % args[0])
            elif "interwho" in r:
                return core.message(text="Huh? %s doesn't look like a site on the interwho. " % args[0])
        else:
            return core.message(text="There is some problems with isup.me. I cant provide you info on this site, sorry.", failed=True)
