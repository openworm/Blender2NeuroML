from pyneuroml.pynml import read_neuroml2_file
from pyneuroml.pynml import nml2_to_svg
import shutil



all_cells = ['ADAL','AIZL','CEPDR','DVC','IL1DR','RIFL','PVCR','SMBVR','URYDR']
#all_cells = ['AIZL']

info = '## Blender and NeuroML images\n\n'
info2 = ''

for cell in all_cells:
    nml_file = '../Output/C.Elegans_%s.nml'%cell

    nml2_doc = read_neuroml2_file(nml_file)
    print('Loaded NeuroML file: %s'%nml_file)

    '''
    nml2_to_svg(nml_file)
    orig_swc_file = nml_file.replace('.nml','.svg')
    swc_file = orig_swc_file.replace('../Output/', './')
    print('Moving %s to %s'%(orig_swc_file, swc_file))
    shutil.move(orig_swc_file, swc_file)'''

    from pyneuroml.plot.PlotMorphology import plot_2D

    planes = ['yz', 'xz', 'xy']
    for plane in planes:

        p2d_file = nml_file.replace('.nml','.%s.png'%plane).replace('../Output/', './')
        plot_2D(nml_file,
                plane2d  = plane,
                min_width = 0,
                verbose= False,
                nogui = True,
                save_to_file=p2d_file,
                square=True)

    info += ' [%s](#%s) '%(cell,cell.lower())

    info2 += '### %s\n'%cell

    height=250
    info2 += '<table border="0">\n'
    info2 += '   <tr><td>Images generated from NeuroML file <a href="../Output/C.Elegans_%s.nml">C.Elegans_%s.nml</a></td>\n'%(cell,cell)
    #info2 += '   <td>Images generated from NeuroML file <a href="../Output/C.Elegans_%s.nml">C.Elegans_%s.nml</a></td>\n'%(cell,cell)
    info2 += '   <td>Images generated from Blender</td></tr>\n   <tr>\n'
    #info2 += '   <td><img src="C.Elegans_%s.svg" alt="%s" height="600"/></td>\n'%(cell,cell)

    info2 += '   <td>\n'
    for plane in planes:
        info2 += '      <img src="C.Elegans_%s.%s.png" alt="%s_%s" height="%s"/><br/>\n'%(cell,plane, cell, plane, height)

    info2 += '   </td>\n\n'

    info2 += '   <td><img src="../NeuronBlenderImaging/NeuronScreenshots/%s_side.png" alt="%s" height="%s"/><br/>\n'%(cell,cell, height)
    info2 += '   <img src="../NeuronBlenderImaging/NeuronScreenshots/%s_front.png" alt="%s" height="%s"/><br/>\n'%(cell,cell,height)
    info2 += '   <img src="../NeuronBlenderImaging/NeuronScreenshots/%s_top.png" alt="%s" height="%s"/></td></tr>\n\n'%(cell,cell, height)
    info2 += '</table>\n\n'


info += '\n\n%s'%info2


f = open('README.md','w')
f.write(info)
f.close()
