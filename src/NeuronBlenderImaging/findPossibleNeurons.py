#To debug, run in your ide of choice as main. 
#Because f-strings are the best string formatting (fight me) you should be running python 3.6 or above
import openpyxl
import os

def read_files(debug=False):
    #should find the file on all OS's
    xlsx_path = os.path.join(os.path.dirname(__file__), "..", "Data", "302.xlsx")
    workbook = openpyxl.load_workbook(xlsx_path)
    sheet = workbook["Sheet1"]
    official_neurons = [] 
    for i, c in enumerate(sheet["B"][1:], start=2):
        official_neurons.append(c.value)

    if debug == True:
        with open("blenderFileObjs.txt") as f:
            all_blender_objs = f.read().splitlines()
        return official_neurons, all_blender_objs
    return official_neurons

def find_closest_unfound(all_blender_objs, debug=False):
    official_neurons = read_files()
    matches = {}
    still_unfound = []
    #we need to search all_blender_objs and remove the ones that we already find.
    for neuron in official_neurons:
        for obj in all_blender_objs:
            if neuron == obj:
                matches[obj] = neuron
                all_blender_objs.remove(obj)
    if debug == True:
        #this will show you what neurons it couldn't find
        print(f"\n{matches = }\n\n{still_unfound = }\n\n{len(still_unfound) = }\n\n{len(matches) = }\n")
        #this is for adjusting the cutoff var
        for match, neuron in matches.items():
            if neuron != match:
                print(f"Is this a correct match? -- {neuron} : {match}")
    return matches

def find(all_blender_objs):
    # official_neurons = read_files()
    matches = find_closest_unfound(all_blender_objs)
    return matches

if __name__ == "__main__":
    official_neurons, all_blender_objs = read_files(debug=True)
    matches = find_closest_unfound(all_blender_objs, debug=True)
    with open("neurons.complete.txt", "w") as w:
        for match in matches:
            w.write(match + "\n")