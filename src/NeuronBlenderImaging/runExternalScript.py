"""This is an edited template script from Blender that I find useful
in writing code and debugging.
How to use:
1. Load this script in Blender (see installDependencies for this)
2. Type in your own script and path relative to the location of the Blender file
(be aware the the CWD of Blender is inside the Blender install, 
not where you are running the .blend file)
3. Push the play button (Hotkey: ALT+P) to run the specified script
4. Cry (I'm sorry you have to script for Blender)
"""

import bpy
import os

#my blender script
filename = "imageNeurons.py"

#my blender path relative to the openworm file in the data directory
blendFileDir = os.path.dirname(os.path.realpath(__file__))
scriptPath = os.path.abspath(os.path.join(blendFileDir, "..", "..", "NeuronBlenderImaging", filename))

#commenent this out if you want to execute a script in the same directory as the blender file.
#scriptPath = os.path.join(os.path.dirname(bpy.data.scriptPath), filename)


global_namespace = {"__file__": scriptPath, "__name__": "__main__"}
with open(scriptPath, 'rb') as file:
    exec(compile(file.read(), scriptPath, 'exec'), global_namespace)
