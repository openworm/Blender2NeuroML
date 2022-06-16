"""
WHY DID I USE PYAUTOGUI?
Blender's API isn't great for automating repetitive tasks like this.
It seems to run code asynchronously and even when trying to use the queue module,
It just ignored my task ordering. (But maybe you could do it?)
So this is a pyautogui script that simulates key presses on my 1080p display.
It theoretically should work on other machines in the same workspace, but
I worry about things like aspect-ratio etc.
I tried to make it obvious what you need to change on your set-up to get it working.
Forgive me. This script is a sin against the ethics of computer science.
 
HOW TO USE?
1. Open the Blender file (I used Virtual_Worm_Neuron_Only_March_2011_with_skin.blend)
2. Click on the GUI workspace tab
3. Comment out image_neurons() and uncomment the find_mouse_location() function in main()
4. Enter in machine specific info
5. Run the script as admin in your terminal or IDE
 
******IMPORTANT******
IF AN ERROR OCCURS:
Slam the mouse into the top left corner of your display.
This will trigger pyautogui's failsafe option and stop the script from running.
"""
 

#two edits I made to the OG Virtual Worm Project Blender Files:
#1 turned down cuticle transparency by editing viewport display alpha (to .25)
#2 set obj browser search to be exact (click the funnel on the object browser in Blender- then click "exact match")
#3 turned the camera focus from ("num." to "r" because pyautogui doesn't have "num." key)
#4 I turned hide all [normally ("shift" + "h")] to ("ctrl" + "h") because the pyautogui shift key won't work in Blender
 
 
import pyautogui as gui
import os
from time import sleep
 

"""ENTER MACHINE SPECIFIC INFO HERE
Use find_mouse_location() in main() to find locations"""
using_2012_worm = False
search_box_location = (186, 814) #the location of the search box in the outliner scene
viewport_distance_from_search_box = 500 #how far the mouse needs to move to the left from the outliner to click onto the 3D viewport
cuticle_viewport_unhide = (353, 98) #the exact location of the hide/unhide eyeball icon in the outliner after you type "cuticle" into the outliner search
view_port_top_edge = (468, 102) #the top left edge of the 3D viewport (you just don't want to click on an object, but you shouldn't have to worry because it zooms out to avoid that)
d = -40 #distance move up from the outliner search to click on the non-search outliner portion to allow the "a" command to select all
p = 0.012 #how long to pause between actions (slower for slower comps)
p = 0.02
if using_2012_worm:
    search_box_location = (184, 62)
    d = 250 #this is below in the 2012 file while the 2011 is above
 
#the screenshot area for the 3D viewport
#the top left of the screenshot x,y
x_start = 465 
y_start = 52
ss_width = 1358
ss_width = 1430
ss_height = 947
screenshot_area = (x_start, y_start, ss_width, ss_height)


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

def create_screenshot_folder():
    if os.path.exists("NeuronScreenshots"):
        return
    os.mkdir("NeuronScreenshots")

def select_neuron(neuron="AVAR"):
    """select neurons
    search needs to be set to "exact match" """
    #unhide all objs
    gui.click(view_port_top_edge, duration=p)
    gui.hotkey("alt", "h")
    #deselect all objects
    gui.press("a")
    gui.press("a")
    #click to select search box
    gui.click(search_box_location, duration=p)
    gui.click(search_box_location, duration=p)
    sleep(p*8)
    gui.hotkey("ctrl", "a")
    sleep(p*5)
    #delete old entry
    gui.press("backspace") 
    #type neuron name to find
    sleep(p*20)
    gui.typewrite(neuron)
    #move mouse just above search box to allow for search result selection
    gui.moveRel(0, d, duration=p)
    gui.click(duration=p)
    gui.press("a")
    gui.moveRel(0, d*-1, duration=p)
    #hide all objs
    gui.moveRel(viewport_distance_from_search_box, 0, duration=p)

    gui.hotkey("ctrl", "h") #I changed the hotkey. Shift H wasn't working... why...?
    gui.moveRel(-viewport_distance_from_search_box, 0, duration=p)


def unhide_cuticle():
    #click to select search box
    gui.click(search_box_location, duration=p)
    #delete old entry
    gui.press("backspace") 
    #type neuron name to find
    sleep(p*16)
    gui.typewrite("Cuticle")
    #move mouse to click Cuticle view
    gui.moveTo(cuticle_viewport_unhide, duration=p)
    gui.click(cuticle_viewport_unhide, duration=p)
    gui.click(cuticle_viewport_unhide, duration=p)

def frame_screenshot():
    """..."""
    #move to the left
    gui.moveRel(viewport_distance_from_search_box, 0, duration=p)
    #centers camera on neuron
    gui.press("r") #had to change hotkey for "num." pyautogui doesn't have that option
    sleep(p*16)

def take_screenshot(neuron, view):
    """"""
    screenshot_pause = p*16
    #make this path work for other os's
    if view == "front":
        gui.press("num1")
        sleep(screenshot_pause)
    if view == "side":
        gui.press("num3")
        sleep(screenshot_pause)
    if view == "top":
        gui.press("num7")
        sleep(screenshot_pause)
    folder_name = "NeuronScreenshots"
    filename = f"{neuron}_{view}.png"
    full_path = os.path.join(folder_name, filename)
    gui.screenshot(full_path, screenshot_area)


def image_neurons(neurons):
    safety_checks()
    create_screenshot_folder()

    for neuron in neurons[:]: #if you get some bad neurons, you can specify the range here based on the 302.xlsx file
        select_neuron(neuron)
        #unhide_cuticle()
        frame_screenshot()
        take_screenshot(neuron, "front")
        take_screenshot(neuron, "side")
        take_screenshot(neuron, "top")
        #zoom out to avoid accidnetly clicking on anything when switching to 3D Viewport
        gui.scroll(-5000)
        sleep(p*8)

    #Use this is if you have issues with specific neurons
    # specific_neuron = "PDA"
    # select_neuron(specific_neuron)
    # unhide_cuticle()
    # frame_screenshot()
    # take_screenshot(specific_neuron, "front")
    # take_screenshot(specific_neuron, "side")
    # take_screenshot(specific_neuron, "top")
    # gui.scroll(-5000)
    # sleep(p*8)

def main():
    neurons = read_neuron_file() #get the neurons from the .txt file
    image_neurons(neurons)
    #find_mouse_location() #push ctrl + c on while the terminal is selected to stop.


if __name__ == "__main__":
    main()