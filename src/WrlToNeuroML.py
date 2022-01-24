'''
Created on 03.06.2011

@author: Sergey Khayrulin
'''

import re, sys, os

import numpy
import neuroml
from NeuroMlEntity.Point import Point
from NeuroMlEntity.Constants import *
from NeuroMlParser.NeuroMlWriter import NeuroMlWriter
from NeuroMlEntity.Cell import Cell
from neuroml import Cell as neuroml_Cell
from neuroml import Segment
from neuroml import SegmentParent
from neuroml import Point3DWithDiam
from Entity.Helper import Faces
from Entity.Entity import Entity
from Entity.Vertex import Vertex 
from Entity.Muscle import connect_with_muscles, convert_muscle_name, line_segment_list, segments_from_connections
from neuroml import NeuroMLDocument
from neuroml import Network
from neuroml import Population
from neuroml import Instance
from neuroml import Location
from neuroml import Projection
from neuroml import Connection
from neuroml import Morphology
import neuroml.writers as writers
import neuroml.loaders as loaders

wrlFileName = './Data/Virtual_Worm_March_2011.wrl'
neuronsFileName = './Data/neurons.txt'
morphoMlFileName = 'C.Elegans_%s'
entity = None
muscles = []
neurons = []
neurons_name = []
neurons_info = ''

#
# file used to handle dump of .blend file created via blenderToNeuroMl.py
# I didn't get it to produce global coordinates that look like the ones
# the project has been using.
dump_filename = 'blender.dump'

neuron_dict = {}
muscle_dict = {}

WRL_UPSCALE = 100

#
# A container class to hold several representations of a cell
#
class Cell2:
    def __init__(self, entity, cell):
        self.cell = cell
        self.entity = entity
        seg_list = []
        self.index_of_seg = {}
        if not cell.segments:
            seg_list = line_segment_list(entity, cell)
            for i in range(len(cell.segments)):
                seg = cell.segments[i]
                self.index_of_seg[seg.id] = i
        else:
            for seg in cell.segments:
                self.index_of_seg[seg.id] = len(seg_list)
                pos = seg.position
                pp = pos.proximal_point or cell.segments[seg.parent].position.distal_point
                dp = pos.distal_point
                if abs(dp.x - pp.x) + abs(dp.y - pp.y) + abs(dp.z - pp.z) < 1.e-5:
                    print("add epsilon")
                    dp.z += 1.e-6
                seg_list.append(([pp.x, pp.y, pp.z], [dp.x, dp.y, dp.z]))
                if pos.proximal_point is None:
                    p1str = 'None'
                else:
                    p1str = "[%.3f,%.3f,%.3f]" % (pos.proximal_point.x, pos.proximal_point.y, pos.proximal_point.z)
                p2str = "[%.3f,%.3f,%.3f]" % (pos.distal_point.x, pos.distal_point.y, pos.distal_point.z)
                print("neuron1 %s %s (%s %s) (%s %s)"
                      % (seg.id, seg.name, seg.parent, seg.cable, p1str, p2str))
        self.line_segs = numpy.array(seg_list)


def loadNeuronsName(fileName):
    '''
    Load neurons names from file with name fileName
    '''
    neuronsNameFile = open(fileName,'r')
    for line in neuronsNameFile:
        s = str(line).strip()
        if not neurons_name.__contains__(s):
            neurons_name.append(s)

#
# not used
#    
def get_points_and_faces_v2(fileName, neuronName='', is_muscle = False):
    '''
    read data from wrl 2.0
    '''
    wrlFile =open(fileName,'r')
    startN = False
    startPoint = False
    startIndexes = False
    for line in wrlFile:
        s = str(line)
        if s.startswith('DEF ' + neuronName + ' Shape {\n'):
            startN = True
        if startN:
            if(s.count('point [') == 1):
                startPoint = True
            if s.count('] # point') == 1 and startPoint:
                startPoint = False
            if startPoint:
                if s.count('point [') == 0:
                    temp = s.strip(' ').strip(',\n').split(' ')
                    if len(temp) == 3:
                        entity.add_vertex(temp)
            if(s.count('coordIndex [') == 1):
                startIndexes = True
            if s.count('] # coordIndex') == 1 and startIndexes:
                startIndexes = False
                startN = False
                break
            if startIndexes:
                if not(s.count('coordIndex [')):
                    temp = s.strip(' ').strip('\n').replace(',','').split(' ')
                    if len(temp) == 5:
                        entity.add_face(temp)
    wrlFile.close()
    entity.findCenterOfSoma()
    entity.find_point()

