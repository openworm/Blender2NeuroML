#!/usr/bin/env python

import bpy

# This is required in order for `import numpy` to succeed on Debian.
import sys
sys.path.append("/usr/lib/python3/dist-packages")

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
    # N.B. this array construction involves a funky coordinate shuffle.
    coordset = numpy.array([numpy.zeros(resolution), bezier_poly(p[:,0], t), bezier_poly(p[:,1], t)])
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

        pointsets.append(base + bezier_pointset(ctrlpoints))

    return numpy.concatenate(pointsets)


def pointset_to_objects(pointset):
    """
    This function is just for visualization of intermediate data
    (i.e. debugging).
    """
    for point in pointset:
        print(point)
        mesh = bpy.data.meshes.new("b" + str(point))
        ob = bpy.data.objects.new("b" + str(point), mesh)
        ob.location = point
        bpy.context.scene.objects.link(ob)

if __name__ == '__main__':
    spine = bpy.data.objects['Center spine for worm model']
    bzspline = spine.data.splines[0]
    pointset = bezier_spline_pointset(numpy.array(spine.location), bzspline)

    pointset_to_objects(pointset)

    #bpy.ops.wm.save_mainfile(check_existing = False)
