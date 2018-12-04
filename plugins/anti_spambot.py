import core
import telegram
import logging
PLUGINVERSION = 2
LOGGER = logging.getLogger("AntiSpamBot")
# Always name this variable as `plugin`
# If you dont, module loader will fail to load the plugin!
SPAMBOTS_RAW = """
@pollsc
@acing
@GroupManagerDomina
@GroupManagerDomina
@akeredbot
@pedoannihilation
@RcSmerdbot
@RCBAD_BOT
@PedoAnnihilation
@lipped_bot
@sbfdskvgld_bot
@akered
@floodmeh
@opsmerderdated
@DrogaPazza_bot
@herhhhhhhhhhhhhhhhhhhbot
@opsmserdedetgbot
@ilcristoBot
@opskekekekbot
@opsksksksk_bot
@BaudaStorm
@ssflood
@nasakedbot
@SsFlood
@AKED_BY_GANJIA
@Shitstorm
@AkedByGanjia
@SonounbravoebelloBot
@sorrowful
@sorrowful10bot
@Floodmeh
@otifaciao
@Mallibot
@uhdhuahs7dys7uhadsubot
@d17shdnam1j1kbot
@bd817udhausdhuhbot
@sorrowful
@xxxPLxxx_bot
@Missafricabot
@hscbot
@Vip835bot
@Hilal99bot
@Ripgroup
@d17shdnam1j1kbot
@dj1771ah1jaka1obot
@bd817udhausdhuhbot
@dag71suhaj1y7a1jbot
@mother
@githubchatbot
@eucodesmerdbot
@blunterblackbot
@TumblrItaliaBot
@NoEscape_bot
@DominioPubblicoBot
@TumblrITbot
@YoungAndreaBot
@AkedBaiAL
@CarabiniereDomina
@SiOkCiao
@Cowboys
@WSpammer
@Washere
@Figobot
@krystorm
@neon
@Carlo
@rewind
@FulmineModzYouTube
""".strip("\n")
SPAMBOTS = []
for sbot in SPAMBOTS_RAW.split("\n"):
    sbot = sbot.lower()
    if sbot.startswith("@"):
        SPAMBOTS.append(sbot[1:])
    else:
        SPAMBOTS.append(sbot)
SPAMBOTS = set(SPAMBOTS)
LOGGER.debug(SPAMBOTS)
plugin = core.Plugin()


@plugin.message(".*")
def spambot_detect(bot, update):
    if update.message.chat.type == "supergroup":
        for admin in update.message.chat.get_administrators():
            if admin.user.id == bot.get_me().id:
                if update.message and update.message.new_chat_members:
                    for new_user in update.message.new_chat_members:
                        for spambot in SPAMBOTS:
                            if new_user.username.lower().startswith(spambot):
                                for member in update.message.new_chat_members:
                                    try:
                                        bot.kickChatMember(update.message.chat.id, member.id)
                                    except (telegram.error.TelegramError, telegram.error.NetworkError):
                                        pass
                                try:
                                    bot.kickChatMember(update.message.chat.id, update.message.from_user.id)
                                except (telegram.error.TelegramError, telegram.error.NetworkError):
                                    pass
                                return "New bots and user who added them were kicked due to being in spamlist."


@plugin.message(".*")
def contains_pollsciemo_detection(bot, update):
    if len(update.message.text) > 500 and ("pollsciemo" in update.message.text.lower()
                                      or "shitstorm" in update.message.text.lower())\
                                      and update.message.chat.type == update.message.chat.SUPERGROUP:
        bot.sendMessage(update.message.chat.id, "Pollsciemo detected - trying to ban user and delete messages")
        update.message.delete()
        bot.kickChatMember(update.message.chat.id, update.message.from_user.id)
