'''
Created on 20.07.2011
@author: Sergey Khayrulin

This doesn't run as a standalone script; run it in blender after loading
the appropriate .blend file

For Run you need do next:
"Run->External Tools->External Tools..." with the following settings: 
Main-Tab: 
Location: blender executable 
Working directory: blender executable directory 
Arguments:-b "path to file Virtual_Worm_March_2011.blend" -w -P ${resource_loc} 
Environment-Tab: 
Variable: PYTHONPATH 
Value: ${container_loc} 
and choose "Append environment to native environment"
'''
import bpy
from bpy import Object, Mesh, NMesh, Lamp, Draw, BGL, Image, Text
import sys, os, mathutils
# Load modules in the script's directory
scriptPath = os.path.dirname(os.path.realpath(__file__))
print("scriptPath %s" % scriptPath)

from NeuroMlEntity.Cell import Cell
from Entity.Entity import Entity
from Entity.Vertex import Vertex 
from NeuroMlEntity.Point import Point
from NeuroMlEntity.Constants import *
from NeuroMlParser.NeuroMlWriter import NeuroMlWriter
import zipfile
import xml.parsers.expat
import xml.dom.minidom


fileWithNeuron = '/Data/neurons.txt'
odsFileWithNeurons = '/Data/302.ods'

neuron = 'ADAL'
outFileName = 'C.elegans_%s'
neurons = []
neurons_name = []
badNeurons = []
neuroNameFromOds = []

def getNeuronsNameFromOdsFile(fileName):
    '''
    Read data from Ods file 
    '''
    try:
        ziparchive = zipfile.ZipFile(fileName, "r")
        xmldata = ziparchive.read("content.xml")
        ziparchive.close()
        xmldoc = xml.dom.minidom.parseString(xmldata)
        for node in xmldoc.getElementsByTagName('table:table-row')[1:]:
            if len(node.childNodes) > 2 :
                neuroName = node.childNodes[1].getElementsByTagName("text:p")[0].childNodes[0].toxml()
                if not neuroNameFromOds.__contains__(neuroName):
                    neuroNameFromOds.append(neuroName.strip('*'))
        if len(neuroNameFromOds) != 302:
            raise Exception("file %s doesn't contains all neurons name"%fileName)
    except IOError as ex:
        print(ex)
    except Exception as ex:
        print(ex)

def loadNeuronsName(fileName):
    '''
    Load name of neuron from file - fileName
    '''
    neuronsNameFile = open(fileName,'r')
    for line in neuronsNameFile:
        s = str(line).strip('\n')
        if not neurons_name.__contains__(s):
            neurons_name.append(s)

def export(theObjects, neuronName):
    '''
    Run export motto neurons from blender file 
    '''
    for object in theObjects:
        # Make sure the object vertices correspond to true location
        bpy.context.scene.objects.active = object
        object.select = True
        bpy.ops.object.transform_apply(scale=True, rotation=True)
        object.select = False
        try:
            objType=object.getType()
            if objType == "Mesh":
                mesh.calc_tessface()
                if len(mesh.materials) > 1:
                    if (neuroNameFromOds.__contains__(object.name) and 
                        object.name == "PVDR"):# or object.name == "URBL"):#object.getData().materials[0].name != "Motor Neuron"

                        print(object.name)
                        entity = Entity()
                        neuronName = object.name
                        mesh = object.getData()
                        for vertex in mesh.verts:
                            ob_matrix = mathutils.Matrix(object.getMatrix('worldspace'))
                            mm = ob_matrix
                            blenvert = mathutils.Vector(vertex.co)
                            v = blenvert * mm
                            entity.add_vertex([round(v[0],3),round(v[1],3),round(v[2],3)])
                        for face in mesh.tessfaces:
                            cordArr = []
                            for i in range(len(face)):
                                indx = mesh.verts.index(face[i])
                                cordArr.append(indx)                            
                            entity.add_face(cordArr)
                        entity.neuronInfo = object.getData().materials[0].name
                        entity.findCenterOfSoma()
                        entity.find_point()
                        create_cell(neuronName,entity)
        except Exception:
            print("Error: object named %s has problem with accessing an attribute" % object.name)
            badNeurons.append(object.name)
            continue
    print(list(badNeurons))
