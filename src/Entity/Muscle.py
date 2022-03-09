from __future__ import absolute_import
import numpy
from neuroml import Connection
from NeuroMlEntity.Point import Point
import csv, re, string, sys, math, pprint

CONN_DENSITY_FACTOR = 0.1

connection_file = './Data/stevecooksdata.csv'

def convert_muscle_name(cell_name):
    mobj = re.match('mu_bod_([DV])(\S+)', cell_name)
    if not mobj:
        return cell_name
    return '%sBWM%s' % (string.lower(mobj.group(1)), mobj.group(2))

def parse_substitute_csv(filename, substitute_connect_dict):
    unique_cell_names = {}
    unbracketed_cell_names = {}
    with open(filename, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        cnt = 0
        for row in reader:
            if len(row) < 5:
                print("skip row %s" % row)
                continue
            if not '[' in row[1]:
                unbracketed_cell_names[row[1]] = True
            if not '[' in row[2]:
                unbracketed_cell_names[row[2]] = True
            pre_cell = row[1].strip('[').strip(']')
            post_cel = row[2].strip('[').strip(']')
            try:
                n = int(row[3])
            except ValueError:
                print("skip row %s" % row)
                continue
            try:
                substitute_connect_dict[(pre_cell, post_cel)] += n
            except KeyError:
                substitute_connect_dict[(pre_cell, post_cel)] = n
                if ("BWM" in pre_cell) + ("BWM" in post_cel) == 1:
                    cnt += 1
                    unique_cell_names[pre_cell] = True
                    unique_cell_names[post_cel] = True
        print("parsed %d possible unique muscle-neuron connections" % cnt)
        print("cell names in connections %s" % sorted(unique_cell_names.keys()))
        print("muscles only reported in brackets:")
        for cell_name in sorted(unique_cell_names.keys()):
            if cell_name not in unbracketed_cell_names:
                print(cell_name)

# crude way to save muscle data
def line_segment_list(entity, cell):
    seg_list = []
    for (key, f) in entity.faces.items():
        seg_list.append(add_seg_to_cell(entity, cell, f.order[0], f.order[1]))
        seg_list.append(add_seg_to_cell(entity, cell, f.order[1], f.order[3]))
        seg_list.append(add_seg_to_cell(entity, cell, f.order[3], f.order[2]))
        seg_list.append(add_seg_to_cell(entity, cell, f.order[2], f.order[1]))
    return seg_list

def add_seg_to_cell(entity, cell, index1, index2):
    p1 = entity.vertices[index1]
    p2 = entity.vertices[index2]
    if abs(p2.x - p1.x) + abs(p2.y - p1.y) + abs(p2.z - p1.z) < 1.e-5:
        raise ValueError
    n = len(cell.segments)
    cell.add_segment('Seg%d_muscle_%d' % (n, n), n,
                     1, Point(p1.x, p1.y, p1.z),
                     n-1, Point(p2.x, p2.y, p2.z))
    return ([p1.x, p1.y, p1.z], [p2.x, p2.y, p2.z])

def select_conn_points(conn0, neuron1, muscle1):
    n_seg = neuron1.line_segs[neuron1.index_of_seg[conn0.pre_segment_id]]
    m_seg = muscle1.line_segs[muscle1.index_of_seg[conn0.post_segment_id]]
    n_pt = n_seg[0] + conn0.pre_fraction_along*(n_seg[1] - n_seg[0])
    m_pt = m_seg[0] + conn0.post_fraction_along*(m_seg[1] - m_seg[0])
    return (n_pt, m_pt)

def seg_sort_fn(a, b):
    if a[0].pre_cell_id == b[0].pre_cell_id:
        return cmp(a[0].pre_segment_id, b[0].pre_segment_id)
    return cmp(a[0].pre_cell_id, b[0].pre_cell_id)

#
# Use the neuron-muscle connection info to generate some muscle "segments"
# that correspond to the neuron segments to which it is attached
#

def segments_from_connections(connect_list, neuron_dict, muscle_dict):
    connections_to_muscle = {}
    for (pre_cell, post_cell, close_pairs) in connect_list:
        neuron1 = neuron_dict[pre_cell]
        muscle1 = muscle_dict[post_cell]
        muscle1.cell.segments = []
        if muscle1.cell.name not in connections_to_muscle:
            connections_to_muscle[muscle1.cell.name] = []
        for conn0 in close_pairs:
            pt_pair = select_conn_points(conn0, neuron1, muscle1)
            connections_to_muscle[muscle1.cell.name].append((conn0, pt_pair))
    keys = connections_to_muscle.keys()
    if 0:
        print("segments_from_connections keys %s" % keys)
        print(pprint.PrettyPrinter().pformat(connections_to_muscle))
    keys.sort(lambda a, b, c=connections_to_muscle: cmp(c[a][0][0].pre_segment_id, c[b][0][0].pre_segment_id))
    for name1 in keys:
        muscle1 = muscle_dict[name1]
        conn_list = connections_to_muscle[muscle1.cell.name]
        conn_list.sort(seg_sort_fn)
        for (conn0, pt_pair) in conn_list:
            n = len(muscle1.cell.segments)
            p1 = Point(pt_pair[0][0], pt_pair[0][1], pt_pair[0][2])
            p2 = Point(pt_pair[1][0], pt_pair[1][1], pt_pair[1][2])
            muscle1.cell.add_segment('Seg%d_muscle_%d' % (n, n), n, 1, p1, n-1, p2)
            print("create seg %s:%s to %s:%s" 
                  % (conn0.pre_cell_id, conn0.pre_segment_id,
                     conn0.post_cell_id, conn0.post_segment_id))

#
# The main function of this module. It finds sets of short line segments
# between line segments connecting coordinates taken from a blender file.
#

def connect_with_muscles(neuron_dict, muscle_dict):
    connect_list = []
    substitute_connect_dict = {}
    parse_substitute_csv(connection_file, substitute_connect_dict)
    #print("connect_with_muscles %s  %d subst keys %s"
    #      % (muscle_dict.keys(), len(substitute_connect_dict), substitute_connect_dict.keys()[:5]))
    for ((pre_cell, post_cell), num_sects) in substitute_connect_dict.items():
        if muscle_dict.has_key(pre_cell):
            (pre_cell, post_cell) = (post_cell, pre_cell)
            print("warn = missing neuron %s" % pre_cell)
        if post_cell in muscle_dict:
            if pre_cell not in neuron_dict:
                if pre_cell not in muscle_dict:
                    continue
            print("pair %6s %6s %d sects" % (pre_cell, post_cell, num_sects))

            i = 0
            close_pairs = []
            max_len = 30.0             # controls quality/speed tradeoff
            density_factors = [1, 0.05, 0.025, 0.02, 0.015, 0.01]
            while i < len(density_factors) and len(close_pairs) < num_sects:
                r = connect_a_muscle(neuron_dict[pre_cell],
                                         muscle_dict[post_cell], num_sects,
                                         1000*density_factors[i], max_len)
                (close_pairs, max_len) = r
                print("try %d created %d pairs expect %d max_len %f"
                      % (i, len(close_pairs), num_sects, max_len))
                i += 1
            if len(close_pairs) < num_sects:
                sys.stderr.write("Probable error %s %s expect %d connections, made %d\n"
                                 % (pre_cell, post_cell, num_sects, len(close_pairs)))
            connect_list.append((pre_cell, post_cell, close_pairs))
    return connect_list

#
# split_line_seg is called when a failure on a prior try to create num_sects
# connections suggests we should try a more dense set of connections. It
# breaks a line segment into multiple parts.
#

def split_line_seg(seg1, density_factor):
    v = seg1[1] - seg1[0]
    dist1 = numpy.linalg.norm(v)
    if dist1 < 1.e-4: print("warn split_line_seg d %g %s" % (dist1, seg1))
    seg1_list = []
    p0 = seg1[0]
    n = int(math.ceil(dist1/density_factor))
    n = min(32, n)
    for i in range(n):
        seg1_list.append((p0 + (i/float(n))*v, p0 + ((i+1)/float(n))*v))
    return seg1_list

#
# connect_a_muscle finds connections between 1 neuron and 1 muscle.
#

def connect_a_muscle(neuron1, muscle1, num_sects, density_factor, max_len):

    close_points = []
    close_pairs = []
    neuron_seg_idx = 0
    for n_idx in range(len(neuron1.line_segs)):
        seg01 = neuron1.line_segs[n_idx]
        seg1_list = split_line_seg(seg01, density_factor)
        #if len(seg1_list) > 10:
        #    print("split into %d segs %d" % (len(seg1_list), neuron_seg_idx))
        for seg1 in seg1_list:
            muscle_seg_idx = 0
            for m_idx in range(len(muscle1.line_segs)):
                seg02 = muscle1.line_segs[m_idx]
                seg2_list = split_line_seg(seg02, density_factor)
                for seg2 in seg2_list:
                    (d, p1, p2) = closestDistanceBetweenLines(seg1, seg2)
                    close_points.append((d, p1, p2, n_idx, m_idx))
                muscle_seg_idx += 1
        neuron_seg_idx += 1
    # sort by length
    conn_info = {}
    close_points.sort(lambda a, b: cmp(a[0], b[0]))
    for (d, p1, p2, n_idx, m_idx) in close_points:
        #print("%3d %3d dist %7.2f %s %s" % (n_idx, m_idx, d, p1, p2))
        if d > 2*max_len:
            if len(close_pairs) > num_sects:
                break
            max_len += d
        conn0 = gen_connection(neuron1, muscle1, n_idx, m_idx, p1, p2)
        conn_info[id(conn0)] = (n_idx, m_idx, p1, p2)
        close_pairs.append(conn0)

    unique_close_pairs = []
    m_done = {}
    n_done = {}
    #print("%s pairs %d n segs %d m segs %d sects" % (len(close_pairs), len(neuron1.line_segs), len(muscle1.line_segs), num_sects))
    for conn0 in close_pairs:
        (n_idx, m_idx, neuron_pt, muscle_pt) = conn_info[id(conn0)]
        neuron_idx = neuron1.index_of_seg[conn0.pre_segment_id]
        muscle_idx = muscle1.index_of_seg[conn0.post_segment_id]
        d12 = numpy.linalg.norm(neuron_pt - muscle_pt)
        if d12 > max_len:
            continue
        #print("conn0 %s %s len %6.3f max_len %.2f" % (n_idx, m_idx, d12, max_len))
        min_d = 1.e99
        for conn1 in unique_close_pairs:
            (n_idx1, m_idx1, neuron_pt1, muscle_pt1) = conn_info[id(conn1)]
            r = closestDistanceBetweenLines((neuron_pt, muscle_pt),
                                            (neuron_pt1, muscle_pt1))
            (dist0, dummy1, dummy2) = r
            if 0: # dist0 < 1.e-5 or dist0 is None:
                print("close conns %9.9s %3d-%3d,%3d-%3d %s %s"
                      % (dist0, n_idx, m_idx, conn1.pre_segment_id,
                         conn1.post_segment_id, neuron_pt, muscle_pt))
            if dist0 is not None:
                min_d = min(dist0, min_d)

        if min_d > 1.e8 and len(unique_close_pairs) > 0:
            print("min_d error %3d %3d closest_neighbor %8.3g conn len %6.3f"
                  % (n_idx, m_idx, min_d, d12))
            continue
        if min_d < CONN_DENSITY_FACTOR*density_factor:   # too close to a prior connection?
            #print("pair too close %3d %3d closest_neighbor %8.3g conn len %6.3f"
            #      % (n_idx, m_idx, min_d, d12))
            continue
        print("close_pairs %3d %3d closest_neighbor %8.3g conn len %6.3f"
              % (n_idx, m_idx, min_d, d12))
        unique_close_pairs.append(conn0)
        n_done[id(neuron_pt)] = True
        m_done[id(muscle_pt)] = True
        if len(unique_close_pairs) >= num_sects:
            break
    if len(unique_close_pairs) < num_sects:
        max_len *= 1.25
    return (unique_close_pairs, max_len)

def fract_along_seg(line_seg, pt):
    length1 = numpy.linalg.norm(line_seg[1] - line_seg[0])
    length_from_prox = numpy.linalg.norm(pt - line_seg[0])
    length_from_dist = numpy.linalg.norm(pt - line_seg[1])
    if abs(length_from_dist + length_from_prox - length1) > 0.01:
        print("not on line? %.3f %.3f %.3f %s %s\n"
              % (length_from_dist, length_from_prox, length1, line_seg, pt))
        raise RuntimeWarning
    return length_from_prox / length1

next_conn_id = 0

def gen_connection(neuron1, muscle1, n_idx, m_idx, neuron_pt, muscle_pt):
    neuron_seg = neuron1.cell.segments[n_idx]
    muscle_seg = muscle1.cell.segments[m_idx]
    best_neuron_fract = fract_along_seg(neuron1.line_segs[n_idx], neuron_pt)
    best_muscle_fract = fract_along_seg(muscle1.line_segs[m_idx], muscle_pt)
    global next_conn_id
    next_conn_id += 1
    return Connection(id=next_conn_id,
                      pre_cell_id="../%s/0/%s"%(neuron1.cell.name, neuron1.cell.name),
                      pre_segment_id = neuron_seg.id,
                      pre_fraction_along = best_neuron_fract,
                      post_cell_id="../%s/0/%s"%(muscle1.cell.name, muscle1.cell.name),
                      post_segment_id = muscle_seg.id,
                      post_fraction_along = best_muscle_fract)


# adapted from http://stackoverflow.com/users/1429402/fnord
# at http://stackoverflow.com/questions/2824478/shortest-distance-between-two-line-segments/2824626#2824626

def closestDistanceBetweenLines(seg1, seg2, verbose = False):
    ''' Given two lines defined by numpy.array pairs (a0,a1,b0,b1)
        Return distance, and the two closest points
    '''
    (a0, a1) = seg1
    (b0, b1) = seg2
    A = a1 - a0
    B = b1 - b0

    try:
        Anorm = A / numpy.linalg.norm(A)
    except RuntimeWarning:
        print(A)
        raise
    Bnorm = B / numpy.linalg.norm(B)
    cross = numpy.cross(Anorm, Bnorm)


    # If denominator is 0, lines are parallel
    denom = numpy.linalg.norm(cross)**2

    if (denom == 0):
        if verbose: print("parallel lines")
        return (None, None, None)

    # Calculate the dereminent and return points
    t = (b0 - a0)
    det0 = numpy.linalg.det([t, Bnorm, cross])
    det1 = numpy.linalg.det([t, Anorm, cross])

    t0 = det0/denom
    t1 = det1/denom

    pA = a0 + (Anorm * t0)
    pB = b0 + (Bnorm * t1)
    intersect_outside_a = (t0 < 0 or t0 > numpy.linalg.norm(A))
    intersect_outside_b = (t1 < 0 or t1 > numpy.linalg.norm(B))
    if intersect_outside_a and intersect_outside_b:
        (pA, pB) = select_closest_pair((a0, a1), (b0, b1))
    elif intersect_outside_a:
        (pA, pB) = select_closest_pair((a0, a1), (b0, b1, pB))
    elif intersect_outside_b:
        (pA, pB) = select_closest_pair((a0, a1, pA), (b0, b1))
    if verbose:
        print("pA %s a0 %s A %s t0 %.3f %d %d"
              % (pA, a0, A, t0, intersect_outside_a, intersect_outside_b))

    d = numpy.linalg.norm(pA-pB)

    return d,pA,pB

def select_closest_pair(a_points, b_points):
    min_d = 1.e99
    for a in a_points:
        for b in b_points:
            len1 = numpy.linalg.norm(a - b)
            if len1 < min_d:
                min_d = len1
                best_pair = (a, b)
    return best_pair
