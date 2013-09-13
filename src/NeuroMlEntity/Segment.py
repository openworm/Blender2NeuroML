'''
Created on 24.05.2011

@author: Sergey Khayrulin
'''

class Segment(object):
    '''
    Definition for NeuroML segment
    '''
    def SetPosition(self,position):
        '''
        Establishes position of segment 
        '''
        self.position = position
        
    def __init__(self,id=0,name='',parent=0,cable=0):
        '''
        Constructor
        '''
        self.id = id
        self.name = name
        self.parent = parent
        self.cable = cable
        