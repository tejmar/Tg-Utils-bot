from requests import get
from telegram_ui import catalog_provider
import html
import core
apiurl = "http://api.urbandictionary.com/v0/define"
message = """
Definition for <b>%(word)s</b> by %(author)s:
%(definition)s

Examples:
<i>
%(example)s
</i>
<a href="%(permalink)s">Link to definition on Urban dictionary</a>
"""
PLUGINVERSION = 2
# Always name this variable as `plugin`
# If you dont, module loader will fail to load the plugin!
plugin = core.Plugin("Urban dictionary")


def escape_definition(definition):
    for key, value in definition.items():
        if isinstance(value, str):
            definition[key] = html.escape(value)
    return definition


def get_definition(term, number, count=1):
    definition = get(apiurl, params={
        "term": term
    }).json()["list"]
    if len(definition) > 0:
        defs = []
        if count + number > len(definition):
            maxdef = len(definition)
        else:
            maxdef = count + number
        for i in range(number-1, maxdef-1):
            deftxt = definition[i]
            deftxt = escape_definition(deftxt)
            defs.append(catalog_provider.CatalogKey(message % deftxt))
        return defs, len(definition)
    else:
        raise IndexError("Not found")

catalog_provider.create_catalog(plugin, get_definition, ["/ud", "/urban"], "Searches for query on Urban dictionary")
