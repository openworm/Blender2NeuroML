'''
Created on 05.06.2011

@author: Sergey Khayrulin
'''

import math

eps = 0.0001

class WRLVector(object):
    '''
    Definition for 3D vector
    '''


    def __init__(self, p1, p2):
        '''
        Constructor
        '''
        self.x = p2.x - p1.x 
        self.y = p2.y - p1.y
        self.z = p2.z - p1.z
        self.lenght = round(math.sqrt(self.x * self.x + self.y * self.y + self.z * self.z),4)
        self.lenght_real = round(math.sqrt(self.x * self.x + self.y * self.y + self.z * self.z),4)
        self.norm_vector()
    
    def norm_vector(self):
        '''
        Norm of vector  
        '''
        self.x = self.x / self.lenght 
        self.y = self.y / self.lenght 
        self.z = self.z / self.lenght
        self.lenght = 1.0
    
    def __mul__(self, vector):
        '''
        Scalar multiplication
        '''
        return round( (self.x * vector.x + self.y * vector.y  + self.z * vector.z)/(self.lenght*vector.lenght), 3 )