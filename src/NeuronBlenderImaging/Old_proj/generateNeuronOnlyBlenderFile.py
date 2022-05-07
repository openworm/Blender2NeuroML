"""This takes the standard .Blend virtual worm file
1. identifies all of neurons
2. puts them in a single collection
3. deletes all non neurons

Note:
If you are using a different .Blend file than the one included in this repo,
then you will have to manually purge the orphan data left behind by the Visual Worm team. 
(Why purge? Well, because Blender includes Orphan objects in bpy.data.objects-- and I can't figure out
how to delete those objects using Blender's API. The delete commands just choke on orphan objects.)
TO PURGE THE ORPHAN DATA:
1. Change to the "1 - Animation" workspace.
2. At the bottom of the object browser, click on the displaymode button- set it to "orphan data".
3. Now click purge to delete all orphan data.
4. Wait until tomorrow and the file is done loading.  
5. Save and reload the file. 
"""

import os
import sys
import bpy #blender's module

#add NueronBlenderImaging folder to path
blendFileDir = os.path.dirname(os.path.realpath(__file__))
blenderWorkingPath = os.getcwd()
print(os.getcwd())
scriptPath = os.path.abspath(os.path.join(blendFileDir, "..", "..", "NeuronBlenderImaging"))
print("""
==============================PATH LOCATIONS==============================
blendFileDir %s
blenderWorkingPath %s
scriptPath %s\n\n""" % (blendFileDir, blenderWorkingPath, scriptPath))
#add scriptPath to Blender's CWD to allow importing of BLENDER2NEUROML/src modules in Blender 
sys.path.insert(0, blendFileDir) #adding this path lets us run code via the runExternalScript.py
sys.path.insert(0, scriptPath)

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
    print("Found %s neuron objects current Blender file" % len(blender_neurons))
    if len(blender_neurons) == 302:
        return blender_neurons
    else:
        raise ValueError("Neuron list is incomplete.")

def delete_non_neurons(neuron_dict):
    bpy.context.area.ui_type = "VIEW_3D"

    #obvs hash maps are faster for "in" checks O(1)
    print(len(bpy.data.objects))

    # for e in [e for e in bpy.data.objects if not e.data]:
    #     bpy.data.objects.remove(e, do_unlink=True)
    # print(len(bpy.data.objects))


    for obj in bpy.data.objects:
        if obj.name not in neuron_dict and obj.type == "MESH":
            try:
                #print("obj.name = %s --- obj.type = %s" % (obj.name, obj.type))
                bpy.ops.object.select_all(action='DESELECT')
                bpy.data.objects[obj.name].select_set(True)
                print("selected object named %s" %obj.name)
            except RuntimeError:
                print("%s is ignored because it's not on the correct view layer." % obj.name)



    # print(non_neurons)
    # print(len(non_neurons))
    # print("deselect all objects")
    

    #print("selecting neuron named: %s" %non_neurons)
    
    #obj = bpy.context.scene.objects[neuron_name]

    # print("hiding all objects except: %s" %non_neurons)
    # bpy.ops.object.hide_view_set(unselected=True)
            




def main():
    neuron_dict = read_neurons()
    delete_non_neurons(neuron_dict)

if __name__ == "__main__":
    main()