def create_cell(cell_name, wrlEntity):
    '''
    Create Cell from received data in wrlEntity 
    '''
    b = wrlEntity.getAllBrunches()
    cell = Cell(wrlEntity.neuronInfo,cell_name)
    if len(b) > 1:
        point = Vertex()
        for k,v in b.items():
            po = wrlEntity.resulting_points[v[0]].point
            point.x += po.x/len(b)
            point.y += po.y/len(b)
            point.z += po.z/len(b)
        point.diametr = wrlEntity.start_center_point.diametr
        wrlEntity.start_center_point = point
    elif(wrlEntity.start_center_point == wrlEntity.resulting_points[b['axon'][0]].point):
        p1 = wrlEntity.resulting_points[b['axon'][0]].point
        p2 = wrlEntity.resulting_points[b['axon'][1]].point
        if p1.x - p2.x >= 0:
            wrlEntity.start_center_point.x = p1.x - 0.001
        if p1.x - p2.x < 0:
            wrlEntity.start_center_point.x = p1.x + 0.001
    soma_proximal_point = Point(wrlEntity.start_center_point.x,\
                                wrlEntity.start_center_point.y,\
                                wrlEntity.start_center_point.z,\
                                wrlEntity.start_center_point.diametr)
    soma_distal_point = Point(wrlEntity.start_center_point.x,\
                              wrlEntity.start_center_point.y,\
                              wrlEntity.start_center_point.z,\
                              wrlEntity.start_center_point.diametr)
    soma_segment_name = 'Seg%d_%s_%d'%(0,soma_name,0)
    cell.add_segment(soma_segment_name, soma,0,soma_distal_point,-1,soma_proximal_point)
    
    for p in b['axon']:
        if b['axon'].index(p) == 0:
            axon_first_segment_proximal_point = Point(wrlEntity.start_center_point.x,\
                                                      wrlEntity.start_center_point.y,\
                                                      wrlEntity.start_center_point.z,\
                                                      wrlEntity.resulting_points[p].point.diametr)
            
            axon_first_segment_distal_point = Point(wrlEntity.resulting_points[p].point.x,\
                                                    wrlEntity.resulting_points[p].point.y,\
                                                    wrlEntity.resulting_points[p].point.z,\
                                                    wrlEntity.resulting_points[p].point.diametr)
            
            axon_first_segment_name = 'Seg%d_%s_%d'%(0, axon_name, 0)
            cell.add_segment(axon_first_segment_name,p, axon,axon_first_segment_distal_point, 0,axon_first_segment_proximal_point)
        else:
            point = wrlEntity.resulting_points[p]
            if not point.isNeurite:
                id = p
                current_segment = id
                parent = point.parentPoint
                axon_segment_distal_point = Point(point.point.x,point.point.y,point.point.z,point.point.diametr)
                axon_segment_proximal_point = None
                axon_segment_name = 'Seg%d_%s_%d'%(current_segment, names[point.cable], 0)
                cell.add_segment(axon_segment_name,id,axon,axon_segment_distal_point, parent, proximal_point=axon_segment_proximal_point)
    if len(b) > 1:
        cell.numOfDendrite = 1
    for k,v in b.items():
        if k != 'axon':
            cell.numOfDendrite += 1
            for p in v:
                if v.index(p) == 0:
                    dendrit_first_segment_proximal_point = Point(wrlEntity.start_center_point.x,\
                                                                 wrlEntity.start_center_point.y,\
                                                                 wrlEntity.start_center_point.z,\
                                                                 wrlEntity.resulting_points[p].point.diametr)
                    dendrit_first_segment_distal_point = Point(wrlEntity.resulting_points[p].point.x,\
                                                               wrlEntity.resulting_points[p].point.y,\
                                                               wrlEntity.resulting_points[p].point.z,\
                                                               wrlEntity.resulting_points[p].point.diametr)
                    dendrit_first_segment_name = 'Seg%d_%s_%d'%(0, dendrite_name, cell.numOfDendrite)
                    cell.add_segment(dendrit_first_segment_name,p,cell.numOfDendrite, dendrit_first_segment_distal_point, 0,dendrit_first_segment_proximal_point)
                else:
                    point = wrlEntity.resulting_points[p]
                    if not point.isNeurite:
                        id = p
                        current_segment = id
                        parent = point.parentPoint
                        dendrite_segment_distal_point = Point(point.point.x,point.point.y,point.point.z,point.point.diametr)
                        dendrite_segment_proximal_point = None
                        dendrite_segment_name = 'Seg%d_%s_%d'%(current_segment, names[point.cable], 0)
                        cell.add_segment(dendrite_segment_name,id,cell.numOfDendrite,dendrite_segment_distal_point, parent, proximal_point=dendrite_segment_proximal_point)
    for k,v in b.items():
        for p in v:
            point = wrlEntity.resulting_points[p] 
            if point.isNeurite:
                id = p
                current_segment = id
                parent = point.parentPoint
                dendrite_segment_distal_point = Point(point.point.x,point.point.y,point.point.z,point.point.diametr)
                dendrite_segment_proximal_point = None
                if point.isBrunchStart and point.cable == neurite:
                    if cell.numOfNeurite == 0:
                        cell.numOfNeurite =  cell.numOfDendrite == 0 and 2 or cell.numOfDendrite + 1
                    else:
                        cell.numOfNeurite += 1 
                    dendrite_segment_proximal_point = Point(wrlEntity.resulting_points[point.parentPoint].point.x,\
                                                            wrlEntity.resulting_points[point.parentPoint].point.y,\
                                                            wrlEntity.resulting_points[point.parentPoint].point.z,\
                                                            wrlEntity.resulting_points[point.parentPoint].point.diametr)
                dendrite_segment_name = 'Seg%d_%s_%d'%(current_segment, names[point.cable], 0)
                cell.add_segment(dendrite_segment_name,id,cell.numOfNeurite,dendrite_segment_distal_point, parent, proximal_point=dendrite_segment_proximal_point)
    neurons.append(cell)
    return
def createMorphoMlFile(fileName):
    '''
    Create MorphoMl File with all cells from neurons
    '''
    neuroMlwriter = NeuroMlWriter(fileName)
    for cell in neurons:
        neuroMlwriter.addCell(cell)
    neuroMlwriter.writeDocumentToFile()
    print("%s neurons was successful imported"%len(neurons))
    
if __name__ == '__main__':
    #loadNeuronsName(fileWithNeuron)
    getNeuronsNameFromOdsFile(odsFileWithNeurons)
    print('Create Neurons')
    scene = bpy.Scene.GetCurrent()
    export(scene, '')
    print('WriteResult To File')
    createMorphoMlFile(outFileName%'I6')
    print('\tFinish')