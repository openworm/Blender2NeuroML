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
load_from_dump = False
if 1:
    load_from_dump = True
else:
    import bpy
import sys, os, pprint

# Load modules in the script's directory
scriptPath = os.path.dirname(os.path.realpath(__file__))
print("scriptPath %s" % scriptPath)

#import Blender
#from Blender import Object, Mesh, NMesh, Lamp, Draw, BGL, Image, Text, sys, Mathutils

try:
    from neuroml import Cell as neuroml_Cell
    from neuroml import Segment
    from neuroml import SegmentParent
    from neuroml import Point3DWithDiam
    from neuroml import Morphology
    from neuroml import NeuroMLDocument
    import neuroml.writers as writers
except ImportError:
    pass

from NeuroMlEntity.Cell import Cell
from Entity.Entity import Entity
from Entity.Vertex import Vertex 
from NeuroMlEntity.Point import Point
from NeuroMlEntity.Constants import *
from NeuroMlParser.NeuroMlWriter import NeuroMlWriter
import zipfile
import xml.parsers.expat
import xml.dom.minidom


"""
this is optional if you wanna debug you should add path with pydev debuger to python path
"""
#pathTopyDevDebuger = r"C:\eclips\eclipse\plugins\org.python.pydev.debug_1.5.4.2010011921\pysrc"
#sys.path.append(pathTopyDevDebuger)
# 
#import pydevd

fileWithNeuron = scriptPath + '/Data/neurons.txt'
odsFileWithNeurons = scriptPath + '/Data/302.ods'

neuron = 'ADAL'
outFileName = 'C.elegans_%s'
neurons = []
neurons_name = []
badNeurons = []
neuroNameFromOds = []

dump_only = not load_from_dump
dump_filename = 'blender.dump'
neuron_dict = {}
muscle_dict = {}

log_fd = None
def write_log(*args):
    global log_fd
    if log_fd is None:
        log_fd = open('blender.log', 'w')
    for (count, s) in enumerate(args):
        log_fd.write(str(s) + ' ')
    log_fd.write('\n')
    log_fd.flush()

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
        write_log(ex)
    except Exception as ex:
        write_log(ex)

def loadNeuronsName(fileName):
    '''
    Load name of neuron from file - fileName
    '''
    neuronsNameFile = open(fileName,'r')
    for line in neuronsNameFile:
        s = str(line).strip('\n')
        if not neurons_name.__contains__(s):
            neurons_name.append(s)
            #neuron_dict[s] = None

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

        #try:
        if 1:
            if object.type == "MESH":
                mesh = object.data
                # Create tesselation faces
                mesh.calc_tessface()
                if len(mesh.materials) > 1:
                    if ( neuroNameFromOds.__contains__(object.name)
                        or object.name[:7] == 'mu_bod_'):
                        #and object.name == "PVDR"):# or object.name == "URBL"):#object.getData().materials[0].name != "Motor Neuron"
                        import mathutils
                        write_log(object.name)
                        write_log("%d vertices, %d faces" % (len(mesh.vertices),
                                                             len(mesh.tessfaces)))
                        write_log("matrix %s" % object.matrix_world)
                        neuronName = object.name
                        if dump_only:
                            v_list = []
                            f_list = []
                            for vertex in mesh.vertices:
                                v = vertex.co
                                v_list.append([v[0], v[1], v[2]])
                            for face in mesh.tessfaces:
                                cordArr = []
                                for v in face.vertices:
                                    cordArr.append(v)
                                if len(cordArr) == 3:
                                    cordArr.append(cordArr[0])
                                f_list.append(cordArr)
                            neuron_dict[str(neuronName)] = [v_list, f_list]
                            write_log(neuronName, '=')
                            write_log(pprint.PrettyPrinter().pformat(mesh))
                            continue
                        entity = mesh_to_entity(mesh)
                        entity_to_cell(entity, neuronName)
        #except Exception:
        #    write_log "Error: object named %s has problem with accessing an attribute" % object.name
        #    badNeurons.append(object.name)
        #    continue
    write_log(list(badNeurons))

