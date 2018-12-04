import core
import requests
PLUGINVERSION = 2
# Always name this variable as `plugin`
# If you dont, module loader will fail to load the plugin!
plugin = core.Plugin()
PORTINFO = """
Port <code>#%(port)s</code>
<b>Description</b>: <i>%(description)s</i>
<b>Status</b>: <i>%(status)s</i>
<b>TCP</b>:<i>%(tcp)s</i>
<b>UDP</b>:<i>%(udp)s</i>
"""
PORTLIST = requests.get(
    "https://raw.githubusercontent.com/mephux/ports.json/master/ports.lists.json").json()


@plugin.command(command="/port",
                description="Sends information about port",
                inline_supported=True,
                required_args=1,
                hidden=False)
def port(bot, update, user, args):
    if " ".join(args) in PORTLIST:
        ports = []
        for port in PORTLIST[" ".join(args)]:
            port["description"] = port["description"].replace("â€”", " ")
            ports.append(PORTINFO % port)
        return core.message(text="\nAlso may be:".join(ports), parse_mode="HTML")
    else:
        return core.message(text="No such port in database", failed=True)
