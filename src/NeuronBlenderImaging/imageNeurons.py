#we have to add script path to sys.path becuase 
#blender's cwd is where its special python install is being run
#there's certainly a better way to do this.
import os
import sys
import bpy #blender's module
import pynput #to emulate keyboard presses to center camera view in blender
import functools #to allow for callable functions with bpy.app.timers.register()

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
sys.path.insert(0, blendFileDir) #adding this path lets it work via the runExternalScript.py
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
    neuron_objs = sorted(blender_neurons.keys())
    print("Found %s neuron objects current Blender file" % len(neuron_objs))
    if len(neuron_objs) == 302:
        return neuron_objs
    else:
        raise ValueError("Neuron list is incomplete.")

def snapshot_neurons(blender_neurons):
    """selects valid neuron objects one by one
    hides the rest, orients the camera, 
    and takes snapshots from 3 perspectives"""
    neuron_name = blender_neurons[4]

    #for neuron_name in blender_neurons:
        #to avoid working directly with the blender API- I'm using the bpy.ops commands
        #bpy.ops commands are really picky about context.
        #so, we will change the text editor window to the desired window, and change it back after

    #set context so ops commands will work
    bpy.context.area.ui_type = "VIEW_3D"

    #unhide all
    print("unhiding all objects")
    bpy.ops.object.hide_view_clear()

    #deselect all
    print("deselect all objects")
    bpy.ops.object.select_all(action='DESELECT')

    #select object
    print("selecting neuron named: %s" %neuron_name)
    bpy.data.objects[neuron_name].select_set(True)
    #obj = bpy.context.scene.objects[neuron_name]

    #hide all objs but selected
    print("hiding all objects except: %s" %neuron_name)
    bpy.ops.object.hide_view_set(unselected=True)

    #center camera on object
    #I have read online centering the viewport camera isn't possible using Blender Python - so I gave up trying.
    #If you know how, please fix my hacky script.
    #Instead, I'm just going to use keyboard input emulation to center the camera.

    #define keyboard controller
    keyboard = pynput.keyboard.Controller()
    def press(x):
        keyboard.press(x)
        keyboard.release(x)
    #center camera on selected object
    def press_num(num):
        press(pynput.keyboard.KeyCode(num)) #the numpad must be use for camera controls in Blender
        #so we have to use specific keycode

    bpy.app.timers.register(functools.partial(press_num, 110), first_interval=6)
    bpy.app.timers.register(functools.partial(press_num, 97), first_interval=5)
    print("screenshot")
    bpy.app.timers.register(functools.partial(press_num, 99), first_interval=5)
    print("screenshot again")
    bpy.app.timers.register(functools.partial(press_num, 103), first_interval=5)










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
    #set context back now that we are done with the 'context-picky' ops commands
    #bpy.context.area.ui_type = "TEXT_EDITOR"

if __name__ == "__main__":
    main()