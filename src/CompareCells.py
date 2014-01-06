# -*- coding: utf-8 -*-

############################################################

#    A simple script to look for differences in .nml files

############################################################

from neuroml import NeuroMLDocument
from neuroml import Network
from neuroml import Population
from neuroml import Instance
from neuroml import Location
from neuroml import Projection
from neuroml import Connection
import neuroml.writers as writers
import neuroml.loaders as loaders

from NeuroMLUtilities import validateNeuroML2
from NeuroMLUtilities import getSegmentIds
from NeuroMLUtilities import get3DPosition

import sys

def compare2(filename1, filename2):

    doc1 = loaders.NeuroMLLoader.load(filename1)
    morphology1 = doc1.cells[0].morphology
    segment_list1 = morphology1.segments

    doc2 = loaders.NeuroMLLoader.load(filename2)
    morphology2 = doc2.cells[0].morphology
    segment_list2 = morphology2.segments

    if len(segment_list1) != len(segment_list2):
        print("different number of segments: %d versus %d" % (len(segment_list1),
                                                              len(segment_list2)))
    else:
        compare_segments(segment_list1, segment_list2)

    morphology1.segment_groups.sort(lambda a, b: cmp(a.id, b.id))
    morphology2.segment_groups.sort(lambda a, b: cmp(a.id, b.id))
    for i in range(len(morphology2.segment_groups)):
        seg_group1 = morphology1.segment_groups[i]
        seg_group2 = morphology2.segment_groups[i]
        if seg_group1.id != seg_group2.id:
            print("error group %s != %s" % (seg_group1.id, seg_group2.id))
            continue
        print("group %s" % seg_group1.id)
        if len(seg_group1.members) != len(seg_group2.members):
            print("error %d members versus %d" % (len(seg_group1.members), len(seg_group2.members)))
        for j in range(len(seg_group1.members)):
            member1 = seg_group1.members[j]
            if member1.segments != seg_group2.members[j].segments:
                print("error %s != %s" % (member1.segments, seg_group2.members[j].segments))
                continue
            print("\tmembers %s" % member1.segments)
        for include1 in seg_group1.includes:
            print("\tincludes %s" % include1.segment_groups)


def compare_segments(segment_list1, segment_list2):
    totd = 0.0
    maxd = 0.0
    seg_of_maxd = None
    totratio = 0.0

    for seg_idx in range(len(segment_list1)):
        pt1 = segment_list1[seg_idx].distal
        pt2 = segment_list2[seg_idx].distal
        d = length3d(pt1, pt2)
        totd += d
        if d > maxd:
            maxd = d
            seg_of_maxd = seg_idx
        if pt2.x > 0:
            totratio += pt1.x/pt2.x
    if len(segment_list1) != 0:
        n = float(len(segment_list1))
        print("Average difference in coordinate location: %f" % (totd/n))
        print("Max difference in coordinate location: %f at %d" % (maxd, seg_of_maxd))
        print("Ratio of coordinates: %f" % (totratio/n))

def length3d(pt1, pt2):
    prox_x = pt1.x
    prox_y = pt1.y
    prox_z = pt1.z

    dist_x = pt2.x
    dist_y = pt2.y
    dist_z = pt2.z

    length = ((prox_x-dist_x)**2 + (prox_y-dist_y)**2 + (prox_z-dist_z)**2)**(0.5)

    return length


if __name__ == "__main__":

    if len(sys.argv) < 3:
        print("I need 2 filenames")
    else:
        compare2(sys.argv[1], sys.argv[2])