def get_points_and_faces(fileName, neuronName='', is_muscle = False):
    '''
    Function read a wrl file and fill entity.faces and entity.vertices collections
    '''
    print("load data from wrl for neuron %s"%neuronName)
    wrlFile =open(fileName,'r')
    startN = False
    startMatrix = False
    startPoint = False
    startIndexes = False
    for line in wrlFile:
        s = str(line)
        #print("startN %d %s" % (startN, s.strip('\n')))
        if(re.search('\tDEF %s\s*$' % neuronName, s)):
            startN = True
        elif re.search('DEF\s+[A-Z]+_%s\sTransform' % neuronName, s):
            startN = True
        if startN:
            if re.match('\s+point \[', s):
                startPoint = True
            if re.match('\s+]',s) and startPoint:
                startPoint = False
            if startPoint:
                if not(re.match('\s+point \[', s)):
                    temp = s.strip().strip(',').split(' ')
                    if(len(temp) == 3):
                        entity.add_vertex(temp)
            if(s.startswith('\t\tUSE ') and startIndexes == False):
                entity.neuronInfo = s[6:].strip()
            if(re.match('\s+coordIndex \[', s)):
                startIndexes = True
            if re.match('\s+\]', s) and startIndexes:
                startIndexes = False
                startN = False
                #break
            if startIndexes:
                if not(re.match('\s+coordIndex \[', s)):
                    temp = s.strip().replace(',','').split(' ')
                    if len(temp) == 5:
                        entity.add_face(temp)
        if re.match('\s+matrix', s):
            startMatrix = True
            tmp_matrix = []
        if startMatrix:
            mobj = re.match('\s+USE\s+(\S+)', s)
            if mobj:
                startMatrix = False
                if mobj.group(1) == neuronName:
                    transformMatrix = numpy.matrix(tmp_matrix)
            tokens = re.split('\s+', s.strip())
            if len(tokens) == 4:
                num_list = []
                for tok in tokens:
                    num_list.append(float(tok))
                tmp_matrix.append(num_list)
    wrlFile.close()
    if len(entity.vertices) == 0:
        print("did not find %s" % neuronName)
        return False
    # convert to global coordinates:
    for i in range(len(entity.vertices)):
        pt = entity.vertices[i]
        v = numpy.array([pt.x, pt.y, pt.z, 1.0])
        v2 = v*transformMatrix
        entity.vertices[i] = Vertex(v2[0,0]*WRL_UPSCALE, v2[0,1]*WRL_UPSCALE, v2[0,2]*WRL_UPSCALE)
    print("loaded %s" % neuronName)
    if not is_muscle:
        try:
            entity.findCenterOfSoma()
            entity.find_point()
        except IndexError:
            sys.stderr.write("parse failure %s\n" % neuronName)
            print("IndexError %d %d" % (len(entity.vertices), len(entity.faces)))
            #from Entity.plot import plot
            #plot(entity.vertices)
            raise
            return False
    entity.clean_all()          # free up memory used for caches
    return True

