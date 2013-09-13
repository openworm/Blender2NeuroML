'''
Created on 03.06.2011

@author: Sergey Khayrulin
'''
from Vertex import Vertex
from Face import Face
from Slice import Slice
from Helper import *

class Entity(object):
    '''
    Main Class which process data from blender file or WRL(formated file).
    '''
    def __init__(self):
        '''
        Constructor
        '''
        self.vertices = []
        self.faces = Faces()
        self.resulting_points = []
        self.checked_points = []
        self.neuronInfo = ''
    
    def add_vertex(self, coordinates):
        '''
        Method add vertex to collection point. It get a 
        collection of coordinates of point, create point 
        and append it to collection of point.
        '''
        try:
            if len(coordinates) != 3:
                raise ParserException('Error')
            point = Vertex(float(coordinates[0]),float(coordinates[1]),float(coordinates[2]))
            self.vertices.append(point)
        except ParserException as ex:
            print 'It should be some incorrect data'
            raise ex
    
    def add_face(self, points_arr):
        '''
        Method add face to faces collection. It get a sequence 
        of numbers which means position in point collection.       
        '''
        try:
            if len(points_arr) < 4:
                raise ParserException('Face contains more that 4 point')
            face = Face(self.vertices[int(points_arr[0])],self.vertices[int(points_arr[1])],self.vertices[int(points_arr[2])],self.vertices[int(points_arr[3])])
            face.order = [int(points_arr[0]),int(points_arr[1]),int(points_arr[2]),int(points_arr[3])]
            self.faces[face.order] = face
            #self.faces.append(face)
        except ParserException as ex:
            print 'Error:%s'%ex
            print points_arr
            raise ex 

    def findCenterOfSoma(self):
        '''
        Method find start point for work main algorithm
        first point should be in soma. Soma is the 
        biggest segment of cell. 
        '''
        iter = 0
        temp_points = []
        slices = []
        for p in range(len(self.vertices)):
            temp_points.append(HelpPoint(p,0))
        slice = Slice(temp_points,self.faces)
        slices.append(slice)
        while len(slice) != 0:
            temp_points = filter(lambda p: not slice.__contains__(p), temp_points)
            slice = None
            slice = Slice(temp_points,self.faces)
            if len(slice) != 0:
                slices.append(slice)
                print len(temp_points)
                #slice.printSlice()
                #print slice.getPerimetr(self.vertices)
                
        perimiter_coll = sorted(slices,key=lambda slice:slice.getPerimetr(self.vertices), reverse=True)
        startSlice = Slice(perimiter_coll[0],self.faces)
        self.start_center_point = self.__getCenterPoint(startSlice)
        self.start_center_point.diametr = 2 * self.start_center_point.len_between_point(self.vertices[perimiter_coll[0][0].point])
        
    def getAllBrunches(self):
        '''
        Method return dictionary which contains pair key=>value:
        key it's name of neurite, value - it's sorted sequence 
        numbers which means position in resulting_points collection  
        for instance 'axon' => [1,2,4]        
        '''
        brunches_temp = {}
        result_coll = {}
        i = 0
        roots = [self.resulting_points.index(p) for p in self.resulting_points \
                 if p.parentPoint == 0 and self.resulting_points.index(p) != 0] 
        for root in roots:
            brunches_temp[root] = []
            for p in self.resulting_points:
                parent = p.getRoot(self.resulting_points)
                if parent == root:
                    brunches_temp[root].append(self.resulting_points.index(p))
        for k1, value in sorted(brunches_temp.iteritems(),key=lambda (k,v):(len(v),k),reverse=True): # we try to determine  
            if i == 0:
                for j in value:
                    self.resulting_points[j].isAxon = True
                result_coll['axon'] = value
            else:
                for j in value:
                    if self.resulting_points[j].cable != 2:
                        self.resulting_points[j].isDendrite = True
                        self.resulting_points[j].cable = 3
                result_coll['dendrite' + str(i)] = value
            i += 1
        return result_coll
    
    def find_point(self,center_point=Vertex(),iteration=0,
                   parentPoint=0, isNeurite=False, 
                   isBrunchStart=False, _slice=None):
        '''
        Main function find axon dendrite and neurite
        '''
        vector_len = []
        if iteration == 0: center_point = self.start_center_point
        if isNeurite:
            res_point = Result_Point(center_point,parentPoint,2,isBrunchStart)
            res_point.isNeurite = True 
            self.resulting_points.append(res_point)
        elif iteration != 0:
            self.resulting_points.append(Result_Point(center_point,parentPoint,1,isBrunchStart))
        elif iteration == 0:
            self.resulting_points.append(Result_Point(center_point,parentPoint,0,isBrunchStart))
        current_point = len(self.resulting_points) - 1
        for p in range(len(self.vertices)):
            vector_len.append(HelpPoint(p,self.vertices[p].len_between_point(center_point)))
        vector_len = sorted(vector_len,key=lambda p:p.lenght)
        if iteration != 0:
            '''
            If iteration != 0 that means we are should find next 4 or more(if we find place of brunching 6 or 8) vertices
            '''
            if _slice != None:
                slice = _slice
            else:
                slice = Slice(vector_len,self.faces)
            adjacentPoints = []
            for p in range(4):
                if p != 3:
                    coll = self.__find_adjacent_vertices(slice[p].point, slice[p+1].point)
                else:
                    coll = self.__find_adjacent_vertices(slice[p].point, slice[0].point)
                for c in coll:
                    helpPoint = HelpPoint(c,self.vertices[c].len_between_point(center_point))
                    if not adjacentPoints.__contains__(helpPoint):
                        if not self.checked_points.__contains__(c):
                            adjacentPoints.append(helpPoint)
            if len(adjacentPoints) == 0: return
            '''
            If we find 8 adjacent vertices it means that we place in branching segments
            '''
            if len(adjacentPoints) > 4:
                if self.__more4AdjacentPointCase(adjacentPoints, slice, isBrunchStart,iteration, current_point, center_point):
                    return
            del vector_len[:]
            vector_len = [HelpPoint(p.point,self.vertices[p.point].len_between_point(center_point)) 
                          for p in adjacentPoints if not self.checked_points.__contains__(p.point)]
            vector_len = sorted(vector_len,key=lambda p:p.lenght)
        slice = Slice(vector_len,self.faces)
        lenOfSlice = len(slice)
        if lenOfSlice == 0:
            slice = vector_len
        new_center_point = self.__getCenterPoint(slice)
        iteration += 1
        if lenOfSlice != 0:
            self.find_point(new_center_point,iteration,parentPoint=current_point,isNeurite=isNeurite,isBrunchStart=False, _slice=slice)
        else:
            if isNeurite:
                res_point = Result_Point(new_center_point,current_point,2,False)
                res_point.isNeurite = True 
                self.resulting_points.append(res_point)
            elif iteration != 0:
                    self.resulting_points.append(Result_Point(new_center_point,current_point,1,False))
        if iteration == 1:
            self.__checkDendrite(slice, center_point, vector_len,current_point)
       
    def __getCenterPoint(self, slice):
        '''
        Get center point like center of mass for input collection slice (usually it should be 4 point) 
        '''
        x=y=z=0
        for p in range(4):
            x += self.vertices[slice[p].point].x
            y += self.vertices[slice[p].point].y
            z += self.vertices[slice[p].point].z
            if not self.checked_points.__contains__(slice[p].point):
                self.checked_points.append(slice[p].point)
        center_point = Vertex(x/4,y/4,z/4)
        center_point.diametr = 2 * center_point.len_between_point(self.vertices[slice[0].point])
        slice.printSlice()
        return center_point
    
    def __find_adjacent_vertices(self, num_p1,num_p2):
        '''
        Find for two point adjacent vertices
        '''
        adjacentVertices = []
        for key,f in self.faces.items():
            if f.order.__contains__(num_p1) and f.order.__contains__(num_p2):
                for p in f.order:
                    if p != num_p1 and p != num_p2:
                        adjacentVertices.append(p)
        return adjacentVertices
    
    def __fillUpBrachesCollection(self, adjacentPoints, slice):
        '''
        Fill branches collection 
        '''
        branchesCollection = []
        for i in range(4):
            if i != 3:
                for p1 in adjacentPoints:
                    for p2 in adjacentPoints:
                        s = Slice([slice[i], slice[i + 1], p1, p2], self.faces)
                        if (p1 != p2 and len(s) == 4):
                            if not branchesCollection.__contains__(s):
                                branchesCollection.append(s)
            
            else:
                for p1 in adjacentPoints:
                    for p2 in adjacentPoints:
                        s = Slice([slice[i], slice[0], p1, p2], self.faces)
                        if (p1 != p2 and len(s) == 4):
                            if not branchesCollection.__contains__(s):
                                branchesCollection.append(s)
        
        if len(Slice(adjacentPoints, self.faces)) != 0:
            branchesCollection.append(Slice(adjacentPoints, self.faces))
        return branchesCollection

    def __more4AdjacentPointCase(self, adjacentPoints, slice, isBrunch,iteration, current_point, center_point):
        '''
        Work when algorithm find more that 4 adjacent points 
        '''
        branchesCollection = self.__fillUpBrachesCollection(adjacentPoints, slice)
        if len(branchesCollection) >= 2 :
            center_points = {}
            thirdBrunchCollection = []
            for branch in branchesCollection:
                branch_center_point = self.__getCenterPoint(branch) 
                center_points[branch_center_point] = branch
            for branch_center_point,branch in center_points.items():
                self.find_point(branch_center_point,iteration,current_point,True,True, _slice=branch)
                if len(adjacentPoints) > 6:
                    thirdBrunchCollection.extend(branch) 
            thirdBrunchPoints = [HelpPoint(p.point,self.vertices[p.point].len_between_point(center_point)) \
                       for p in thirdBrunchCollection if not slice.__contains__(p)]
            slice_t = Slice(thirdBrunchPoints, self.faces)
            if len(slice_t) == 4:
                third_brunch_center_point = self.__getCenterPoint(slice_t)
                self.find_point(third_brunch_center_point,iteration, current_point,True,True, _slice=slice_t)
            return True
        elif len(branchesCollection) == 0 or (len(branchesCollection) == 1 and not isBrunch):
                sortedadjacentPoints = sorted(adjacentPoints,key=lambda p:p.lenght)
                first_slice = Slice(sortedadjacentPoints,self.faces)
                second_slice = Slice(filter(lambda p: first_slice.__contains__(p) == False, sortedadjacentPoints),self.faces)
                perimeter_1 = first_slice.getPerimetr(self.vertices)
                perimeter_2 = second_slice.getPerimetr(self.vertices)
                if perimeter_1 > perimeter_2 and perimeter_2 != 0:
                    new_center_point = self.__getCenterPoint(second_slice)
                    self.find_point(new_center_point,iteration, current_point,False,False, _slice=second_slice)
                    return True
                elif perimeter_1 < perimeter_2 or perimeter_2 == 0:
                    if perimeter_1 == 0:
                        if len(branchesCollection) == 1:
                            first_slice = branchesCollection[0] 
                        else:
                            first_slice.getFaceFromColl(adjacentPoints,self.faces)
                        new_center_point = self.__getCenterPoint(first_slice)
                        self.find_point(new_center_point,iteration, current_point,isBrunch,False, _slice=first_slice)
                    else:
                        new_center_point = self.__getCenterPoint(first_slice)
                        self.find_point(new_center_point,iteration, current_point,False,False, _slice=first_slice)
                    return True
        elif len(branchesCollection) == 1 and isBrunch:
            slice = branchesCollection[0]
            if len(slice) == 0:
                slice = slice.getFaceFromColl(adjacentPoints,self.faces)
            new_center_point = self.__getCenterPoint(slice)
            self.find_point(new_center_point,iteration, parentPoint=current_point,isNeurite=True,isBrunchStart=False, _slice=slice)
            return True
        return False
    
    def __checkDendrite(self, slice, center_point, vector_len, current_point):
        '''
        Private Method.
        Check if soma has other output processes
        if it's contain than run find_point for it.
        '''
        iteration = 1
        vector_len = filter(lambda p: slice.__contains__(p) == False 
                                and self.checked_points.__contains__(p.point) == False, vector_len)
        vector_len = sorted(vector_len,key=lambda p:p.lenght)
        for i in range(5):
            slice2 = Slice(vector_len,self.faces)
            if (len(slice2) == 4 and
                int(slice.getPerimetr(self.vertices) / slice2.getPerimetr(self.vertices)) <= 1 and 
                int(slice2.getPerimetr(self.vertices) / slice.getPerimetr(self.vertices)) <= 1):
                new_center_point = self.__getCenterPoint(slice2) 
                iteration += 1
                self.find_point(new_center_point,iteration,parentPoint=current_point,isNeurite=False,isBrunchStart=False, _slice=slice2)
            vector_len = filter(lambda p: slice2.__contains__(p) == False 
                                and self.checked_points.__contains__(p.point) == False, vector_len)
            vector_len = sorted(vector_len, key=lambda p:p.lenght)    