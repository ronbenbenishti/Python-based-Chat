import sys, platform
from cx_Freeze import setup, Executable

includefiles = ['chat.ico']
includes = []
excludes = []
packages = []

def getTargetName():
    myOS = platform.system()
    if myOS == 'Linux':
        return "Client"
    elif myOS == 'Windows':
        return "Client.exe"
    else:   
        return "Client.dmg"
if sys.platform == "win32":
    base = "Win32GUI"

exe = Executable(
    script = "client.py",
    base = base,
    icon = "chat.ico",
    )

setup(
    name = "Chat",
    version = "1.2",
    description = "Chat client based python by Ron Benbenishti",
    author = "Ron Benbenishti",
    targetName = getTargetName(),
    executables = [exe],
    options = {'build_exe': {'includes':includes,'packages':packages,'include_files':includefiles}},
    copyright = 'Copyright (C) Ron Benbenishti'

    # shortcutName = 'PyChat client by Ron',                  # FOR MSI INSTALLERS
    # shortcutDir = r'%programfiles%\PyChat client',     # FOR MSI INSTALLERS
    )
