#!/usr/bin/env python
#
# (c) 2013  Petr Baudis <pasky@ucw.cz>
# MIT licence
#
# Blender script for straightening worm data (mesh objects) assuming that
# (i) the worm is already straight along the x axis, and (ii) a bezier curve
# 'Center spine for worm model' is put through the middle of the worm body
# all along.
#
# Example: blender virtualworm.blend -P blenderStraighten.py
#
# Algorithm: The spine curve is converted to a densely segmented line;
# then, for each mesh vertex, the nearest point on this line is found,
# distance on the line (from its beginning) is used as the y coordinate,
# distance of the vertex from the line is used as the z coordinate.

import bpy
import mathutils

# This is required in order for `import numpy` to succeed on Debian.
import sys
sys.path.append("/usr/lib/python3/dist-packages")

import math
import numpy

def bezier_poly(p, t):
    """
    Evaluate the Bezier polynomial at a particular @t point.
    """
    return (1-t)**3*p[0] + 3*(1-t)**2*t*p[1] + 3*(1-t)*t**2*p[2] + t**3*p[3]

def bezier_pointset(p, resolution = 100):
    """
    Interpolate the Bezier curve of given control points.
    """
    t = numpy.linspace(0.0, 1.0, resolution)
    coordset = numpy.array([numpy.zeros(resolution), bezier_poly(p[:,1], t), bezier_poly(p[:,2], t)])
    return coordset.T

def bezier_spline_pointset(base, bzspline):
    """
    bzspline is a sequence of bezier curves where each curve
    spans from [i].co to [i+1].co with control points
    [i].handle_right and [i+1].handle_left.

    Interpolate a set of points on this bzspline.
    """
    pointsets = []

    for i in range(len(bzspline.bezier_points)-1):
        bzleft = bzspline.bezier_points[i]
        bzright = bzspline.bezier_points[i+1]
        ctrlpoints = numpy.array([bzleft.co, bzleft.handle_right, bzright.handle_left, bzright.co])
        # print('===', i, ctrlpoints)

        pointset_1 = base + bezier_pointset(ctrlpoints)
        if i < len(bzspline.bezier_points)-2:
            # remove the last point, which will be re-added
            # by the next spline segment
            pointset_1 = numpy.delete(pointset_1, len(pointset_1)-1, 0)
            pass
        pointsets.append(pointset_1)

    return numpy.concatenate(pointsets)


def pointset_mileage(pointset):
    """
    Distance (approximated by straight lines) from the spine beginning,
    to be used as the Y coordinate of straightened worm.
    """
    # @distances lists pointwise distances between successive pairs
    # of points
    distances = numpy.sqrt(numpy.sum((pointset[1:] - pointset[:-1]) ** 2, 1))

    mileage = 0.
    mileageset = [0.]
    # Simple accumulation
    for i in range(len(distances)):
        mileage += distances[i]
        mileageset.append(mileage)
    return mileageset


def pointset_to_objects(pointset):
    """
    This function is just for visualization of intermediate data
    (i.e. debugging).
    """
    for point in pointset:
        # print(point)
        mesh = bpy.data.meshes.new("b" + str(point))
        ob = bpy.data.objects.new("b" + str(point), mesh)
        ob.location = point
        bpy.context.scene.objects.link(ob)


def nearest_point_pair(pointset, coord):
    """
    Return the two nearest points in pointset, leftmost first.
    """
    # XXX: Extremely naive, compute distances to all points and sort
    distances = numpy.sqrt((pointset[:,0] - coord[0]) ** 2 + (pointset[:,1] - coord[1]) ** 2 + (pointset[:,2] - coord[2]) ** 2)
    dist_i = sorted(zip(distances, range(len(distances))), key = lambda o: o[0])
    i, j = dist_i[0][1], dist_i[1][1]
    if i > j:
        i, j = j, i
    return (i, j)

