Blender2NeuroML
===============

Conversion script to bring neuron models created in Blender into NeuroML format.

In the [src folder](/tree/master/src) there are two Python files which can be run in the console and blenderToNeuroMl.py which can be run in Eclipse.


**Update 2022: the scripts below have been rechecked and tested in Python 3**

  1. [CheckWrlFile.py](src/CheckWrlFile.py) - compare WRL file [Virtual_Worm_March_2011.wrl](src/Data/Virtual_Worm_March_2011.wrl) with [302.ods](src/Data/302.ods) and [NeuronConnect.xls](src/Data/NeuronConnect.xls).
     It finds neurons which are in 302.ods and NeuronConnect.xls but aren't in [Virtual_Worm_March_2011.wrl](src/Data/Virtual_Worm_March_2011.wrl). Output of scripts prints
     to console. Before you run it you'll need to install xlrd. Type: `pip install xlrd`
  2. [WrlToNeuroML.py](src/WrlToNeuroML.py) - create NeuroML files from WRL file [Virtual_Worm_March_2011.wrl](src/Data/Virtual_Worm_March_2011.wrl) for neurons listed in the [neurons.txt](/src/Data/neurons.txt) file. This script takes data from the [Data folder](/tree/master/src/Data) and creates one NeuroML file in folder [Output](/tree/master/src/Output).

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
