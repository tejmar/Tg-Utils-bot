import core
import time
PLUGINVERSION = 2
# Always name this variable as `plugin`
# If you dont, module loader will fail to load the plugin!
PING_MSG = """
<code>PING %(fname)s (%(id)s) 56(84) bytes of data.
64 bytes from %(fname)s (%(id)s): icmp_seq=1 ttl=47 time=%(time)s

--- %(fname)s ping statistics ---
1 packets transmitted, 1 received, 0%% packet loss, time %(time)s seconds</code>
""".strip("\n")
plugin = core.Plugin()
@plugin.command(command="/ping",
                description="Command for checking if bot is alive",
                inline_supported=True,
                hidden=False)
def ping(bot, update, user, args):
    data = {
            "time":(time.time() - time.mktime(update.message.date.timetuple())),
            "fname":bot.getMe().username,
            "id":bot.getMe().id
    }
    return core.message(text=PING_MSG % data, parse_mode="HTML")
