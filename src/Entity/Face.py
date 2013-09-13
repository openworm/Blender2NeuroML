'''
Created on 03.06.2011

@author: Sergey Khayrulin
'''
class Face(object):
    '''
    Class Face for definition WRL-blender Face
    Face consists 4 vertex (in this case 4 
    vertex but it can be more or less)
    '''


    def __init__(self, a=None, b=None, c=None, d=None):
        '''
        Constructor
        '''
        self.a = a
        self.b = b
        self.c = c
        self.d = d
        self.lenghts = {}
    def printSlice(self):
        str_t ='\t\t\t '
        for p in slice:
            str_t += str(p.point) + ', '
        str_t += ' -1,'
        print str_t