def transform_coord(pointset, newyset, coord):
    """
    Reinterpolate the coordinate of each vertex of each object
    by using pointset as the axis guide.
    """
    i, j = nearest_point_pair(pointset, coord)
    #print(i, j)

    # We are interested in the nearest point @k on line [i,j];
    # this point can be then used to interpolate y from newyset,
    # distance from @k to @coord is then z.

    # Note that pointset[.], coord [0] is the x-coordinate which
    # we are not recomputing (the worm is already straight along
    # the x axis). The other indices are therefore used shifted
    # accordingly.

    d_ij = pointset[j] - pointset[i]
    v = numpy.array([d_ij[1], d_ij[2]])
    w = numpy.array([-v[1], v[0]]) # w is perpendicular to v; v always points rightwards
    w = w / numpy.sqrt(numpy.dot(w, w)) # normalize w
    #print('v', v, 'w', w)

    # Find an intersection between lines [i] + s*v and coord + t*w:
    # [i]0 + s*v0 = coord0 + t*w0      [i]1 + s*v1 = coord1 + t*w1
    # t = ([i]0 + s*v0 - coord0) / w0  [i]1 + s*v1 = coord1 + ([i]0 + s*v0 - coord0) * w1/w0
    # => [i]1 + s*v1 = coord1 + [i]0*w1/w0 + s*v0*w1/w0 - coord0*w1/w0
    # => s*v1 - s*v0*w1/w0 = coord1 + [i]0*w1/w0 - [i]1 - coord0*w1/w0
    # => s = (coord1 + [i]0*w1/w0 - [i]1 - coord0*w1/w0) / (v1 - v0*w1/w0)
    s = (coord[2] + pointset[i][1]*w[1]/w[0] - pointset[i][2] - coord[1]*w[1]/w[0]) / (v[1] - v[0]*w[1]/w[0])
    t = (pointset[i][1] + s*v[0] - coord[1]) / w[0]

    # s is in [0,1], usable for interpolation
    # t is unit vector, so we can directly use it as z (distance from spine)
    y = (1. - s) * newyset[i] + s * newyset[j]
    z = t
    return mathutils.Vector((coord[0], y, z))

def transform_objects(pointset, newyset, objectset):
    """
    Reinterpolate the coordinate of each vertex of each object
    by using pointset as the axis guide.
    """

    for o in objectset:
        # Make sure the object vertices correspond to true location
        bpy.context.scene.objects.active = o
        o.select = True
        bpy.ops.object.transform_apply(scale=True, rotation=True)
        o.select = False

        print(o)
        for i in range(len(o.data.vertices)):
            v = o.data.vertices[i]
            coord_in = v.co + o.location
            #print(':-', v.co, '=>', v.co + o.location, '=', coord_in, 'loc', o.location)

            coord_out = transform_coord(pointset, newyset, coord_in)
            o.data.vertices[i].co = coord_out - o.location
            #print(':+', coord_out, '=>', coord_out - o.location, '=', o.data.vertices[i].co, 'loc', o.location)

        o.data.update()


if __name__ == '__main__':
    bpy.ops.object.mode_set(mode='OBJECT')

    # Convert the spine to a dense sequence of sampled points on the spine
    spine = bpy.data.objects['Center spine for worm model']
    bzspline = spine.data.splines[0]
    pointset = bezier_spline_pointset(numpy.array(spine.location), bzspline)

    # Compute Y coordinates in straightened worm corresponding to the pointset
    mileageset = pointset_mileage(pointset)
    newybase = mileageset[-1] / 2.
    newyset = list(map(lambda x: x - newybase, mileageset))

    # Debug stop along the way:
    #pointset_to_objects(pointset)
    #bpy.ops.wm.save_mainfile(check_existing = False)

    # Transform mesh coordinates by interpolation
    transform_objects(pointset, newyset, filter(lambda o: o.type == "MESH", bpy.data.objects))
