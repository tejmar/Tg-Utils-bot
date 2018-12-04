from PyLyrics import *
from telegram import Bot, Update
import core
LYRICSINFO = "\n[Full Lyrics](http://lyrics.wikia.com/wiki/%s:%s)"

PLUGINVERSION = 2
# Always name this variable as `plugin`
# If you dont, module loader will fail to load the plugin!
plugin = core.Plugin()


@plugin.command(command="/lyrics",
                description="Looks up for lyrics",
                inline_supported=True,
                hidden=False,
                required_args=3)
def lyrics(_: Bot, update: Update, user, args):
    song = " ".join(args).split("-")
    if len(song) == 2:
        while song[1].startswith(" "):
            song[1] = song[1][1:]
        while song[0].startswith(" "):
            song[0] = song[0][1:]
        while song[1].endswith(" "):
            song[1] = song[1][:-1]
        while song[0].endswith(" "):
            song[0] = song[0][:-1]
        try:
            lyrics = "\n".join(PyLyrics.getLyrics(
                song[0], song[1]).split("\n")[:20])
        except ValueError as e:
            return core.message("❌ Song %s not found :(" % song[1], failed=True)
        else:
            lyricstext = LYRICSINFO % (song[0].replace(
                " ", "_"), song[1].replace(" ", "_"))
            return core.message(lyrics + lyricstext, parse_mode="MARKDOWN")
    else:
        return core.message("Invalid syntax!", failed=True)
