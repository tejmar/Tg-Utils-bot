# -*- coding: utf-8 -*-
import os
import sys
import reader
global INVALIDS
INVALIDS = 0
def check_locale(path=""):
    global INVALIDS
    path = os.path.normpath(path)
    if ((not path == ".") and path.startswith(".")) or path.startswith("_"):
        return
    print(" " * (len(os.path.split(path))-1),"Folder:", path, sep="")
    folders = []
    for item in os.listdir(path):
        npath = os.path.normpath(os.path.join(path, item))
        if item.endswith(".locale"):
            beautiful_path = " " * len(os.path.split(npath)) + npath
            try:
                reader.read(npath)
            except Exception as e:
                print(beautiful_path, "FAIL(%s)" % e)
                INVALIDS += 1
            else:
                print(beautiful_path, "is valid")
        elif os.path.isdir(npath):
            folders.append(npath)
    for folder in folders:
        check_locale(folder)

print("Checking json files for validness")
check_locale()
if INVALIDS:
    print("Validation FAILED")
    print("Invalid count:", INVALIDS)
    sys.exit(INVALIDS)