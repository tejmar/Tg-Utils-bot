try:
    import core
except ModuleNotFoundError:
    import os
    import sys
    import inspect
    currentdir = os.path.dirname(os.path.abspath(
        inspect.getfile(inspect.currentframe())))
    parentdir = os.path.dirname(currentdir)
    sys.path.insert(0, parentdir)
    import plugins.admin
import json
from glob import glob
from tqdm import tqdm

print("Importing username database...")
with open("plugdata/admin/usernames.json", 'r', encoding="utf-8") as f:
    usernames = json.load(f)
for uid, username in tqdm(usernames.items(), unit="usernames"):
    plugins.admin.get_user(uid=uid, username=username)

print("Importing chat warns...")
for chat in tqdm(glob("plugdata/admin/chat-*.json"), unit="chats"):
    with open(chat, 'r', encoding='utf-8') as f:
        chat_json = json.load(f)
        chat = plugins.admin.get_chat(chat.split("chat")[1].rstrip(".json"))
        chat.maxwarns = chat_json["maxwarns"]
        for user, warns in chat_json["warns"].items():
            for warn in warns:
                uwarn = chat.warns.create(target=plugins.admin.get_user(
                    uid=user), reason=warn[1][:280], warn_id=warn[0].lstrip("#warn")[:8])
                uwarn.save()
