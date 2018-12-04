import logging
import csv
from io import StringIO

import requests

import core

PLUGINVERSION = 2
# Always name this variable as `plugin`
# If you dont, module loader will fail to load the plugin!
plugin = core.Plugin(name="Currency Converter")
CURR_TEMPLATE = """
%(in)s = %(out)s

<a href="http://free.currencyconverterapi.com/">Powered by Currency convert API</a>
"""
LOGGER = logging.getLogger("/cash")

def convert(in_c, out_c, count):
    rate = requests.get(
        "http://free.currencyconverterapi.com/api/v3/convert?compact=ultra",
        params={
            "q": in_c + "_" +  out_c
        }
    )
    LOGGER.debug(rate.text)
    rate = rate.json()
    if rate == {}:
        raise NameError("Invalid currency")
    else:
        out = {}
        out["in"] = "<b>%s</b> <i>%s</i>" % (count, in_c.upper())
        out["out"] = "<b>%s</b> <i>%s</i>" % (round(float(count)*float(list(rate.values())[0]), 2), out_c.upper())
        return out

@plugin.command(command=["/cash", "/currency"],
                description="Converts currency",
                inline_supported=True,
                required_args=3,
                hidden=False)
def currency(bot, update, user, args):
    """
    Powered by Yahoo Finance
    Example usage:

    User:
    /cash 100 RUB USD

    OctoBot:
    100 RUB = 1.66 USD

    8/7/2017 10:30pm
    Data from Yahoo Finance
    """
    if len(args) < 3:
        return core.message(text="Not enough arguments! Example:<code>/cash 100 RUB USD</code>",
                              parse_mode="HTML",
                              failed=True)
    else:
        try:
            rate = convert(args[1], args[-1], args[0])
        except NameError:
            return core.message('Bad currency name', failed=True)
        else:
            return core.message(CURR_TEMPLATE % rate, parse_mode="HTML", extra_args={"disable_web_page_preview":True})
