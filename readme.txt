In root folder two files are which you can run in console independent and blenderToNeuroMl you can run in eclipse
  1. CheckWrlFile.py - compare wrl file Virtual_Worm_March_2011.wrl (located in folder Data) with  302.ods and NeuronConnect.xls.
     It find neurons which is in 302.ods and NeuronConnect.xls but isn't in Virtual_Worm_March_2011.wrl. Output of scripts infers 
     to console. Before you run you'll need to install some plugins for your Eclipse to work with python (http://pydev.org/). 
     Also you need to install a plugin for your python to get it to work with an MS Excel file:
        * (xlrd-0.6.1.win32) for windows 
        * (http://pypi.python.org/pypi/xlrd - you can download it for other platforms) 
  2. WrlToNeuroML.py - create morphoMl form wrl file Virtual_Worm_March_2011.wrl for neurons listed in neurons.txt file.
     This script takes data form Data folder and create one morphoMl file in folder Output.
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
     
If you have any problem will be glad to help
write s.khayrulin@gmail.com
or openworm@googlegroups.com