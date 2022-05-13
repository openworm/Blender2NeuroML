"""Blender's API isn't great for automating repetitive tasks like this. 
It runs code asynchronously and even when trying to use the queue module,
It just ignored my task ordering. (But maybe you could do it?)

So this is a pyautogui script that simulates key presses on my 1080p display.
It theoretically should work on other machines in the same workspace, but
I worry about things like aspect-ratio etc.

I will make it obvious what you need to change on your set-up to get it working.
Forgive me. This script is a sin against the ethics of computer science."""

#two edits I made to the OG Virtual Worm Project Blender Files:
#1 turned down cuticle transparency by editing viewport display alpha (to .25)
#2 set obj broswer search to be exact

import pyautogui as gui
import os
from time import sleep

#I put the machine specific vars up here. (I think I got them all.)
#You can use the find_mouse_location() function in main() to find the location of
#your own search box.  
using_2012_worm = False
search_box_location = (186, 814)
cuticle_viewport_unhide = (353, 98)
d = -40 #distance move up
p = 0.012 #how long to pause between actions (slower for slower comps)
if using_2012_worm:
    search_box_location = (184, 62)
    d = 250

x_start = 10
y_start = 10
ss_width = 500
ss_height = 500
screenshot_area = (x_start, y_start, ss_width, ss_height)

#How cool would it be if I could get the program to collect the inputs while the script was running?
#like: Click on the GUI workspace
#Click on the searchbox
#Now I'll just do my thing.


def find_mouse_location():
    """Use this function to find where your mouse is to edit mouse position
    Push ctrl+c to end"""
    gui.displayMousePosition()

def find_file(file_name):
    """Move up on dir on any os and searches all the of the dirs
    for the specified file name and returns the path"""
    up_one = os.path.abspath(os.path.join(os.getcwd(), ".."))
    for root, dirs, files in os.walk(up_one):
        if file_name in files:
            return os.path.join(root, file_name)
    raise RuntimeError("File '%s' not found" % file_name)

def read_neuron_file(file_name="neurons.complete.txt"):
    """Reads the neurons from file_name and returns a list of them
    so we can find and image them"""
    file_path = find_file(file_name) #navigate to the neurons.complete.txt file
    with open(file_path, encoding="utf8") as f:
        file = f.read().splitlines()
    return file

def safety_checks():
    #check resolution
    resolution = gui.size()
    my_resuolution = (1920, 1080)
    if resolution != my_resuolution:
        raise RuntimeError("""
        Your display resolution isn't "%s".
        It's actually %s.
        So Pyautogui is just going to actively make your day worse
        because it was designed for "%s" """ % (my_resuolution, resolution, my_resuolution))
    #check other things???

def create_screenshot_folder():
    if os.path.exists("NeuronScreenshots"):
        return
    os.mkdir("NeuronScreenshots")

def select_neuron(neuron="AVAR", multi_select=False):
    """select neurons
    search needs to be set to "exact match" """

    #click to select search box
    gui.click(search_box_location, duration=p)
    #delete old entry
    gui.press("backspace") 
    #type neuron name to find
    sleep(p)
    gui.typewrite(neuron)
    #move mouse just above search box to allow for search result selection
    gui.moveRel(0, d, duration=p)
    gui.click(duration=p)
    if multi_select:
        gui.hotkey("shift", "a")
    else:
        gui.press("a")
    gui.moveRel(0, d*-1, duration=p)

def select_cuticle():
    #click to select search box
    gui.click(search_box_location, duration=p)
    #delete old entry
    gui.press("backspace") 
    #type neuron name to find
    sleep(p)
    gui.typewrite("Cuticle")
    #move mouse to click Cuticle view
    gui.moveTo(cuticle_viewport_unhide, duration=p)
    gui.click(cuticle_viewport_unhide, duration=p)
    gui.click(cuticle_viewport_unhide, duration=p)


def frame_screenshot():
    """..."""
    #move to the left
    select_cuticle()
    gui.moveRel(300, 0, duration=p)
    gui.press("r")
    sleep(.3)
    #gui.click(search_box_location, duration=p)

def take_screenshot(neuron, view):
    """"""
    #make this path work for other os's
    folder_name = "NeuronScreenshots"
    filename = f"{neuron}_{view}.png"
    full_path = os.path.join(folder_name, filename)
    gui.screenshot(full_path, screenshot_area)


def image_neurons(neurons):
    safety_checks()
    create_screenshot_folder()
    select_neuron(neurons[0])
    frame_screenshot()
    #WE CANNOT SELECT MULTIPLE AT ONCE... SO....
    #We might have to just make everything transparent- remap the numkey
    #and finally just take the screenshots..... yikes

    
    #take_screenshot()
    # for neuron in neurons:
    #     select_neuron(neuron)

def main():
    neurons = read_neuron_file() #get the neurons from the .txt file
    image_neurons(neurons)
    take_screenshot("ADAL", "ortho")
    #find_mouse_location()


if __name__ == "__main__":
    main()