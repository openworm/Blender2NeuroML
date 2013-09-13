'''
Created on 03.06.2011

@author: Sergey Khayrulin
'''


from NeuroMlEntity.Point import Point
from NeuroMlEntity.Constants import *
from NeuroMlParser.NeuroMlWriter import NeuroMlWriter
from NeuroMlEntity.Cell import Cell
from Entity.Entity import Entity
from Entity.Vertex import Vertex 

wrlFileName = './Data/Virtual_Worm_March_2011.wrl'
neuronsFileName = './Data/neurons.txt'
morphoMlFileName = 'C.Elegans_%s'
entity = None
neurons = []
neurons_name = []
neurons_info = ''
troubleNeurons = []

def loadNeuronsName(fileName):
    '''
    Load neurons names from file with name fileName
    '''
    neuronsNameFile = open(fileName,'r')
    for line in neuronsNameFile:
        s = str(line).strip('\n')
        if not neurons_name.__contains__(s):
            neurons_name.append(s)
    
def get_points_and_faces_v2(fileName, neuronName=''):
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
def get_points_and_faces(fileName, neuronName=''):
    '''
    Function read a wrl file and fill entity.faces and entity.vertices collections
    '''
    print "load data from wrl for neuron %s"%neuronName
    wrlFile =open(fileName,'r')
    startN = False
    startPoint = False
    startIndexes = False
    for line in wrlFile:
        s = str(line)
        if(s.startswith('\tDEF '+ neuronName + '\n')):
            startN = True
        if startN:
            if(s.startswith('\t\t\tpoint [')):
                startPoint = True
            if s.startswith('\t\t\t]') and startPoint:
                startPoint = False
            if startPoint:
                if not(s.startswith('\t\t\tpoint [')):
                    temp = s.strip('\t').strip(' ').strip(',\n').split(' ')
                    if(len(temp) == 3):
                        entity.add_vertex(temp)
            if(s.startswith('\t\tUSE ') and startIndexes == False):
                entity.neuronInfo = s[6:].strip('\n')
            if(s.startswith('\t\t\tcoordIndex [')):
                startIndexes = True
            if s.startswith('\t\t\t]') and startIndexes:
                startIndexes = False
                startN = False
                break
            if startIndexes:
                if not(s.startswith('\t\t\tcoordIndex [')):
                    temp = s.strip('\t').strip(' ').strip('\n').replace(',','').split(' ')
                    if len(temp) == 5:
                        entity.add_face(temp)
    wrlFile.close()
    print "loaded"
    entity.findCenterOfSoma()
    entity.find_point()

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
    neurons.append(cell)
    return
def createMorphoMlFile(fileName):
    '''
    Create MorphoMl for every cell from cells collection
    '''
    neuroMlwriter = NeuroMlWriter(fileName)
    for cell in neurons:
        neuroMlwriter.addCell(cell)
    neuroMlwriter.writeDocumentToFile()
if __name__ == '__main__':
    print '===================== Program Start ====================='
    print 'Load information about neurons name from file: %s'%neuronsFileName
    print 'Load is finished'
    loadNeuronsName(neuronsFileName)
    print 'Create Neurons'
    for neuron_name in neurons_name:
        print '\tCreate Neuron: %s'%neuron_name
        entity = Entity()
        get_points_and_faces(wrlFileName,neuron_name)
        if len(entity.resulting_points) < 3:
            raise Exception()
        else:
            create_cell(neuron_name)
            createMorphoMlFile(morphoMlFileName%neuron_name)
        print '\tFinish'
    print '\tFinish'
    print '\tCreate MorphoMlFile: %s'%neuron_name
    print list(troubleNeurons)
    print '===================== Program End ====================='