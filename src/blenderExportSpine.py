#- invoke from blender, not as a standalone script -
#
# (c) 2013  Petr Baudis <pasky@ucw.cz>
# MIT licence
#
# Blender script that will dump data of the bezier curve 'Center spine
# for worm model' which shall put through the middle of the worm body
# model all along. This can then be used for processing e.g. NeuroML
# data accordingly.
#
# Example: blender virtualworm.blend -P blenderExportSpine.py
#
# Algorithm: The spine curve is converted to a densely segmented line;
# then, for each mesh vertex, the nearest point on this line is found,
# distance on the line (from its beginning) is used as the y coordinate,
# distance of the vertex from the line is used as the z coordinate.

import bpy
import mathutils
import sys

# This is required in order for `import numpy` to succeed on Debian.
stardard_os = {'win32', 'cygwin', 'darwin'}
if sys.platform not in stardard_os:
    sys.path.append("/usr/lib/python3/dist-packages")

import math
import numpy

OUTFILE = "spine-spline.tsv"

def tj(a):
    """ Tab Join """
    return "\t".join(map(lambda i: str(i), a))
def cj(a):
    """ Comma Join """
    return ",".join(map(lambda i: str(i), a))

def bezier_spline_dump(f, base, bzspline):
    """
    bzspline is a sequence of bezier curves where each curve
    spans from [i].co to [i+1].co with control points
    [i].handle_right and [i+1].handle_left.

    Print out the parameters of the bzspline, one curve per line.
    """
    for i in range(len(bzspline.bezier_points)-1):
        bzleft = bzspline.bezier_points[i]
        bzright = bzspline.bezier_points[i+1]
        print(tj([cj(base + bzleft.co), cj(base + bzleft.handle_right), cj(base + bzright.handle_left), cj(base + bzright.co)]), file = f)


if __name__ == '__main__':
    f = open(OUTFILE, 'w')

    # Convert the spine to a dense sequence of sampled points on the spine
    spine = bpy.data.objects['Center spine for worm model']
    bzspline = spine.data.splines[0]
    bezier_spline_dump(f, numpy.array(spine.location), bzspline)

    f.close()
