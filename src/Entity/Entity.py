'''
Created on 03.06.2011

@author: Sergey Khayrulin
'''

from __future__ import absolute_import
from Entity.Vertex import Vertex
from Entity.Face import Face
from Entity.Slice import Slice, AlternateSlice
from Entity.Helper import *
import pprint
import math

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

    def clean_all(self):
        self.faces.clean_all()
    
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
            print('It should be some incorrect data')
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
            #print("add_face %s" % face.order)
            #self.faces.append(face)
        except ParserException as ex:
            print('Error:%s'%ex)
            print(points_arr)
            raise ex 

    def findCenterOfSoma(self, use_method2 = False):
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
        if use_method2:
            startSlice = Slice(temp_points,self.faces, use_method2 = True, vertices = self.vertices)
            point_on_perimeter = self.vertices[startSlice[0].point]
            self.checked_points += startSlice.extra_dict['points_in_soma']
            self.start_center_point = startSlice.extra_dict['center_pt']
            self.start_center_point.diametr = 2 * self.start_center_point.len_between_point(point_on_perimeter)
            self.starting_slice = startSlice
            return
        slice = Slice(temp_points,self.faces)
        slices.append(slice)
        while len(slice) != 0:
            temp_points = list([p for p in temp_points if not slice.__contains__(p)])
            slice = None
            slice = Slice(temp_points,self.faces)
            if len(slice) != 0:
                slices.append(slice)
                #if not (iter % 10):
                #    print('slice %d iter %d' % (len(temp_points), iter))
                #slice.printSlice()
                #print slice.getPerimetr(self.vertices)
            iter += 1
        # find slice with longest line segments
        perimiter_coll = sorted(slices,key=lambda slice:slice.getPerimetr(self.vertices), reverse=True)
        startSlice = Slice(perimiter_coll[0],self.faces)
        #print("findCenterOfSoma while loop done %d %d" % (iter, len(temp_points)))
        try:
            self.start_center_point = self.__getCenterPoint(startSlice, minimal = True)
        except IndexError:
            print("no center point startSlice %d perimiter_coll %d"
                  % (len(startSlice), len(perimiter_coll[0])))
            for face in self.faces.keys():
                print("face order %s" % face)
            # the coordinates aren't organized in a pattern that the normal
            # code in Slice can understand, so we use an alternate method
            return self.findCenterOfSoma(use_method2 = True)
        if not use_method2:
            point_on_perimeter = self.vertices[perimiter_coll[0][0].point]
        self.start_center_point.diametr = 2 * self.start_center_point.len_between_point(point_on_perimeter)
        
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
        # the first of these two lines works with python3, the second with python2:
        print('>>> %s' % brunches_temp)
        for k1, value in sorted(brunches_temp.items(),key=lambda k,v:(len(v),k),reverse=True): # we try to determine  
        #for k1, value in sorted(brunches_temp.iteritems(),key=lambda (k,v):(len(v),k),reverse=True): # we try to determine  
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

    def use_alt_slice(self):
        return hasattr(self, 'starting_slice')

    def create_slice(self, coll, allow_checked = False):
        if self.use_alt_slice():
            if not allow_checked:
                coll = [p for p in coll if not self.checked_points.__contains__(p.point)]
            slice = AlternateSlice(coll,self.faces, self.vertices, self.checked_points, self.vertices[self.starting_slice[0].point], None, allow_checked)
        else:
            slice = Slice(coll,self.faces)
        return slice

    def branching(self, slice):
        if not self.use_alt_slice():
            return False
        for p in range(len(slice)):
            if len(self.starting_slice.extra_dict['adjacentPoints'][slice[p].point]) == 5:
                return True
        return False
    
    def find_point(self,center_point=Vertex(),iteration=0,
                   parentPoint=0, isNeurite=False, 
                   isBrunchStart=False, _slice=None):
        '''
        Main function find axon dendrite and neurite
        '''
        vector_len = []
        print("enter find_point iteration %d isBrunchStart %d" % (iteration, isBrunchStart))
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
        tmp_list = []
        if iteration != 0:
            '''
            If iteration != 0 that means we are should find next 4 or more(if we find place of brunching 6 or 8) vertices
            '''
            if _slice is not None:
                slice = _slice
            else:
                slice = self.create_slice(vector_len)
            adjacentPoints = []
            use_v5 = iteration >= 3 and self.branching(slice) # with 5 adjacent points
            for p in range(4):
                if use_v5 and not isBrunchStart:
                    c = slice[p].point
                    tmp_list.append(c)
                    adjacentPoints.append(HelpPoint(c, self.vertices[c].len_between_point(center_point)))
                if use_v5 and isBrunchStart:
                    #print("use_v5 br %d p %d" % (len(slice), p))
                    coll = self.__find_adjacent_vertices5(slice[p].point)
                elif p != 3:
                    coll = self.__find_adjacent_vertices(slice[p].point, slice[p+1].point)
                else:
                    coll = self.__find_adjacent_vertices(slice[p].point, slice[0].point)
                #print("%d-%d has %d adj v" % (slice[p].point, slice[(p+1)%4].point, len(coll)))
                for c in coll:
                    helpPoint = HelpPoint(c,self.vertices[c].len_between_point(center_point))
                    #print("%3d %3d is checked? %d" % (p, c, self.checked_points.__contains__(c)))
                    if not adjacentPoints.__contains__(helpPoint):
                        if not self.checked_points.__contains__(c):
                            adjacentPoints.append(helpPoint)
                            tmp_list.append(c)
            print("got %d adjacentPoints %s" % (len(adjacentPoints), tmp_list))
            if len(adjacentPoints) == 0: return
            '''
            If we find 8 adjacent vertices it means that we place in branching segments
            '''
            if len(adjacentPoints) > 4 and not (use_v5 and isBrunchStart):
                if self.__more4AdjacentPointCase(adjacentPoints, slice, isBrunchStart,iteration, current_point, center_point):
                    return
            del vector_len[:]
            vector_len = [HelpPoint(p.point,self.vertices[p.point].len_between_point(center_point)) 
                          for p in adjacentPoints if not self.checked_points.__contains__(p.point)]
            vector_len = sorted(vector_len,key=lambda p:p.lenght)
        if self.use_alt_slice():
            vector_len = [p for p in vector_len if not self.checked_points.__contains__(p.point)]
            if iteration == 0:
                adj_dict = self.starting_slice.extra_dict['adjacentPoints']
            else:
                adj_dict = None
            slice = AlternateSlice(vector_len,self.faces, self.vertices, self.checked_points, self.vertices[self.starting_slice[0].point], adj_dict)
        else:
            slice = Slice(vector_len,self.faces)
        lenOfSlice = len(slice)
        print("lenOfSlice %d iter %d %d" % (lenOfSlice, iteration, len(vector_len)))
        if lenOfSlice == 0:
            slice = vector_len
        if len(slice) < 4:
            return
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
       
    def __getCenterPoint(self, slice, minimal = False):
        '''
        Get center point like center of mass for input collection slice (usually it should be 4 point) 
        '''
        x=y=z=0
        n_points = 4
        if len(slice) < 4:
            print("Bad slice len %d" % len(slice))
            if minimal and len(slice) > 0:
                n_points = len(slice)
            else:
                raise IndexError
        for p in range(n_points):
            x += self.vertices[slice[p].point].x
            y += self.vertices[slice[p].point].y
            z += self.vertices[slice[p].point].z
            if not self.checked_points.__contains__(slice[p].point):
                self.checked_points.append(slice[p].point)
        center_point = Vertex(x/n_points,y/n_points,z/n_points)
        center_point.diametr = 2 * center_point.len_between_point(self.vertices[slice[0].point])
        if isinstance(slice, Slice):
            slice.printSlice()
        else:
            print(slice)
        return center_point
    
    def __find_adjacent_vertices(self, num_p1,num_p2):
        '''
        Find for two point adjacent vertices
        '''
        adjacentVertices = []
        for key,f in list(self.faces.items()):
            if f.order.__contains__(num_p1) and f.order.__contains__(num_p2):
                for p in f.order:
                    if p != num_p1 and p != num_p2:
                        adjacentVertices.append(p)
        return adjacentVertices
    
    def __find_adjacent_vertices5(self, num_p1):
        '''
        Find for one point adjacent vertices
        '''
        adjacentVertices = []
        for key,f in self.faces.items():
            if f.order.__contains__(num_p1):
                for p in f.order:
                    if p != num_p1 and not (p in adjacentVertices):
                        near_old_point = False
                        for r_pt in self.resulting_points:
                            dist = r_pt.point.len_between_point(self.vertices[p])
                            if dist < r_pt.point.diametr:
                                near_old_point = True
                                break
                        if not near_old_point:
                            adjacentVertices.append(p)
        return adjacentVertices
    
    def __fillUpBrachesCollection(self, adjacentPoints, slice):
        '''
        Fill branches collection 
        '''
        branchesCollection = []
        for i in range(4):
            for p1 in adjacentPoints:
                for p2 in adjacentPoints:
                    if p1 == p2:
                        continue
                    s = self.create_slice([slice[i], slice[(i + 1) % 4], p1, p2],
                                          allow_checked = True)
                    if (len(s) == 4):
                        if not branchesCollection.__contains__(s):
                            branchesCollection.append(s)
        
        if len(self.create_slice(adjacentPoints)) != 0:
            branchesCollection.append(self.create_slice(adjacentPoints))
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
            print("%d center_points" % (len(list(center_points.keys()))))
            for branch_center_point,branch in list(center_points.items()):
                old_num_r_points = len(self.resulting_points)
                print("start branch %d %d %d %d size %d %3d resulting_points"
                      % (branch[0].point, branch[1].point, branch[2].point, branch[3].point, len(branch), len(self.resulting_points)))
                self.find_point(branch_center_point,iteration,current_point,True,True, _slice=branch)
                print("finish branch %d %3d resulting_points" % (branch[0].point, len(self.resulting_points)))
                if self.use_alt_slice() and len(self.resulting_points) == old_num_r_points + 1:
                    del self.resulting_points[-1]
                    print("undo branches of length 1")
                if len(adjacentPoints) > 6:
                    thirdBrunchCollection.extend(branch) 
            thirdBrunchPoints = [HelpPoint(p.point,self.vertices[p.point].len_between_point(center_point)) \
                       for p in thirdBrunchCollection if not slice.__contains__(p)]
            slice_t = self.create_slice(thirdBrunchPoints)
            if len(slice_t) == 4:
                third_brunch_center_point = self.__getCenterPoint(slice_t)
                self.find_point(third_brunch_center_point,iteration, current_point,True,True, _slice=slice_t)
            return True
        elif len(branchesCollection) == 0 or (len(branchesCollection) == 1 and not isBrunch):
                sortedadjacentPoints = sorted(adjacentPoints,key=lambda p:p.lenght)
                first_slice = self.create_slice(sortedadjacentPoints)
                second_slice = self.create_slice([p for p in sortedadjacentPoints if first_slice.__contains__(p) == False])
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
            try:
                new_center_point = self.__getCenterPoint(slice)
            except IndexError:
                print("Warning: __getCenterPoint failed, slice len %d, %d adjacentPoints"
                      % (len(slice), len(adjacentPoints)))
                slice.printSlice()
                return False
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
        vector_len = [p for p in vector_len if slice.__contains__(p) == False 
                                and self.checked_points.__contains__(p.point) == False]
        vector_len = sorted(vector_len,key=lambda p:p.lenght)
        for i in range(5):
            slice2 = self.create_slice(vector_len)
            if (len(slice2) == 4 and
                int(slice.getPerimetr(self.vertices) / slice2.getPerimetr(self.vertices)) <= 1 and 
                int(slice2.getPerimetr(self.vertices) / slice.getPerimetr(self.vertices)) <= 1):
                new_center_point = self.__getCenterPoint(slice2) 
                iteration += 1
                self.find_point(new_center_point,iteration,parentPoint=current_point,isNeurite=False,isBrunchStart=False, _slice=slice2)
            vector_len = [p for p in vector_len if slice2.__contains__(p) == False 
                                and self.checked_points.__contains__(p.point) == False]
            vector_len = sorted(vector_len, key=lambda p:p.lenght)    

    #
    # check_unused_coordinates might be of some use in checking for
    # sections of a neuron that were omitted due to flaws in the code
    #

    def check_unused_coordinates(self):
        for key,f in self.faces.items():
            unused = True
            for p in f.order:
                if p in self.checked_points:
                    unused = False
                    break
            if unused:
                print("unused face %s" % f.order)