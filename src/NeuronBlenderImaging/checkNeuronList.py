"""This script is intended to run in Directly in Blender"""

from __future__ import absolute_import
#we have to add script path to sys.path becuase 
#blender's cwd is where its special python install is being run
#there's certainly a better way to do this.
import os
import sys
import bpy #blender's module

#add NueronBlenderImaging folder to path
blendFileDir = os.path.dirname(os.path.join(os.path.dirname(__file__)))
blenderWorkingPath = os.getcwd()
scriptPath = os.path.abspath(os.path.join(blendFileDir, "..", "..", "NeuronBlenderImaging"))
print("""
==============================PATH LOCATIONS==============================
blendFileDir %s
blenderWorkingPath %s
scriptPath %s\n\n""" % (blendFileDir, blenderWorkingPath, scriptPath))
#add scriptPath to Blender's CWD to allow importing of BLENDER2NEUROML/src modules in Blender 
#sys.path.insert(0, blendFileDir) #adding this path lets us run code via the runExternalScript.py
sys.path.insert(0, 'C:\\Users\\tyson\\Documents\\git\\Blender2NeuroML\\NeuronBlenderImaging\\')

print("script path %s" % scriptPath)
print("sys path %s" % sys.path[:])

#import local modules
import findPossibleNeurons as fpn

def read_neurons():
    """gets a list of possible blender objects from .Blend file
    gets a list of neurons from the xlsx file
    uses findPossibleNeurons to select neurons
    """
    #collect objects from .Blender
    blender_objects = []
    for obj in bpy.data.objects:
        blender_objects.append(obj.name)
    blender_neurons = fpn.find(blender_objects) #find known neurons with the findPossibleNeurons.py script
    neuron_objs = sorted(blender_neurons.keys())
    print("Found %s neuron objects current Blender file" % len(neuron_objs))
    if len(neuron_objs) == 302:
        return neuron_objs
    else:
        raise ValueError("Neuron list is incomplete.")

def write_file_objs():
    blender_obj_file = os.path.join(blendFileDir, "blenderFileObjs.txt")
    with open(blender_obj_file, "w", encoding="utf8") as f:
        for obj in bpy.data.objects:
            f.write(obj.name)

def main():
    #neuron_objs = read_neurons()
    write_file_objs()

if __name__ == "__main__":
    main()