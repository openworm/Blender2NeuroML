'''
Created on 19.08.2011

@author: Sergey Khayrulin
'''
from __future__ import absolute_import
from Entity.Helper import HelpPoint
from Entity.Vertex import Vertex
import pprint

class Slice(list):
    '''
    Definition for Slice
    '''
    
    def __init__(self, coll, faces, use_method2 = False, vertices = None):
        '''
        Get collection of point and return first found slice
        '''
        coll_dict = {}
        for v in coll:
            coll_dict[v.point] = v
        if use_method2:
            self.construct_method2(coll, coll_dict, faces, vertices)
            return
        for v in coll:
            del self[:]
            sidepoint = []
            #faceswithV = [faces[i] for i in filter(lambda key:" %s,"%v.point in key, faces.keys())]
            for face in faces.WithPoints(v.point, v.point):
                for p in face.order:
                    if p != v.point:
                        if faces.hasFaceWithSide(p, v.point):
                            hp = self.__getPoint(coll_dict, p)
                            if hp is not None and not sidepoint.__contains__(hp):
                                sidepoint.append(hp)
            #print("%d %d sidepoints" % (v.point, len(sidepoint)))
            for s in sidepoint:
                for s1 in sidepoint:
                    if s != s1:
                        #faceswithpoints = [faces[key] for key in filter(lambda k:" %s,"%s.point in k or " %s,"%s1.point in k,faces.keys())]
                        for face in faces.WithPoints(s.point, s1.point):
                            for vertex in face.order:
                                p = self.__getPoint(coll_dict, vertex)
                                if p is not None and p != s and p != s1 and p != v: 
                                    if( faces.hasFaceWithSide(p.point, s.point) and
                                        faces.hasFaceWithSide(p.point, s1.point)):
                                        #print("faces %s %s %s %s" % (v.point,s.point,s1.point,p.point))
                                        if faces[[s.point, s1.point, v.point, p.point]] is None:
                                            self.__getSlice([v,s,s1,p],faces)
                                            return None
        #print("Slice constructor fall through to end")
    
    def __getPoint(self,coll_dict,point):
        try:
            return coll_dict[point]
        except KeyError:
            return None
        #tempColl = list(filter(lambda p:p.point == point,coll))
        #if len(tempColl) != 0:
        #    return tempColl[0]
        #else:
        #    return None

    def add_adjacent_points(self, maybe_center_ring, adjacentPoints, cluster, done, point_idx1):
        for next_point_idx in adjacentPoints[point_idx1]:
            if done.has_key(next_point_idx):
                continue
            if maybe_center_ring.has_key(next_point_idx):
                cluster.append(next_point_idx)
                done[next_point_idx] = True
                self.add_adjacent_points(maybe_center_ring, adjacentPoints, cluster, done, point_idx1)


    def __find_adjacent_vertices(self, faces, num_p1):
        '''
        Find for two point adjacent vertices
        '''
        adjacentVertices = []
        for key,f in faces.items():
            for i in range(4):
                if num_p1 == f.order[i]:
                    for j in range(4):
                        if abs(j-i) in (1, 3): # adjacent in face to num_p1
                            p2 = f.order[j]
                            if not adjacentVertices.__contains__(p2):
                                adjacentVertices.append(p2)
        return adjacentVertices

    #
    # construct_method2 is used when the first attempt to find a Slice
    # in the neuron finds nothing. That typically means the soma is
    # represented by many small faces. It finds the largest group of faces
    # whose neighbors are all close (compared to distances between neighbors
    # for the whole neuron), and classifies them as part of the soma.
    # It uses the center of the vertices in that soma and finds groups of
    # 4 vertices having 5 adjacent vertices connected to it via faces.
    # (i.e. vertices likely to be at the start of the axon or dendrite.
    # It uses the group with the largest perimeter as the Slice.
    #


    def construct_method2(self, coll, coll_dict, faces, vertices):
        best_index = {}
        best_slice_perimeter = 0
        maybe_center_ring = {}
        adjacentPoints = {}
        for i in range(len(coll)):
            best_dist = 1.e6
            best_idx = None
            point_idx1 = coll[i].point
            adjacentPoints[point_idx1] = self.__find_adjacent_vertices(faces, point_idx1)
            if 0:
                print("maybe_center_ring %3d %5.1f %5.1f %5.1f %s" \
                      % (point_idx1,
                         vertices[point_idx1].len_between_point(Vertex(2.825,-282.763, 52.762997)),
                         vertices[point_idx1].len_between_point(Vertex(2.95,-281.725, 52.725)),
                         vertices[point_idx1].len_between_point(Vertex(2.7,-283.80002, 52.8)),
                         adjacentPoints[point_idx1]))
            if len(adjacentPoints[point_idx1]) == 3:
                maybe_center_ring[point_idx1] = adjacentPoints[point_idx1]

        # find cluster of close points
        shortest_radii = 1.e9
        points_maybe_in_soma = []
        network_size = {}
        for (point_idx1, point_list) in adjacentPoints.items():
            max_dist = 0
            for p2 in point_list:
                max_dist = max(max_dist, vertices[point_idx1].len_between_point(vertices[p2]))
            if len(point_list) > 0:
                if max_dist < shortest_radii:
                    shortest_radii = max_dist
                points_maybe_in_soma.append((point_idx1, max_dist))
                network_size[point_idx1] = max_dist
            #print("point_in_soma %d %.3f" % (point_idx1, max_dist))
        points_maybe_in_soma.sort(lambda a, b: cmp(a[1], b[1]))
        print("shortest_radii %f" % shortest_radii)
        points_in_soma = []
        x = y = z = 0
        n = 0
        done = {}
        for (point_idx1, max_dist) in points_maybe_in_soma:
            if max_dist < 3*shortest_radii: # ?????
                pt_list = points_in_close_network(point_idx1, network_size, shortest_radii, adjacentPoints, done)
                if len(pt_list) > len(points_in_soma):
                    print("possible soma size %d" % len(pt_list))
                    points_in_soma = pt_list
                pt = vertices[point_idx1]
                x += pt.x
                y += pt.y
                z += pt.z
                n += 1
        center_pt = Vertex(x/float(n), y/float(n), z/float(n))
        #print("center_pt %5.2f" % center_pt.len_between_point(Vertex(2.825,-282.763, 52.762997)))
        best_d = 1.e9
        slice_points = []
        for (point_idx1, point_list) in adjacentPoints.items():
            if len(point_list) == 5:
                d = center_pt.len_between_point(vertices[point_idx1])
                #print("5adj dist %5.2f %3d" % (d, point_idx1))
                best_d = min(d, best_d)
                slice_points.append((point_idx1, d))


        self.extra_dict = {'points_in_soma' : points_in_soma,
                           'center_pt' : center_pt,
                           'adjacentPoints' : adjacentPoints,
                           }
        if len(slice_points) < 4:
            print("give up %s" % slice_points)
            return
        print("best_d %.2f %s" % (best_d, slice_points))
        for (point_idx1, dist) in slice_points:
            if dist > 2*best_d:
                continue
            max_dist = 0
            for (point_idx2, dist2) in slice_points:
                if point_idx2 != point_idx1 and dist2 <= 2*best_d:
                    dist_from1 = vertices[point_idx1].len_between_point(vertices[point_idx2])
                    if dist_from1 > max_dist:
                        max_dist = dist_from1
                        far_point_in_soma = point_idx2
            adj_pt = adjacentPoints[point_idx1][0]
            far_adj_pt = adjacentPoints[far_point_in_soma][0]
            slice_points1 = [HelpPoint(point_idx1, 0),
                            HelpPoint(adj_pt, 0),
                            HelpPoint(far_point_in_soma, 0),
                            HelpPoint(far_adj_pt, 0)]
            del self[:]
            for p in slice_points1:
                super(Slice,self).append(p)
            print("slice %d %d %d %d dist %5.2f vertices %d"
                  % (point_idx1, adj_pt, far_point_in_soma, far_adj_pt, max_dist, len(self)))
            if len(self) < 4:
                continue
            perimeter = self.getPerimetr(vertices)
            if perimeter > best_slice_perimeter and len(self) == 4:
                best_slice_perimeter = perimeter
                best_slice = slice_points1
                print("best_slice %s perimeter %f" % (best_slice, perimeter))
        del self[:]
        for p in best_slice:
            super(Slice,self).append(p)
                

    
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
            #print('i %d points %d %d' % (i, self[i].point, self[(i+1)%len(self)].point))
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
        print(str_t)


