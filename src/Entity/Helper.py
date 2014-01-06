'''
Created on 03.06.2011

@author: Sergey Khayrulin
'''
import math, re, pprint


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
        self.faces_with_points = {} # cache by point
    def __setitem__(self,key,value):
        '''
        Set item with key to Faces
        '''
        if key.__class__ == list:
            keystr = self.__transformkey(key) 
            super(Faces, self).__setitem__(keystr, value)
        elif key.__class__ == str:
            super(Faces, self).__setitem__(key, value)
        self.faces_with_points = {}
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

    def __Regen_Dict(self):
        for key in self.keys():
            tokens = re.split('[,\s]+', key)
            for tok in tokens:
                if not tok: continue
                p = int(tok)
                try:
                    self.faces_with_points[p].append(self[key])
                except KeyError:
                    self.faces_with_points[p] = [self[key]]

    def WithPoints(self, p0, p1):
        if not self.faces_with_points:
            self.__Regen_Dict()
        try:
            list0 = self.faces_with_points[p0]
        except KeyError:
            list0 = []
        try:
            list1 = self.faces_with_points[p1]
        except KeyError:
            list1 = []
        return list0 + list1

    def clean_all(self):
        self.faces_with_points = {}

    def hasFaceWithSide(self, num_p1, num_p2):
        face = self.getFaceWithSide(num_p1, num_p2)
        return face is not None

    def getFaceWithSide(self, num_p1, num_p2):
        '''
        Check for two vertices num_1, num_2
        Is collection of faces contain face with such side.
        '''
        if 0:
            faceWithpoints = [self[key] for key in filter(lambda k:" %s,"%num_p1 in k and " %s,"%num_p2 in k,self.keys())]
        else:
            if not self.faces_with_points:
                self.__Regen_Dict()
            faceWithpoints = []
            for p in (num_p1, num_p2):
                if self.faces_with_points.has_key(p):
                    for face in self.faces_with_points[p]:
                        if num_p1 in face.order and num_p2 in face.order:
                            faceWithpoints.append(face)
        for face in faceWithpoints:
            if abs(face.order.index(num_p1) - face.order.index(num_p2)) == 1 or abs(face.order.index(num_p1) - face.order.index(num_p2)) == 3:
                    return face
        return None




eps = 0.0001

class Vector(object):
    '''
    classdocs
    '''


    def __init__(self, p1, p2 = None):
        '''
        Constructor
        '''
        if p2 is None:
            self.x = p1[0]
            self.y = p1[1]
            self.z = p1[2]
        else:
            self.x = p2.x - p1.x 
            self.y = p2.y - p1.y
            self.z = p2.z - p1.z
    
    def __mul__(self, vector):
        return self.x * vector.x + self.y * vector.y  + self.z * vector.z

    #def __div__(self, f):
    #    return WRLVector((self.x / f, self.y / f, self.z / f))

    #def __add__(self, vector):
    #    return WRLVector((self.x + vector.x, self.y + vector.y, self.z + vector.z))

    def length(self):
        return math.sqrt(self.x * self.x + self.y * self.y + self.z * self.z)

    def angle_between(self, vector):
        l2 = self.length() * vector.length()
        if l2 == 0:
            return 0.0
        try:
            return math.acos(self * vector / l2)
        except ValueError:
            if self * vector / l2 > 1:
                return 0.0
            print("%s angle_between %s %f" % (self, vector, self*vector))
            raise

    def perpendicular(self, vector):
        return Vector((self.y*vector.z - self.z*vector.y,
                          self.z*vector.x - self.x*vector.z,
                          self.x*vector.y - self.y*vector.x))

    def __str__(self):
        return '[%.3f,%.3f,%.3f]' % (self.x, self.y, self.z)

    __repr__ = __str__

    def as_tuple(self):
        return (self.x, self.y, self.z)