def mesh_to_entity(mesh):
    entity = Entity()
    for vertex in mesh.vertices:
        v = vertex.co
        entity.add_vertex([round(v[0],3),round(v[1],3),round(v[2],3)])
    for face in mesh.tessfaces:
        cordArr = []
        for v in face.vertices:
            write_log('+', v)
            cordArr.append(v)
        if len(cordArr) == 3:
            cordArr.append(cordArr[0])
        write_log('=', cordArr)
        entity.add_face(cordArr)
    entity.neuronInfo = mesh.materials[0].name
    return entity

def entity_to_cell(entity, neuronName):
    entity.findCenterOfSoma()
    write_log('found center of soma')
    entity.find_point()
    create_cell(neuronName,entity)

def export2():
    for (neuronName, v) in neuron_dict.items():
        print('start %s' % neuronName)
        if neuronName[:7] == 'mu_bod_' or neuronName != 'VA10': # or neuronName in ('M1', 'RMED', 'PVDR', 'PVDL', 'IL1DL', 'IL1DR', 'I5', ):
            continue
        (v_list, f_list) = v
        entity = Entity()
        for vertex in v_list:
            v = vertex
            entity.add_vertex([round(v[0],3),round(v[1],3),round(v[2],3)])
        for face in f_list:
            entity.add_face(face)
        entity.neuronInfo = neuronName
        entity_to_cell(entity, neuronName)


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

def cvt_pt(p):
    return Point3DWithDiam(x=p.x, y=p.y, z=p.z, diameter = p.diameter)

def createMorphoMlFile(fileName, cell):
    '''
    Convert to new neuroml structures and write
    '''

    seg0 = cell.segments[0].position
    soma = Segment(proximal=cvt_pt(seg0.proximal_point),
                   distal=cvt_pt(seg0.distal_point))
    soma.name = 'Soma'
    soma.id = 0

    axon_segments = []
    for seg1 in cell.segments[1:]:

        parent = SegmentParent(segments=seg1.parent)
        if seg1.position.distal_point is None:
            p = None
        else:
            p = cvt_pt(seg1.position.distal_point)
        axon_segment = Segment(proximal = p,
                               distal = cvt_pt(seg1.position.distal_point),
                               parent = parent)
        axon_segment.id = seg1.id
        axon_segment.name = seg1.name
        axon_segments.append(axon_segment)

    morphology = Morphology()
    morphology.segments.append(soma)
    morphology.segments += axon_segments
    morphology.id = 'morphology_' + cell.name

    nml_cell = neuroml_Cell()
    nml_cell.id = cell.name
    nml_cell.morphology = morphology

    doc = NeuroMLDocument()
    #doc.name = "Test neuroML document"
    doc.cells.append(nml_cell)
    doc.id = fileName
    writers.NeuroMLWriter.write(doc, "Output/%s.nml" % fileName)
    
if __name__ == '__main__':
    if not load_from_dump:
        bpy.ops.object.mode_set(mode='OBJECT')
    #loadNeuronsName(fileWithNeuron)
    getNeuronsNameFromOdsFile(odsFileWithNeurons)
    write_log('Create Neurons')
    if load_from_dump:
        fd = open(dump_filename, 'r')
        neuron_dict = eval(fd.readline())
        #write_log(pprint.PrettyPrinter().pformat(neuron_dict))
        export2()
        for cell in neurons:
            neuron_dict[cell.name] = cell
    else:
        export(bpy.data.objects, '')
    if dump_only:
        try:
            fd = open(dump_filename, 'w')
            fd.write(str(neuron_dict))
            fd.close()
        except (IOError, OSError, TypeError) as msg:
            raise
    write_log('WriteResult To File')
    for neuronName in sorted(neuron_dict.keys()):
        if type(neuron_dict[neuronName]) != type([]):
            createMorphoMlFile(outFileName % neuronName, neuron_dict[neuronName])

    #createMorphoMlFile(outFileName%'I6')
    write_log('\tFinish')
