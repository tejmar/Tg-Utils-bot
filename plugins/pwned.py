"""Have I been pwned module"""
from cgi import escape
from telegram import Bot, Update
import requests
from emoji import emojize
import core
headers = {
    'User-Agent': 'OctoBotHIBP/1.0'
}


PLUGINVERSION = 2
# Always name this variable as `plugin`
# If you dont, module loader will fail to load the plugin!
plugin = core.Plugin()


@plugin.command(command="/pwned",
                description="Have you been hacked?",
                inline_supported=True,
                hidden=False,
                required_args=1)
def pwned(_: Bot, update: Update, user, args):
    """
    Example usage:
    User: /pwned asdasdsad
    Bot: ✅Got cool news for you! You are NOT pwned!
    """
    account = " ".join(args)
    r = requests.get(
        "https://haveibeenpwned.com/api/v2/breachedaccount/%s" % account)
    if r.status_code == 404:
        return core.message(emojize(":white_check_mark:Got cool news for you! You are NOT pwned!", use_aliases=True))
    else:
        pwns = r.json()
        message = emojize(
            ":warning:<b>Oh No!</b> You have been <b>pwned</b>:\n<b>Leaked data:</b><i>")
        pwnedthings = {}
        pwnedsites = {}
        for pwn in pwns:
            pwnedsites.update({pwn["Title"]: pwn["Title"]})
            for data in pwn["DataClasses"]:
                pwnedthings.update({data: data})
        message += escape(", ".join(list(pwnedthings)))
        message += "</i>\n<b>From sites:</b><i>\n" + \
            escape("\n".join(list(pwnedsites))) + "</i>"
        return core.message(message, parse_mode="HTML")
