'''
Created on 24.05.2011

@author: Sergey Khayrulin
'''
from NeuroMlEntity.Segment import Segment
from NeuroMlEntity.Position import Position

class Cell(object):
    '''
    Definition of NeuroMl Cell
    '''

    def __init__(self,note='',name=''):
        '''
        Constructor
        '''
        self.note = note
        self.name = name
        self.segments = []
        self.numOfNeurite = 0
        self.numOfDendrite = 0
        
    def add_segment(self,segment):
        '''
        Add segment 'segment' 
        to segments collection
        '''
        self.segments.append(segment)
        
    def add_segment(self,name,id,cable,distal_point,parent,proximal_point=None):
        '''
        Create Segment from input parameter 
        and add it to segments collection 
        '''
        segment_id = id
        parent_id = parent
        segment = Segment(segment_id, name, parent_id, cable)
        position = Position(proximal_point,distal_point)
        segment.SetPosition(position)
        self.segments.append(segment)