Blender2NeuroML
===============

Conversion scripts to convert <i>C. elegans</i> 3D neural models created in Blender into NeuroML format.

<p align="center"><img src="https://github.com/openworm/Blender2NeuroML/raw/master/images/Blender_ADAL.png" height="230"/>&nbsp;&nbsp;
<img src="https://github.com/openworm/Blender2NeuroML/raw/master/images/ADAL.png" height="230"/></p>
<p align="center"><sup><i>Figure showing a single cell (<a href="https://www.wormatlas.org/neurons/Individual%20Neurons/ADAframeset.html">ADAL</a>) highlighted in orange in the original
<a href="https://github.com/openworm/Blender2NeuroML/blob/master/src/Data/Virtual_Worm_March_2011.blend">3D Blender file</a> (from the
<a href="http://caltech.wormbase.org/virtualworm">Virtual Worm Project</a>) on the left, and corresponding images of the cell on its own in Blender (middle 2 panels) and in
<a href="https://docs.neuroml.org/Userdocs/NeuroMLv2.html">NeuroML 2</a> format (right 2 panels). The NeuroML version is being used in our
<a href="https://github.com/openworm/c302">biophysical model of the worm nervous system</a>. See
<a href="https://github.com/openworm/Blender2NeuroML/blob/master/src/NeuroMLImages/README.md">here</a> for more examples.</i></sup></p>


**Update 2022: the scripts below have been rechecked and tested in Python 3**

  1. [CheckWrlFile.py](src/CheckWrlFile.py) - compare WRL file [Virtual_Worm_March_2011.wrl](src/Data/Virtual_Worm_March_2011.wrl) with [302.ods](src/Data/302.ods) and [NeuronConnect.xls](src/Data/NeuronConnect.xls).
     It finds neurons which are in 302.ods and NeuronConnect.xls but aren't in [Virtual_Worm_March_2011.wrl](src/Data/Virtual_Worm_March_2011.wrl). Output of scripts prints
     to console. Before you run it you'll need to install xlrd. Type: `pip install xlrd`
  2. [WrlToNeuroML.py](src/WrlToNeuroML.py) - create NeuroML files from WRL file [Virtual_Worm_March_2011.wrl](src/Data/Virtual_Worm_March_2011.wrl) for neurons listed in the [neurons.txt](/src/Data/neurons.txt) file. This script takes data from the [Data folder](src/Data) and creates one NeuroML file in folder [Output](src/Output).

**Update 2022: the following is still being updated/tested**

  3. blenderToNeuroMl.py - create morphoMl form blender file for all mottor neurons from Virtual_Worm_March_2011.blend
     (should located in folder 'path to your blender\.blender\').
     For run you should do in eclipse this:
       "Run->External Tools->External Tools..." with the following settings:
        Main-Tab:
        Location: blender executable
        Working directory: blender executable directory
        Arguments:-b "path to file Virtual_Worm_March_2011.blend" -w -P ${resource_loc}
        Environment-Tab:
        Variable: PYTHONPATH
        Value: ${container_loc}
        and choose "Append environment to native environment"
     Also you need in your blender folder create folder with name Output there are will be save output file.
  4. blenderStraighten.py - edit blender file, straightening the worm body; see the file header for details.
  5. blenderExportSpine.py - export spine information from the Blender model (e.g. for NeuroML transformation); see the file header for details.

If you have any problem will be glad to help
write s.khayrulin@gmail.com or openworm-discuss@googlegroups.com


For some scripts (like blenderToNeuroMl.py) you need to run them in the Blender Scripting console.

To Run Python Scripts in the Blender Console:
1. Install Blender
2. Click on the Scripting Workspace Tab near the top right/middle
3. Under the text editor, click the folder icon that says "Open"
4. Navigate to your Python Script
5. Push the play button to run the script
There likely will be errors.
To view the Blender console click on "Window" near the top left and click "Toggle System Console"
For 3rd party module import errors, remember that Blender uses its own install of Python-
You will need to get Blender to install those modules to its own internal Python.

To Install 3rd Party Modules to Blender's Internal Python:
1. Follow the above instructions and open the installDependencies.py in Blender
2. Run the script. (Blender needs to be open as admin (at least on Windows))
3. Go for a walk. It might take a bit.

TIPS ABOUT RUNNING SCRIPTS IN BLENDER(3.0.1):
Editing a script:
It can be kind of annoying. If you edit a script, in your IDE and save, Blender will not autoupdate the script.
Reload the script by clicking the "Text" tab (on the "Text Editor" workspace) and then click reload. (Hotkey: ALT+R)
If you edit a dependency/module of the main script you're loading, then even reopening the script won't work.
You need to completely close and reopen Blender for it to update. (If you find a workaround, delete this and write it.)

Making scripting less annoying:
You can install a fake bpy module to make it so your linter (I use VScode) recognizes your bpy module.
To install this module just call "pip install fake-bpy-module-2.82"

Crashing:
Sometimes it will just crash.
My most frequent cause of crashing is Blender's internal version of Python reaching for things on the OS (Windows)
that it doesn't have permission to.
That is why I reccomend opening Blender as admin ('shift + rightclick' the program).
I know it's not the best practice, but it's either that or you have to copy
all of your scripts into the correct folder of the Blender install.
(Even if you did do that, the default install location for Blender on Windows is not on the User's folder.
So you need admin permissions to use the OS or SYS modules or edit files there anyways.
[The whole point of the conversion scripts is to edit files.]
It's a mess. So, if you really care about security on Windows, just run Blender portably or
reinstall Blender in the User's folder...
It's almost like Blender wasn't designed for our use case...
But then again, if you find a better way to do this, delete my bad advice please.)
