'''
Created on 19.08.2011

@author: Sergey Khayrulin
'''
from Helper import HelpPoint
class Slice(list):
    '''
    Definition for Slice
    '''
    
    def __init__(self, coll, faces):
        '''
        Get collection of point and return first found slice
        '''
        arr_p = []
        for v in coll:
            del arr_p [:]
            del self[:]
            sidepoint = []
            faceswithV = [faces[i] for i in filter(lambda key:" %s,"%v.point in key, faces.keys())]
            for face in faceswithV:
                for p in face.order:
                    if p != v.point:
                        if faces.hasFaceWithSide(p, v.point):
                            hp = self.__getPoint(coll, p)
                            if hp != None and not sidepoint.__contains__(hp):
                                sidepoint.append(hp)
            for s in sidepoint:
                for s1 in sidepoint:
                    if s != s1:
                        faceswithpoints = [faces[key] for key in filter(lambda k:" %s,"%s.point in k or " %s,"%s1.point in k,faces.keys())]
                        for face in faceswithpoints:
                            for vertex in face.order:
                                p = self.__getPoint(coll, vertex)
                                if p != None and p != s and p != s1 and p != v: 
                                    if( faces.hasFaceWithSide(p.point, s.point) and
                                        faces.hasFaceWithSide(p.point, s1.point)):
                                        if faces[[s.point, s1.point, v.point, p.point]] == None:
                                            self.__getSlice([v,s,s1,p],faces)
                                            return None
    
    
    def __getPoint(self,coll,point):
        tempColl = filter(lambda p:p.point == point,coll)
        if len(tempColl) != 0:
            return tempColl[0]
        else:
            return None
    
    def __eq__(self, slice):
        if  super(Slice,self).__contains__(slice[0]) and \
            super(Slice,self).__contains__(slice[1]) and \
            super(Slice,self).__contains__(slice[2]) and \
            super(Slice,self).__contains__(slice[3]):
            return True
        return False
        
    def __getSlice(self,coll,faces):
        '''
        Return rectangle for sequence of point.
        
        Rectangle - is the sequence of 4 vertices which closed 
        (there are face with side with vertex in first and second vertices) 
        isn't a face. If collection isn't contain any rectangle method 
        returns empty collection.    
        '''
        #self = []
        arr_p = []
        arr_p.append(0)
        super(Slice,self).append(coll[0])
        while len(arr_p) != 4:
            temp_len = len(arr_p)
            for p in range(4):
                if not arr_p.__contains__(p):
                    if faces.hasFaceWithSide(coll[p].point, coll[arr_p[-1]].point):
                        super(Slice,self).append(coll[p])
                        arr_p.append(p)
                        break
            if temp_len == len(arr_p):
                break
            if len(self) == 4:
                break
        ''' Check if  obtain rectangle is closed last point has a common side with first '''
        if len(self) == 4:
            if faces.hasFaceWithSide(self[0].point, self[-1].point):
                return
        self = []
        return
    
    def getFaceFromColl(self, coll, faces):
        '''
        Get collection of point and return first found face
        '''        
        arr_p = []
        #self = []
        for v in coll:
            del arr_p [:]
            sidepoint = []
            for p in coll:
                if p != v:
                    if faces.hasFaceWithSide(p.point, v.point):
                        sidepoint.append(p)
            for s in sidepoint:
                for s1 in sidepoint:
                    if s != s1:
                        for p in coll:
                            if p != s and p != s1 and p != v: 
                                if( faces.hasFaceWithSide(p.point, s.point) and
                                    faces.hasFaceWithSide(p.point, s1.point)):
                                    self.__getSlice([v,s,s1,p],faces)
                                    return
        return []
    
    def getPerimetr(self, vertices):
        '''
        Get perimeter of slice
        '''
        perimetr = 0
        for i in range(len(self)):
            if i != 3:
                perimetr += vertices[self[i].point].len_between_point(vertices[self[i+1].point])
            else:
                perimetr += vertices[self[i].point].len_between_point(vertices[self[0].point])
        return perimetr
    
    def printSlice(self):
        '''
        Print slice collection in wrl format
        '''
        str_t ='\t\t\t '
        for p in self:
            str_t += str(p.point) + ', '
        str_t += ' -1,'
        print str_t