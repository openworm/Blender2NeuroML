#we have to add script path to sys.path becuase 
#blender's cwd is where its special python install is being run
#there's certainly a better way to do this.
import os
import sys
import bpy #blender's module

#add NueronBlenderImaging folder to path
blendFileDir = os.path.dirname(os.path.realpath(__file__))
blenderWorkingPath = os.getcwd()
scriptPath = os.path.abspath(os.path.join(blendFileDir, "..", "..", "NeuronBlenderImaging"))
print("""
==============================PATH LOCATIONS==============================
blendFileDir %s
blenderWorkingPath %s
scriptPath %s\n\n""" % (blendFileDir, blenderWorkingPath, scriptPath))
#add scriptPath to Blender's CWD to allow importing of BLENDER2NEUROML/src modules in Blender 
sys.path.insert(0, scriptPath)

#import local modules
import findPossibleNeurons as fpn

def read_neurons():
    """gets a list of possible blender objects from .Blend file
    gets a list of neurons from the xlsx file
    uses findPossibleNeurons to select neurons
    """
    #test like this and see if you can just throw it away
    # #specify paths
    # worm_file_dir = os.path.dirname(os.path.realpath(__file__))
    # script_path = os.path.abspath(os.path.join(worm_file_dir, "..", ".."))
    # #neurons_file = os.path.join(script_path, "Data", "neurons.complete.txt")

    #collect objects from .Blender
    blender_objects = []
    for obj in bpy.data.objects:
        blender_objects.append(obj.name) #make a list of all blender objects
    blender_neurons = fpn.find(blender_objects) #find known neurons with the findPossibleNeurons.py script
    return blender_neurons.keys()

def snapshot_neurons(blender_neurons):
    """selects valid neuron objects one by one
    hides the rest, orients the camera, 
    and takes snapshots from 3 perspectives"""


    for neuron_name in blender_neurons:
        # #so ops will work, I'll set the context to the 3d viewport window in blender
        view_layer = bpy.context.view_layer
        #unhide all
        # print("unhiding all objects")
        # bpy.ops.object.hide_view_clear()
        # #deselect all
        # print("deselect all objects")
        # bpy.ops.object.select_all(action='DESELECT')
        #select object
        print("selecting neuron named: %s" %neuron_name)
        obj = bpy.context.scene.objects[neuron_name]
        view_layer.objects.active = obj
        # #hide all objs but selected
        print("hiding all objects but %s" %neuron_name)
        bpy.ops.obj.hide_videw_set(unselected=True)
        # #center camera on object
        print("centering camera on %s" %neuron_name)
        bpy.ops.view3d.camera_to_view_selected() #possibly depriciated








    #deselect all objects
    # for ob in bpy.data.objects:
    #     if ob.name in neuron_names:
    #         ob.select_set(True)

    # scene_objects = []
    # for ob in bpy.data.objects:
    #     scene_objects.append(ob.name)
    # for neuron in neuron_names:
    #     if neuron not in scene_objects:
    #         print(neuron)
    #     else:
    #         scene_objects.remove(neuron)
    # for ob in scene_objects:
    #     print(ob)
    

def main():
    snapshot_neurons(read_neurons())

if __name__ == "__main__":
    main()