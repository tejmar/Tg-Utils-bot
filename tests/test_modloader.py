try:
    import core
except ModuleNotFoundError:
    import os,sys,inspect
    currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    parentdir = os.path.dirname(currentdir)
    sys.path.insert(0,parentdir) 
    import core
import os.path
import telegram
from hypothesis import given
from hypothesis.strategies import text
from datetime import datetime
import logging
USER = telegram.User(0, "Test User", is_bot=False, username="testuser")
CHAT = telegram.Chat(0, "private")
def test_load_plugin():
    ml = core.core.OctoBotCore(load_all=False)
    assert ml.load_plugin(os.path.normpath("examples/Command.py"))

def test_handle_inline_button():
    ml = core.core.OctoBotCore(load_all=False)
    ml.load_plugin(os.path.normpath("examples/InlineButton.py"))
    update = telegram.CallbackQuery('0',
            data="hello", from_user=USER, chat_instance='0')
    assert ml.handle_inline_button(update) == ml.plugins[0].inline_buttons["hello"]

def test_handle_command():
    ml = core.core.OctoBotCore(load_all=False)
    ml.load_plugin(os.path.normpath("examples/Command.py"))
    update = telegram.Update(1,
                             message=telegram.Message('0',
                                                      from_user=USER,
                                                      chat=CHAT,
                                                      date=datetime.now(),
                                                      text="/hi"))
    assert ml.handle_command(update) == ml.plugins[0].commands[0].execute

@given(text())
def test_handle_message(s):
    ml = core.core.OctoBotCore(load_all=False)
    ml.load_plugin(os.path.normpath("examples/Message.py"))
    update = telegram.Update(1,
                             message=telegram.Message('0',
                                                      from_user=USER,
                                                      chat=CHAT,
                                                      date=datetime.now(),
                                                      text=s))
    assert ml.handle_message(update) == [ml.plugins[0].message_handlers[".*"]]
