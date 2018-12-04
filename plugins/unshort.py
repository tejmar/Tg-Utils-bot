import core
import html
import requests
PLUGINVERSION = 2
# Always name this variable as `plugin`
# If you dont, module loader will fail to load the plugin!
plugin = core.Plugin()
@plugin.command(command="/unshort",
                description="Unshortens bit.ly/goo.gl and other url shorteners",
                inline_supported=True,
                hidden=False,
                required_args=1)
def unshort(bot, update, user, args):
    if not args[0].startswith("http"):
        args[0] = "http://" + args[0]
    r = requests.get(args[0], allow_redirects=False)
    if str(r.status_code).startswith('3'):
        return core.message(text="<b>%s</b> = <a href=\"%s\">%s</a>" % (html.escape(args[0]), r.headers["Location"], html.unescape(r.headers["Location"])), parse_mode="HTML")
    else:
        return core.message(text="This doesnt seems to be shortened link(status code:%s)" % r.status_code, failed=True)
