"""Timezones"""
from telegram import Bot, Update
import pendulum
import core

from pytzdata.exceptions import TimezoneNotFound
TIMEFORMAT = 'dddd DD MMMM YYYY HH:MM'

PLUGINVERSION = 2
# Always name this variable as `plugin`
# If you dont, module loader will fail to load the plugin!
plugin = core.Plugin()


@plugin.command(command="/tz",
                description="Sends info about specifed zone(for example:Europe/Moscow)",
                inline_supported=True,
                required_args=1,
                hidden=False)
def timezonecmd(bot: Bot, update: Update, user, args):
    """
    Example usage:
    User: /tz Europe/Moscow
    Bot: Europe/Moscow: Friday 18 of August 2017 08:21:04
    """
    timezone = " ".join(args).replace(" ", "_")
    try:
        timezone = pendulum.now(timezone)
    except (TimezoneNotFound, ValueError, pendulum.tz.zoneinfo.exceptions.InvalidTimezone):
        return core.message("⚠You specifed unknown timezone", failed=True)
    else:
        return core.message(timezone.timezone_name + ": " + timezone.format(TIMEFORMAT))