def create_cell(cell_name):
    '''
    Create NeuroMlCell
    '''
    b = entity.getAllBrunches()
    cell = Cell(entity.neuronInfo,cell_name)
    if len(b) > 1:
        point = Vertex()
        for k,v in b.items():
            po = entity.resulting_points[v[0]].point
            point.x += po.x/len(b)
            point.y += po.y/len(b)
            point.z += po.z/len(b)
        point.diametr = entity.start_center_point.diametr
        entity.start_center_point = point
    elif(entity.start_center_point == entity.resulting_points[b['axon'][0]].point):
        p1 = entity.resulting_points[b['axon'][0]].point
        p2 = entity.resulting_points[b['axon'][1]].point
        if p1.x - p2.x >= 0:
            entity.start_center_point.x = p1.x - 0.001
        if p1.x - p2.x < 0:
            entity.start_center_point.x = p1.x + 0.001
    soma_proximal_point = Point(entity.start_center_point.x,entity.start_center_point.y,entity.start_center_point.z,entity.start_center_point.diametr)
    soma_distal_point = Point(entity.start_center_point.x,entity.start_center_point.y,entity.start_center_point.z,entity.start_center_point.diametr)
    soma_segment_name = 'Seg%d_%s_%d'%(0,soma_name,0)
    cell.add_segment(soma_segment_name, soma,0,soma_distal_point,-1,soma_proximal_point)
    
    for p in b['axon']:
        if b['axon'].index(p) == 0:
            axon_first_segment_proximal_point = Point(entity.start_center_point.x,entity.start_center_point.y,entity.start_center_point.z,entity.resulting_points[p].point.diametr)
            axon_first_segment_distal_point = Point(entity.resulting_points[p].point.x,entity.resulting_points[p].point.y,entity.resulting_points[p].point.z,entity.resulting_points[p].point.diametr)
            axon_first_segment_name = 'Seg%d_%s_%d'%(0, axon_name, 0)
            cell.add_segment(axon_first_segment_name,p, axon,axon_first_segment_distal_point, 0,axon_first_segment_proximal_point)
        else:
            point = entity.resulting_points[p]
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
                    dendrit_first_segment_proximal_point = Point(entity.start_center_point.x,entity.start_center_point.y,entity.start_center_point.z,entity.resulting_points[p].point.diametr)
                    dendrit_first_segment_distal_point = Point(entity.resulting_points[p].point.x,entity.resulting_points[p].point.y,entity.resulting_points[p].point.z,entity.resulting_points[p].point.diametr)
                    dendrit_first_segment_name = 'Seg%d_%s_%d'%(0, dendrite_name, cell.numOfDendrite)
                    cell.add_segment(dendrit_first_segment_name,p,cell.numOfDendrite, dendrit_first_segment_distal_point, 0,dendrit_first_segment_proximal_point)
                else:
                    point = entity.resulting_points[p]
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
            point = entity.resulting_points[p] 
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
                    dendrite_segment_proximal_point = Point(entity.resulting_points[point.parentPoint].point.x,entity.resulting_points[point.parentPoint].point.y,entity.resulting_points[point.parentPoint].point.z,entity.resulting_points[point.parentPoint].point.diametr)
                dendrite_segment_name = 'Seg%d_%s_%d'%(current_segment, names[point.cable], 0)
                cell.add_segment(dendrite_segment_name,id,cell.numOfNeurite,dendrite_segment_distal_point, parent, proximal_point=dendrite_segment_proximal_point)
                if point.cable == neurite:
                    cell.segments[-1].neurite_id = cell.numOfNeurite
    neurons.append(cell)
    neuron_dict[cell_name] = Cell2(entity, cell)
    return cell

def create_muscle_cell(cell_name):
    print("create_muscle_cell %d checked before start" % len(entity.checked_points))
    cell_name = convert_muscle_name(cell_name)
    cell = Cell(entity.neuronInfo,cell_name)
    muscles.append(cell)
    muscle_dict[cell_name] = Cell2(entity, cell)
    return cell

def writeConnections():
    net_id = "MuscleConnections"
    nml_network_doc = NeuroMLDocument(id=net_id)

    # Create a NeuroML Network data structure to hold on to all the neuron-
    # muscle connection info.
    net = Network(id=net_id)
    nml_network_doc.networks.append(net)

    pop0 = Population(id=muscles[0].name, component=muscles[0].name, size=1)
    inst = Instance(id="0")
    inst.location = Location(x="0.0", y="0.0", z="0.0")
    pop0.instances.append(inst)

    # put that Population into the Network data structure from above
    net.populations.append(pop0)

    for (pre_cell, post_cell, close_pairs) in connect_list:

        # take information about each connection and package it into a 
        # NeuroML Projection data structure
        proj_id = "NCXLS_%s_%s"%(pre_cell, post_cell)
        proj0 = Projection(id=proj_id,
                           presynaptic_population=pre_cell,
                           postsynaptic_population=post_cell) 
                           #synapse=conn.synclass)
        for conn0 in close_pairs:
            proj0.connections.append(conn0)

        net.projections.append(proj0)
    nml_file = 'Output/' + net_id+'.nml'
    writers.NeuroMLWriter.write(nml_network_doc, nml_file)

def createMorphoMlFile(fileName, cell):
    '''
    Convert to new neuroml structures and write
    '''

    if not muscle_dict.has_key(cell.name):
        neuroMlwriter = NeuroMlWriter(fileName, cell.name)
        neuroMlwriter.addCell(cell)
        neuroMlwriter.writeDocumentToFile()
        return

    #
    # Incomplete code to use the neuroml interface to write the file,
    # used for muscles, doesn't produce good enough result on neurons yet.
    #

    seg0 = cell.segments[0].position
    soma = Segment(proximal=cvt_pt(seg0.proximal_point),
                   distal=cvt_pt(seg0.distal_point))
    soma.name = 'Soma'
    soma.id = 0


    axon_segments = []
    for seg1 in cell.segments[1:]:

        parent = SegmentParent(segments=seg1.parent)
        if seg1.position.proximal_point is None:
            p = None
        else:
            p = cvt_pt(seg1.position.proximal_point)

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
    doc.cells.append(nml_cell)
    #addCell(doc, cell)
    doc.id = "TestNeuroMLDocument"
    writers.NeuroMLWriter.write(doc, "Output/%s.nml" % fileName)

