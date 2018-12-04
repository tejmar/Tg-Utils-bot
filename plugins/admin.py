import core
import random
import string
import telegram
import settings
from logging import getLogger
import mongoengine
LOCALE_STR = core.locale.get_locales_dict("admin")
LOGGER = getLogger("Admin-Plugin")
PLUGINVERSION = 2


def gen_id():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
# MONGO STUFF


mongoengine.connect(host=settings.MONGO_DB_HOST,
                    port=settings.MONGO_DB_PORT, db=settings.MONGO_DB_NAME)


class UserNotFound(ValueError):
    pass


class User(mongoengine.Document):
    username = mongoengine.StringField(max_length=33)
    telegram_id = mongoengine.StringField(max_length=32)


class Warn(mongoengine.EmbeddedDocument):
    target = mongoengine.ReferenceField(User)
    warn_id = mongoengine.StringField(min_length=8, max_length=8)
    reason = mongoengine.StringField(max_length=280)


class Chat(mongoengine.Document):
    warns = mongoengine.EmbeddedDocumentListField(Warn)
    maxwarns = mongoengine.IntField(min_value=2, max_value=10)
    chat_id = mongoengine.StringField(max_length=32)


def get_chat(chat_id):
    chat = Chat.objects(chat_id=str(chat_id))
    if chat.count() == 0:
        chat = Chat()
        chat.warns = []
        chat.chat_id = str(chat_id)
        chat.maxwarns = 3
        chat.save()
    else:
        chat = chat[0]
    return chat


def get_user(uid=None, username=None):
    if uid is not None:
        user = User.objects(telegram_id=str(uid))
        if user.count() == 0:
            user = User()
            user.telegram_id = str(uid)
            user.username = username
            user.save()
        else:
            user = user[0]
            if username is not None:
                user.username = username
            user.save()
        return user
    if username is not None:
        user = User.objects(username=username)
        if user.count == 0:
            raise UserNotFound("No user with such username was found!")
        else:
            return user[0]
    raise ValueError("No arguments specified!")

# TELEGRAM STUFF


class AdminMessage(core.message):
    def post_init(self):
        core.message.post_init(self)
        self.reply_to_prev_message = False


def is_admin(user_id, chat):
    if chat.type == chat.SUPERGROUP:
        for admin in chat.get_administrators():
            if user_id == admin.user.id or str(user_id) == str(settings.ADMIN):
                return True
        return False
    else:
        return False


class AdminOnly():
    def __init__(self, f):
        LOGGER.debug("Got admin_only attached to %s", f)
        self.function = f

    def __call__(self, bot, update, user, args):
        def _(x): return core.locale.get_localized(x, update.message.chat.id)
        if update.message.chat.type == "supergroup":
            if is_admin(bot.getMe().id, update.message.chat):
                if is_admin(user.id, update.message.chat):
                    # Defining target
                    target = None
                    if update.message.reply_to_message:
                        target = get_user(username=update.message.reply_to_message.from_user.username,
                                          uid=update.message.reply_to_message.from_user.id)
                        reason = " ".join(args)
                    elif len(args) > 0:
                        if args[0].isdigit():
                            target = get_user(uid=args[0])
                            if len(args) > 1:
                                reason = " ".join(args[1:])
                            else:
                                reason = ""
                        elif args[0].startswith("@"):
                            try:
                                target = get_user(username=args[0].strip("@"))
                            except UserNotFound:
                                return AdminMessage(_(LOCALE_STR["invalid_id"]), failed=True)
                            if len(args) > 1:
                                reason = " ".join(args[1:])
                            else:
                                reason = ""
                    # Executing command
                    if target is not None:
                        if not is_admin(target.telegram_id, update.message.chat):
                            return self.function(bot, update.message.chat, target, user, reason)
                        else:
                            return AdminMessage(_(LOCALE_STR["banning_admin"]))
                    else:
                        return AdminMessage(_(LOCALE_STR["no_target"]))
                else:
                    return AdminMessage(_(LOCALE_STR["insufficient_permissions"]), failed=True)
            else:
                return
        else:
            return AdminMessage(_(LOCALE_STR["not_supergroup"]))


plugin = core.Plugin()


@plugin.message(regex=".*")
def user_overseer(bot, update):
    get_user(uid=update.message.from_user.id,
             username=update.message.from_user.username)
    return


@plugin.command(command="/getwarns",
                description="Shows your warn count",
                inline_supported=False,
                hidden=False)
