'''
Created on 03.06.2011

@author: Sergey Khayrulin
'''

import math 

class Vertex(object):
    '''
    Class defines 3D point 
    point has x,y,z coordinates and diameter   
    '''
    def __init__(self,x=0, y=0, z=0,diametr=0):
        '''
        Constructor 
        '''
        self.x = round(x,5)
        self.y = round(y,5)
        self.z = round(z,5)
        self.isSoma = False
        self.diametr = diametr
        
    def __eq__(self,point):
        '''
        Return bool value which 
        means is current point equal to 'point'  
        '''
        if self.x == point.x and self.y == point.y and self.z == point.z:
            return True
        else:
            return False
            
    def __add__(self, point):
        '''
        Return new point which has coordinates 
        equal a sum of coordinates 
        of current point and 'point'  
        '''
        return Vertex(self.x + point.x,self.y+point.y,self.z + point.z)
    
    def __sub__(self,point):
        return Vertex(self.x - point.x,self.y - point.y,self.z - point.z)
    
    def len_between_point(self,point):
        '''
        count length between current point and 'point'
        '''
        p = self - point
        return math.sqrt(p.x*p.x + p.y*p.y + p.z*p.z)
