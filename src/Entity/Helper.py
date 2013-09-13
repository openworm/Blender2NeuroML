'''
Created on 03.06.2011

@author: Sergey Khayrulin
'''
class ParserException(Exception):
    '''
    User Exception
    '''
    def __init__(self,value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class HelpPoint:
    '''
    Helper Class
    '''
    def __init__(self,point, lenght):
        self.point = point
        self.lenght = lenght
    def __eq__(self,p):
        if self.point == p.point:
            return True
        else:
            return False
 
class Result_Point:
    '''
    Definition for resulting point:
    point - WrlPoint3D
    parentPoint - is index of parent point index from resultin_points collection
    cable - int number which indicate to what cableGroup 
    isBrunchStart - indicate when the point is a start of branching
    '''
    def __init__(self,point,parentPoint,cable=0,isBrunchStart=False):
        self.point = point
        self.cable = cable
        self.isAxon = False 
        self.isDendrite = False
        self.isNeurite = False
        self.parentPoint = parentPoint
        self.isBrunchStart = isBrunchStart
        
    def getRoot(self, resulting_points):
        '''
        Get root point 
        '''
        if self.parentPoint != 0:
            return resulting_points[self.parentPoint].getRoot(resulting_points)
        else:
            if self.parentPoint == 0:
                return resulting_points.index(self)

class Faces(dict):
    '''
    definition for collection of face
    inherit from dictionary
    Faces - contains pair (key=>value) where key is sorted order of face.
    '''
    
    def __init__(self):
        dict.__init__({})
    def __setitem__(self,key,value):
        '''
        Set item with key to Faces
        '''
        if key.__class__ == list:
            keystr = self.__transformkey(key) 
            super(Faces, self).__setitem__(keystr, value)
        elif key.__class__ == str:
            super(Faces, self).__setitem__(key, value)
    def __getitem__(self,key):
        '''
        Get item with key from Faces
        '''
        if key.__class__ == list:
            keystr = self.__transformkey(key) 
            return super(Faces, self).__getitem__(keystr)
        elif key.__class__ == str:
            return super(Faces, self).__getitem__(key)
    def __missing__(self,key):
        '''
        This method run if __getitem__ didn't find any item with key
        '''
        return None
    def __transformkey(self, keyArray):
        '''
        Transform key from list to string 
        '''
        keyArray = sorted(keyArray)
        return " %s, %s, %s, %s,"%(keyArray[0],keyArray[1],keyArray[2],keyArray[3])
    def hasFaceWithSide(self, num_p1, num_p2):
        '''
        Check for two vertices num_1, num_2
        Is collection of faces contain face with such side.
        '''
        faceWithpoints = [self[key] for key in filter(lambda k:" %s,"%num_p1 in k and " %s,"%num_p2 in k,self.keys())]
        for face in faceWithpoints:
            if abs(face.order.index(num_p1) - face.order.index(num_p2)) == 1 or abs(face.order.index(num_p1) - face.order.index(num_p2)) == 3:
                    return True
        return False
