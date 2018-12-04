import core
import settings

import os, sys
PLUGINVERSION = 2
# Always name this variable as `plugin`
# If you dont, module loader will fail to load the plugin!
plugin = core.Plugin()
ACCESS_DENIED = """
Access denied.
Access is denied.
Unauthorized access.
Illegal access.
This door is locked.
Entry forbidden.
Entry not permitted.
No unauthorized personnel.
You do not have access to this facility.
Sorry, you may not enter.
Sorry, this door is locked.
Please, move away from this area.
Please, move away from door.
You will not get in.
Entry is not an option.
Will we do this all day?
Move on immediately.
No. No. And NO.""".split("\n")[1:]
global access_try
access_try = 0

@plugin.command(command="//update",
                description="Performs git pull, git submodule update and stops bot",
                inline_supported=True,
                hidden=True)
def doupd(bot, update, user, args):
    global access_try
    if update.message.from_user.id == settings.ADMIN:
        os.system("git pull")
        os.system("git submodule update")
        os.system(sys.executable + " -m pip install --user -r requirements.txt")
        os.kill(os.getpid(), 9)
    else:
        if access_try > (len(ACCESS_DENIED) - 1):
            access_try = 0
        access_msg = ACCESS_DENIED[access_try]
        access_try += 1
        return core.message(text=access_msg)
