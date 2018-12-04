from telegram import Bot, Update  # Telegram core stuff
from telegram import InlineKeyboardMarkup, InlineKeyboardButton  # Inline UI
from telegram import InlineQueryResultArticle, InlineQueryResultGif, InputTextMessageContent
from uuid import uuid4
import core
import re

def cleanhtml(raw_html):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext

class CatalogKey:
    def __init__(self, text, image=None, thumbnail=None, is_gif=False):
        self.text = text
        self.image = image
        self.thumbnail = thumbnail
        self.is_gif = is_gif
        if thumbnail is None:
            self.thumbnail = self.image

    def __str__(self):
        text = str(self.text)
        if self.image:
            text = f'<a href="{self.image}">\u00a0</a>{text}'
        return text


def create_catalog(plugin, get_definition, command, description):
    if isinstance(command, list):
        cmdpref = command[0][1:]
    else:
        cmdpref = command[1:]

    @plugin.command(command=command,
                    description=description,
                    inline_hidden=True,
                    required_args=1,
                    hidden=False)
    def catalog_search(_: Bot, ___: Update, user, args):
        defnum = 1
        if len(args) > 0:
            term = " ".join(args)
            try:
                definition = get_definition(term, defnum)
            except IndexError:
                return core.message("Nothing found!", failed=True)
            else:
                kbd = InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton(text="⬅️", callback_data=cmdpref+":bwd:" +
                                             str(defnum) + ":" + term + ":" + str(definition[1])),
                        InlineKeyboardButton(
                            text="1/" + str(definition[1]), callback_data="none"),
                        InlineKeyboardButton(text="➡️", callback_data=cmdpref+":fwd:" +
                                             str(defnum) + ":" + term + ":" + str(definition[1]))
                    ]
                ])
                if len(definition[0]) > 0:
                    definition = definition[0][0]
                    return core.message(str(definition), parse_mode="HTML", inline_keyboard=kbd)
                else:
                    return core.message("Nothing found!", failed=True)
        else:
            return core.message("You hadn't supplied the query!", failed=True)

    @plugin.inline_button(cmdpref)
    def catalog_switch(bot, update, query):
        data = query.data.split(":")
        term = data[3]
        defnum = None
        if data[1] == "fwd":
            if not int(data[2]) + 1 > int(data[-1]):
                defnum = int(data[2])+1
        elif data[1] == "bwd":
            if not int(data[2]) - 1 <= 0:
                defnum = int(data[2]) - 1
        if (not data[2] == defnum) and defnum:
            definition = get_definition(term, defnum)
            kbd = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(text="⬅️", callback_data=cmdpref+":bwd:" +
                                         str(defnum) + ":" + term + ":" + str(definition[1])),
                    InlineKeyboardButton(
                        text=str(defnum) + "/" + str(definition[1]), callback_data="none"),
                    InlineKeyboardButton(text="➡️", callback_data=cmdpref+":fwd:" +
                                         str(defnum) + ":" + term + ":" + str(definition[1]))
                ]
            ])
            query.edit_message_text(str(definition[0][0]), parse_mode="HTML", reply_markup=kbd)
            if data[1] == "fwd":
                query.answer("Switched to next entry")
            else:
                query.answer("Switched to previous entry")
        else:
            query.answer("This wont do anything.")

    @plugin.inline_command(command)
    def catalog_inline(bot, query):
        term = " ".join(query.split(" ")[1:])
        results = []
        if len(term) > 0:
            try:
                definitions = get_definition(term, 1, count=25)
            except IndexError as e:
                if str(e) == "Not found":
                    return []
                else:
                    raise e
            for definition in definitions[0]:
                input_mes = InputTextMessageContent(str(definition), 
                                                    parse_mode="HTML")
                if definition.is_gif:
                    results.append(InlineQueryResultGif(id=uuid4(),
                                                        title=plugin.name,
                                                        description=cleanhtml(definition.text),
                                                        gif_url=definition.image,
                                                        thumb_url=definition.thumbnail,
                                                        hide_url=True,
                                                        input_message_content=input_mes))       
                else:
                    results.append(InlineQueryResultArticle(id=uuid4(),
                                                        title=plugin.name,
                                                        description=cleanhtml(definition.text),
                                                        thumb_url=definition.thumbnail,
                                                        hide_url=True,
                                                        input_message_content=input_mes))
        return results

    return True
