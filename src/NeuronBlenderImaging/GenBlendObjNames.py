"""WHAT: This script generates a .txt file of all objs inside of a Blender File
WHY: It lets us check to see if the Virtual_Worm.blend has the 302 neurons
with the CheckBlendObjs.py script.
HOW: Run the script in Blender (3.1 is what I used) under the scripting workspace
See github readme for more details
WHERE: This script is in the Data folder, becuase Blender
WHICH:
"""

import os
import sys
import bpy #blender's API

def fild_file_path(file):
    blendFileDir = os.path.dirname(os.path.realpath(__file__))
    src_path = os.path.abspath(os.path.join(blendFileDir, "..", ".."))
    print(f"{src_path = }")
    for root, dirs, files in os.walk(src_path):
        for f in files:
            if f == file:
                file_dir_path = root
                return file_dir_path

def collect_blender_objs(path_to_worm):
    pass

def main():
    path_to_worm = os.path.dirname(__file__)
    print(f"{path_to_worm = }")
    print(fild_file_path("302.xlsx"))

if __name__ == "__main__":
    main()