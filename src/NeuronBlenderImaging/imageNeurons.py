"""I really dislike Blender's API and its scant documentation.
Unless you're making a very specific mesh addon- it's useless.
That's the reason why this project only uses a few lines of blender code
and then does all the rest in python. Using the bpy module is terrible.
Running code in Blender's Python is also terrible.
It makes no sense. 
So I'm writing this script that will just simulate keypresses 
instead of working with the hellish Blender api"""

import pyautogui as gui
from time import sleep

obj_search_box = (190, 812)
gui.displayMousePosition()