def cvt_pt(p):
    return Point3DWithDiam(x=p.x*WRL_UPSCALE, y=p.y*WRL_UPSCALE, z=p.z*WRL_UPSCALE, diameter = p.diameter)



def replace_muscle(muscle_name):
    fd = open(dump_filename, 'r')
    blender_neuron_dict = eval(fd.readline())
    for key in blender_neuron_dict.keys():
        if key == muscle_name:
            [vertex_list, face_list] = blender_neuron_dict[key]
            break
    vertex_p_list = []
    for i in range(len(vertex_list)):
        best_dist = 1.e6
        p_i = Vertex(vertex_list[i][0], vertex_list[i][1], vertex_list[i][2])
        vertex_p_list.append(p_i)
    entity.vertices = vertex_p_list
    entity.faces = Faces()
    for face1 in face_list:
        entity.add_face(face1)

#
# Compare info from .wrl to info from .blend
#
def diff_muscle(muscle1):
    fd = open(dump_filename, 'r')
    blender_neuron_dict = eval(fd.readline())
    for key in blender_neuron_dict.keys():
        if convert_muscle_name(key) == muscle1.name:
            [vertex_list, face_list] = blender_neuron_dict[key]
            break
    muscle_entity = muscle_dict[muscle1.name].entity
    print("diff_muscle %d %d" % (len(vertex_list), len(muscle_entity.vertices)))
    vertex_p_list = []
    for i in range(len(vertex_list)):
        best_dist = 1.e6
        p_i = Vertex(vertex_list[i][0], vertex_list[i][1], vertex_list[i][2])
        vertex_p_list.append(p_i)
        for j in range(len(muscle_entity.vertices)):
            dist = p_i.len_between_point(muscle_entity.vertices[j])
            if dist < best_dist:
                best_dist = dist
                best_idx = j
        print("%3d %3d %7.4f" % (i, best_idx, best_dist))
    from Entity.plot import plot_multi
    plot_multi([muscle_entity.vertices, vertex_p_list, ])

if __name__ == '__main__':
    print('===================== Program Start =====================')
    print('Load information about neurons name from file: %s'%neuronsFileName)
    if 0:                       # used in testing to compare to old version
        old_il1dl_doc = loaders.NeuroMLLoader.load('IL1DL.nml')
        old_il1dl_segs = old_il1dl_doc.cells[0].morphology.segments
        from Entity.plot import plot_segs
        plot_segs(old_il1dl_segs)

    loadNeuronsName(neuronsFileName)
    print('Load is finished')
    print('Create Neurons')
    for neuron_name in neurons_name:
        is_muscle = neuron_name.startswith('mu_')
        print('\tCreate Neuron: %s'%neuron_name)
        entity = Entity()
        try:
            is_good = get_points_and_faces(wrlFileName,neuron_name, is_muscle)
        except (AttributeError, IndexError):
            print(neuron_name)
            from Entity.plot import plot_faces
            plot_faces(entity)
            raise
        if not is_good:
            continue
        #    replace_muscle(neuron_name)
        #from Entity.plot import plot_faces
        #plot_faces(entity)
        if is_muscle:
            neuron_name = convert_muscle_name(neuron_name)
            cell = create_muscle_cell(neuron_name)
        else:
            if len(entity.resulting_points) < 3:
                raise Exception()
            else:
                entity.check_unused_coordinates()
                cell = create_cell(neuron_name)
                createMorphoMlFile(morphoMlFileName % neuron_name, cell)
    if muscles:
        #diff_muscle(muscles[0])
        print("connect muscles")
        connect_list = connect_with_muscles(neuron_dict, muscle_dict)
        segments_from_connections(connect_list, neuron_dict, muscle_dict)
        for cell in muscles:
            createMorphoMlFile(morphoMlFileName % cell.name, cell)
        #from Entity.plot import plot_connect
        #plot_connect(connect_list, neuron_dict, muscle_dict)

        writeConnections()

    print('\tFinish')
    print('===================== Program End =====================')
