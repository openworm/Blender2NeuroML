from __future__ import absolute_import
import math
import numpy
import matplotlib.pyplot as plotter
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from .Muscle import select_conn_points

def plot_connect(connect_list, neuron_dict, muscle_dict):

    fig = plotter.figure()
    ax = Axes3D(fig)

    colors = ('b', 'r', 'c', 'y', 'k',)
    print("plot_connect %d" % len(connect_list))

    for (pre_cell, post_cell, close_pairs) in connect_list:
        neuron1 = neuron_dict[pre_cell]
        muscle1 = muscle_dict[post_cell]
        color1 = '0.8'
        for w in (neuron1.entity, muscle1.entity):
            for (key, face1) in w.faces.items():
                x = []
                y = []
                z = []
                for p in face1.order:
                    pt = w.vertices[p]
                    if pt.len_between_point(muscle1.entity.vertices[0]) < 5000:
                        x.append(pt.x)
                        y.append(pt.y)
                        z.append(pt.z)
                ax.plot(x, y, zs = z, zdir='z', color = color1)
            color1 = 'g'
        if muscle1.cell.segments:
            color1 = 'y'
            pt = muscle1.cell.segments[0].position.proximal_point
            x = [pt.x]
            y = [pt.y]
            z = [pt.z]
            for seg in muscle1.cell.segments:
                last_pt = pt
                pt = seg.position.distal_point
                dist = math.sqrt((pt.x - last_pt.x)**2 + (pt.y - last_pt.y)**2 + (pt.z - last_pt.z)**2)
                print("plot seg %s len %.3f" % (seg.id, dist))
                x.append(pt.x)
                y.append(pt.y)
                z.append(pt.z)
            ax.plot(x, y, zs = z, zdir='z', color = color1)


        color_index = 0
        for conn0 in close_pairs:
            pt_pair = select_conn_points(conn0, neuron1, muscle1)
            color1 = colors[color_index % len(colors)]
            print("plot len %6.3f color %s %s"
                  % (numpy.linalg.norm(pt_pair[1] - pt_pair[0]),
                     color1, pt_pair))
            x = [pt_pair[0][0], pt_pair[1][0]]
            y = [pt_pair[0][1], pt_pair[1][1]]
            z = [pt_pair[0][2], pt_pair[1][2]]
            ax.plot(x, y, zs = z, zdir='z', color = 'b', linewidth = 2)
            color_index += 1

    plotter.show()

def plot_multi(point_lists):
    fig = plotter.figure()
    i = 0
    colors = ('b', 'r', 'c', 'y', 'k',)
    for points in point_lists:
        x = []
        y = []
        z = []
        for pt in points:
            x.append(pt.x)
            y.append(pt.y)
            z.append(pt.z)

        ax = Axes3D(fig)
        ax.plot(x, y, zs = z, zdir='z', color = colors[i % len(colors)])
        i += 1
    plotter.show()


def plot_faces(w):

    fig = plotter.figure()

    ax = Axes3D(fig)

    for (key, face1) in w.faces.items():
        x = []
        y = []
        z = []
        p0 = w.vertices[face1.order[0]]
        if 0:
        #if abs(p0.z) > 54.5 or not (-1.5 < p0.x < 4.5) or not (-277 < p0.y < -256):
        #if abs(p0.z) > 54.5 or not (2.5 < p0.x < 5) or not (-292 < p0.y < -270):
        #if abs(p0.z) < 54.5 or not (1 < p0.x < 5.5) or not (-337 < p0.y < -270):
            continue
        for p in face1.order:
            pt = w.vertices[p]
            x.append(pt.x)
            y.append(pt.y)
            z.append(pt.z)
        if 246 in face1.order and 247 in face1.order and 248 in face1.order:
        #if 366 in face1.order and 367 in face1.order and 368 in face1.order:
        #if 272 in face1.order and 277 in face1.order and 278 in face1.order:
                verts = [zip(x, y, z)]
                poly = Poly3DCollection(verts)
                poly.set_facecolor('0.5')
                ax.add_collection3d(poly, zs = z, zdir='z')
        else:
            ax.plot(x, y, zs = z, zdir='z', color = 'b')

    if 0:
        x = []
        y = []
        z = []
        for p in [259, 258, 261, 260]: #[351, 360, 374, 379,375, 376, 377, 378,]:#[351, 359, 345, 348]: #[375, 376, 377, 378,]:#  (302, 304, 305, 307):
            pt = w.vertices[p]
            x.append(pt.x)
            y.append(pt.y)
            z.append(pt.z)
        ax.plot(x, y, zs = z, zdir='z', color = 'g')
    if 0:
        x = []
        y = []
        z = []
        for p in [25, 39]:
            pt = w.vertices[p]
            x.append(pt.x)
            y.append(pt.y)
            z.append(pt.z)
        ax.plot(x, y, zs = z, zdir='z', color = 'r')
    plotter.show()


def plot(points):

    fig = plotter.figure()
    x = []
    y = []
    z = []
    for pt in points:
        x.append(pt.x)
        y.append(pt.y)
        z.append(pt.z)

    ax = Axes3D(fig)
    ax.plot(x, y, zs = z, zdir='z')

    plotter.show()

def cvt_pt(p):
    from neuroml import Point3DWithDiam
    return Point3DWithDiam(x=p.x, y=p.y, z=p.z, diameter = p.diameter)

def plot_segs(segments):

    fig = plotter.figure()
    ax = Axes3D(fig)
    color1 = 'b'
    pt = cvt_pt(segments[0].proximal)
    x = [pt.x]
    y = [pt.y]
    z = [pt.z]
    for seg in segments:
        last_pt = pt
        pt = cvt_pt(seg.distal)
        dist = math.sqrt((pt.x - last_pt.x)**2 + (pt.y - last_pt.y)**2 + (pt.z - last_pt.z)**2)
        x.append(pt.x)
        y.append(pt.y)
        z.append(pt.z)
    ax.plot(x, y, zs = z, zdir='z', color = color1)
    plotter.show()
