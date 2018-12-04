import core
from PIL import Image
from io import BytesIO
from telegram.error import BadRequest, TimedOut
import logging
LOGGER = logging.getLogger("Sticker Optimizer")
PLUGINVERSION = 2
maxwidth, maxheight = 512, 512
# Always name this variable as `plugin`
# If you dont, module loader will fail to load the plugin!
plugin = core.Plugin()

class NoImageProvided(ValueError): pass

def resize_sticker(image: Image):
    resz_rt = min(maxwidth / image.width, maxheight / image.height)
    sticker_size = [int(image.width * resz_rt), int(image.height * resz_rt)]
    if sticker_size[0] > sticker_size[1]:
        sticker_size[0] = 512
    else:
        sticker_size[1] = 512
    image = image.resize(sticker_size, Image.ANTIALIAS)
    io_out = BytesIO()
    quality = 80
    image.convert("RGBA").save(io_out, "PNG", quality=quality)
    while 1:
        quality -= 10
        io_out = BytesIO()
        image.save(io_out, "PNG", quality=quality)
        io_out.seek(0)
        if io_out.tell() < 358400:
            break
    io_out.seek(0)
    return io_out


def create_pack_name(bot, update):
    name = f"group_{str(update.message.chat_id)[1:]}_by_{bot.getMe().username}"
    return name


def get_chat_creator(chat):
    for admin in chat.get_administrators():
        if admin.status == 'creator':
            return admin.user.id

def get_file_id_from_message(message):
    if message.photo:
        LOGGER.debug(message.photo)
        fl = message.photo[-1]
    elif message.document:
        fl = message.document
    elif message.sticker:
        fl = message.sticker
    elif message.reply_to_message:
        fl = get_file_id_from_message(message.reply_to_message)
    else:
        raise NoImageProvided()
    return fl

def get_file_from_message(bot, update):
    io = BytesIO()
    file_id = get_file_id_from_message(update.message).file_id
    fl = bot.getFile(file_id)
    fl.download(out=io)
    io.seek(0)
    return Image.open(io)


@plugin.command(command="/sticker_optimize",
                description="Optimizes image/file for telegram sticker",
                inline_supported=False,
                hidden=False)
def sticker_optimize(bot, update, user, args):
    try:
        image = get_file_from_message(bot, update)
    except NoImageProvided:
        return core.message("No image as photo/file provided.")
    return core.message(file=resize_sticker(image))


@plugin.command("/group_pack_add", "Adds sticker to group stickerpack", inline_supported=False)
def sticker_add(bot, update, user, args):
    if update.message.chat.type != update.message.chat.PRIVATE:
        if len(args) > 0:
            emoji = args[0]
        else:
            emoji = "🤖"
        try:
            try:
                image = resize_sticker(get_file_from_message(bot, update))
            except NoImageProvided:
                return core.message("No image as photo/file provided.")
            try:
                bot.addStickerToSet(get_chat_creator(update.message.chat), create_pack_name(bot, update), image, emoji)
            except BadRequest:
                image.seek(0)
                try:
                    bot.createNewStickerSet(get_chat_creator(update.message.chat),
                                            create_pack_name(bot, update),
                                            f"{update.message.chat.title[:32]} by @{bot.getMe().username}",
                                            image,
                                            emoji)
                except BadRequest as e:
                    if str(e).lower() == "peer_id_invalid":
                        return core.message("Sorry, but I can't create group pack right now. Ask group creator to PM me and try again.", failed=True)
            sticker = bot.getStickerSet(create_pack_name(bot, update)).stickers[-1]
            return core.message(file=sticker.file_id)
        except TimedOut:
            return core.message("It seems like I got timed out when creating sticker, that is Telegram-side error. Please try again.", failed=True)
    else:
        return core.message("This command is for groups only, sorry!")