def warncount(bot, update, user, args):
    def _(x): return core.locale.get_localized(x, update.message.chat.id)
    if update.message.chat.type == "supergroup":
        data = {"user": user.first_name}
        warns = get_chat(update.message.chat.id).warns.filter(
            target=get_user(uid=str(user.id)))
        data["count"] = warns.count()
        data["warns"] = ""
        for warn in warns:
            data["warns"] += "#warn%s - %s" % (warn.warn_id, warn.reason)
        return AdminMessage(text=_(LOCALE_STR["warns"]) % data)
    else:
        return AdminMessage(text=_(LOCALE_STR["not_supergroup"]), failed=True)


@plugin.command(command="/warn",
                description="Warns user. Max length for reason: 280 symbols",
                inline_supported=False)
@AdminOnly
def warn_command(bot, chat, target, admin, reason):
    def _(x): return core.locale.get_localized(x, chat.id)
    data = {
        "target": target.telegram_id,
        "user": target.username,
        "adminid": admin.id,
        "admin": admin.first_name
    }
    chat_db = get_chat(chat.id)
    uwarn = chat_db.warns.create(target=get_user(
        uid=target.telegram_id), reason=reason, warn_id=gen_id())
    uwarn.save()
    userwarns = chat_db.warns.filter(target=get_user(uid=target.telegram_id))
    LOGGER.debug(userwarns)
    data["current"] = userwarns.count()
    data["reason"] = reason
    data["max"] = chat_db.maxwarns
    data["warn_id"] = "#warn" + str(uwarn.warn_id)
    if data["current"] >= data["max"]:
        userwarns.delete()
        userwarns.save()
        bot.kickChatMember(chat.id, target.telegram_id)
        return AdminMessage(_(LOCALE_STR["reached_maximum_warns"]) % data, parse_mode="HTML")
    else:
        return AdminMessage(_(LOCALE_STR["was_warned"]) % data, parse_mode="HTML")


@plugin.command(command="/unwarn",
                description="Removes warn from user.",
                inline_supported=False)
@AdminOnly
def unwarn_command(bot, chat, target, admin, reason):
    def _(x): return core.locale.get_localized(x, chat.id)
    data = {
        "target": target.telegram_id,
        "user": target.username,
        "adminid": admin.id,
        "admin": admin.first_name
    }
    chat_db = get_chat(chat.id)
    userwarns = chat_db.warns.filter(target=get_user(uid=target.telegram_id))
    LOGGER.debug(userwarns)
    if userwarns.count() == 0:
        return AdminMessage(_(LOCALE_STR["cant_unwarn"]) % data, parse_mode="HTML", failed=True)
    else:
        LOGGER.debug("Entries deleted: %s", userwarns.filter(
            warn_id=userwarns[0].warn_id).delete())
        chat_db.save()
        userwarns = chat_db.warns.filter(
            target=get_user(uid=target.telegram_id))
        data["current"] = userwarns.count()
        data["max"] = chat_db.maxwarns
        return AdminMessage(_(LOCALE_STR["warn_removed"]) % data, parse_mode="HTML")


@plugin.command(command="/kick",
                description="Kicks user from chat",
                inline_supported=False)
@AdminOnly
def kick_command(bot, chat, target, admin, reason):
    def _(x): return core.locale.get_localized(x, chat.id)
    data = {
        "target": target.telegram_id,
        "user": target.username,
        "adminid": admin.id,
        "admin": admin.first_name
    }
    chat_db = get_chat(chat.id)
    userwarns = chat_db.warns.filter(target=get_user(uid=target.telegram_id))
    userwarns.delete()
    chat_db.save()
    bot.kickChatMember(chat.id, target.telegram_id)
    bot.unbanChatMember(chat.id, target.telegram_id)
    return AdminMessage(_(LOCALE_STR["was_kicked"]) % data, parse_mode="HTML")


@plugin.command(command="/ban",
                description="Bans user from chat",
                inline_supported=False)
@AdminOnly
def ban_command(bot, chat, target, admin, reason):
    def _(x): return core.locale.get_localized(x, chat.id)
    data = {
        "target": target.telegram_id,
        "user": target.username,
        "adminid": admin.id,
        "admin": admin.first_name
    }
    chat_db = get_chat(chat.id)
    userwarns = chat_db.warns.filter(target=get_user(uid=target.telegram_id))
    userwarns.delete()
    chat_db.save()
    bot.kickChatMember(chat.id, target.telegram_id)
    return AdminMessage(_(LOCALE_STR["was_banned"]) % data, parse_mode="HTML")
