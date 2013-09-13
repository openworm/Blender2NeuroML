'''
Created on 24.05.2011

@author: Sergey Khayrulin
'''

class Position(object):
    '''
    Definition for position of point 
    '''
    
    def __init__(self,proximal_point=None,distal_point=None):
        '''
        Constructor
        '''
        self.distal_point = distal_point 
        self.proximal_point = proximal_point #if null than = distal point of parent