#
# AlternateSlice constructs a Slice through algorithms that bear little
# resemblance to the original Slice constructor. It is typically passed
# 4 or somewhat more points that are near each other, and just selects
# the first 4 of those.
#

class AlternateSlice(Slice):
    def __init__(self, coll, faces, vertices, checked_points, start_point = None, adjacentPoints = None, allow_checked = False):
        min_dist = 1.e9
        if adjacentPoints is None:
            if not coll:
                #print("AlternateSlice coll %d" % len(coll))
                return
            point_idx1 = coll[0].point
        else:
            # Construct an initial Slice based on a starting point that is
            # in the soma. It finds vertices near that start point which
            # have more connections than a typical part of the soma.
            maybe_axon_start = []
            for p in coll:
                d = start_point.len_between_point(vertices[p.point])
                if len(adjacentPoints[p.point]) == 5:
                    maybe_axon_start.append((p.point, d))
                if d < min_dist:
                    min_dist = d
                    point_idx1 = p.point
            maybe_axon_start.sort(lambda a,b: cmp(a[1], b[1]))
            #print("AlternateSlice select %d %s" % (point_idx1, maybe_axon_start[:4]))
            if len(maybe_axon_start) >= 4:
                for (p, d) in maybe_axon_start[:4]:
                    self.append(HelpPoint(p, d))
                return
        if len(coll) == 2:
            # We weren't passed enough points to generate a complete slice,
            # so look for a few more adjacent ones that haven't already been
            # used.
            face = faces.getFaceWithSide(coll[0].point, coll[1].point)
            if face:
                for p in face.order:
                    if not HelpPoint(p,0) in coll:
                        if not allow_checked and p in checked_points:
                            print("ignore, points were checked")
                            return
                        coll.append(HelpPoint(p, 0))
                        #print("add pt %d" % p)
            else:
                print("warn no face")
        self.append(HelpPoint(point_idx1, 0))
        for p in coll:
            if p.point == point_idx1: continue
            #print("add to %d: %d?" % (point_idx1, p.point))
            if not self.__contains__(p) and len(self) < 4:
                self.append(p)
                #print("AlternateSlice %3d %3d %5.2f" % (point_idx1, p.point, p.lenght))
        self.sort(lambda a, b: cmp(a.point, b.point))
        if 0 and len(self) != 4:
            print("warning AlternateSlice size %d" % len(self))
        #for i in range(len(self)):
        #    for j in range(i):
        #        print("%d,%d have point %s" % (self[i].point, self[j].point, faces.hasFaceWithSide(self[i].point, self[j].point)))

def points_in_close_network(point, network_size, shortest_radii, adjacentPoints, done):
    result = [point]
    done[point] = True
    print("points_in_soma %3d %5.2f %d adj pts" % (point, network_size[point], len(adjacentPoints[point])))
    for p in adjacentPoints[point]:
        if done.has_key(p) or network_size[p] > 3*shortest_radii:
            continue
        result += points_in_close_network(p, network_size, shortest_radii, adjacentPoints, done)
    return result
