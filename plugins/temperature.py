import core
PLUGINVERSION = 2
# Always name this variable as `plugin`
# If you dont, module loader will fail to load the plugin!
plugin = core.Plugin()


def convert(temp, unit):
    unit = unit.lower()
    if unit == "c":
        temp = 9.0 / 5.0 * temp + 32
        return "%s degrees Fahrenheit" % round(temp, 2)
    if unit == "f":
        temp = (temp - 32) / 9.0 * 5.0
        return "%s degrees Celsius" % round(temp, 2)


@plugin.command(command="/temp",
                description="Converts temparture",
                inline_supported=True,
                required_args=1,
                hidden=False)
def temperatures(bot, update, user, args):
    """
    Converts temp from Celsius to Fahrenheit and Backwards
    Example usage:
    User:/temp 3C
    Bot:37.4 degrees Fahrenheit
    User:/temp 37.4F
    Bot:3.0 degrees Celsius
    """
    out = ""
    if args[0].upper().endswith("C") or args[0].upper().endswith("F"):
        unit = args[0][-1]
        temp = float(args[0][:-1])
    else:
        unit = args[-1]
        temp = float(args[0])
    out = convert(temp, unit)
    return core.message(text=out)
