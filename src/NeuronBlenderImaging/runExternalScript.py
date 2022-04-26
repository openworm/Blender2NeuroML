#This is a template script which you can just reload to execute the script you're currently editing. 
#Just change the filename and path name.

import bpy
import os

#my blender script
filename = "imageNeurons.py"

#my blender path relative to the openworm file in the data directory
blendFileDir = os.path.dirname(os.path.realpath(__file__))
scriptPath = os.path.abspath(os.path.join(blendFileDir, "..", "..", "NeuronBlenderImaging", filename))

#commenent this out if you want to execute a script in the same directory as the blender file.
#scriptPath = os.path.join(os.path.dirname(bpy.data.filepath), filename)


global_namespace = {"__file__": scriptPath, "__name__": "__main__"}
with open(filepath, 'rb') as file:
    exec(compile(file.read(), filepath, 'exec'), global_namespace)
