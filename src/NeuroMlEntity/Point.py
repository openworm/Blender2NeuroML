'''
Created on 25.05.2011

@author: Sergey
'''
import math

class Point(object):
    '''
    Definition for NeuroMlPoint 
    '''

    def __init__(self,x=0, y=0,z=0,diameter=1):
        '''
        Constructor
        '''
        self.x = round(x,5)
        self.y = round(y,5)
        self.z = round(z,5)
        if abs(self.x) == 0.0:
            self.x = 0.0
        if abs(self.y) == 0.0:
            self.y = 0.0
        if abs(self.z) == 0.0:
            self.z = 0.0
        self.diameter = diameter
        
    def lenBetweenTwoPoint(self,point):
        '''
        Count length between 
        current point and 'point'
        '''
        return math.sqrt((self.x - point.x) * (self.x - point.x) + 
                         (self.y - point.y) * (self.y - point.y) + 
                         (self.z - point.z) * (self.z - point.z))
        