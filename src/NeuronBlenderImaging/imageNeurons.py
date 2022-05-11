"""Blender's API isn't great for automating repetitive tasks like this. 
It runs code asynchronously and even when trying to use the queue module,
It just ignored my task ordering. (But maybe you could do it?)

So this is a pyautogui script that simulates key presses on my 1080p display.
It theoretically should work on other machines in the same workspace, but
I worry about things like aspect-ratio etc.

I will make it obvious what you need to change on your set-up to get it working.
Forgive me. This script is a sin against the ethics of computer science."""

import pyautogui as gui
from time import sleep

obj_search_box = (190, 812)
gui.displayMousePosition()