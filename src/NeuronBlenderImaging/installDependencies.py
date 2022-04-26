"""This script is to automate the process of install modules
Blender's internal version of Python

How to use it:
1. Open Blender with Admin permissions if Blender is 
    installed in the default location (at least with windows)
2. Open the scripting scene
3. Open the script in the "Text Editor" window
(Optionally click "Window" in the top left and then "Toggle System Console")
4. Push the play button to run the script
5. Wait despite it looking frozen 
(You can look at the system console if you opened it to comfort yourself)
"""
#WARNING THE MACOS AND LINUX FUNCTIONS ARE NOT CURRENTLY CODED
#if you are working on one of those OS's
#I trust you can follow my windows pleb example and run the commands for your own OS


#here are the dependencies that are required to run all of the scripts. 
dependencies = ["numpy", "pandas", "pyinput", "libneuroml", "xlrd", "matplotlib"]
#add any 3rd party dependencies that I missed

import os
import sys
import subprocess

#add NueronBlenderImaging folder to path
blendFileDir = os.path.dirname(os.path.realpath(__file__))
blenderWorkingPath = os.getcwd()
scriptPath = os.path.abspath(os.path.join(blendFileDir, "..", "..", "NeuronBlenderImaging"))
print("""
==============================PATH LOCATIONS==============================
blendFileDir %s
blenderWorkingPath %s
scriptPath %s\n\n""" % (blendFileDir, blenderWorkingPath, scriptPath))
#add scriptPath to Blender's CWD to allow install
sys.path.insert(0, scriptPath)


def install_4win():
    for package in dependencies:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

def install_4linux():
    #use the subprocess module to send commands to your console using bash
    #or whatever you linux peeps use

    #for package in dependencies:
        #subprocess.check_call([#enter in your commands here!!! package])
    pass

def install_4macos():
    #use the subprocess module to send commands to your console using zsh
    #or whatever you macos peeps use 

    #for package in dependencies:
        #subprocess.check_call([#enter in your commands here!!! package])
    pass


def main():
    win_systems = ["win32", "cygwin", "msys"]
    macos_systems = ["darwin", "os2", "os2emx"]
    linux_systems = ["linux", "linux2"]
    if sys.platform in win_systems:
        install_4win()
    elif sys.platform in linux_systems:
        install_4linux()
    elif sys.platform in macos_systems:
        install_4macos()

if __name__ == "__main__":
    main()