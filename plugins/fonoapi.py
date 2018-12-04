import core
import html
import requests
import settings
from telegram_ui import catalog_provider
assert settings.FONOAPI_TOKEN
BASE =  requests.get("https://fonoapi.freshpixl.com/v1/getdevice", params={
        "token":settings.FONOAPI_TOKEN,
        "device":"samsung galaxy s8"
        }).json()[0]
for k, v in BASE.items():
    BASE[k] = "N/A"
INFO = """
<b>%(DeviceName)s</b> by <i>%(Brand)s</i>
Runs <b>%(os)s</b> on <b>%(chipset)s</b>
<b>Status:</b> <i>%(status)s</i>
<b>CPU:</b> <i>%(cpu)s</i>
<b>GPU:</b> <i>%(gpu)s</i>
<b>Battery:</b> <i>%(battery_c)s</i>
<b>NFC:</b> <i>%(nfc)s</i>
<b>Sensors:</b> <i>%(sensors)s</i>
<b>Memory:</b> <i>%(internal)s</i>
<b>Supported networks:</b> <i>%(technology)s</i>
<b>Dimensions:</b> <i>%(dimensions)s</i>
<b>SIM card(s):</b> <i>%(sim)s</i>
<b>Display:</b> <i>%(type)s, %(size)s, %(resolution)s</i>
<b>USB:</b> <i>%(usb)s</i>
<b>3.5 jack:</b> <i>%(_3_5mm_jack_)s</i>
<b>Primary camera:</b> <i>%(primary_)s</i>
<b>Secondary camera:</b> <i>%(secondary)s</i>
<b>2G Bands:</b> <i>%(_2g_bands)s</i>
<b>3G Bands:</b> <i>%(_3g_bands)s</i>
<b>4G Bands:</b> <i>%(_4g_bands)s</i>
"""
PLUGINVERSION = 2
# Always name this variable as `plugin`
# If you dont, module loader will fail to load the plugin!
plugin = core.Plugin(name="Fono API")
def fonoapi(term, number, count=1):
    r = requests.get("https://fonoapi.freshpixl.com/v1/getdevice", params={
        "token":settings.FONOAPI_TOKEN,
        "device":term
        }).json()
    if "status" in r and r["status"] == "error":
        raise IndexError("Not found")
    else:
        devices = []
        if count + number > len(r):
            maxdev = len(r)
        else:
            maxdev = count + number
        for i in range(number-1, maxdev):
            device = dict(BASE) # Avoid changes to BASE
            device.update(r[i])
            for k, v in device.items():
                device[k] = html.escape(v.replace("\n", "/"))
            devices.append(catalog_provider.CatalogKey(INFO % device))
        return devices, len(r)

catalog_provider.create_catalog(plugin, fonoapi, ["/phone"], "Fono API Search")
