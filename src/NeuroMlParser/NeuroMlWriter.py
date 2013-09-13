'''
Created on 07.06.2011

@author: Sergey
'''

from xml.dom.minidom import Document 
from NeuroMlParser.Constants import *
from NeuroMlEntity.Constants import neurite

class NeuroMlWriter(object):
    '''
    Definition for NeuroMlWriter
    '''
    def __init__(self,doc_name=''):
        '''
        Constructor
        '''
        self.docname = doc_name
        self.out_doc = Document()
        self.neuroml_element = self.out_doc.createElement('neuroml')
        self.neuroml_element.setAttribute('xmlns','http://morphml.org/neuroml/schema')
        self.neuroml_element.setAttribute('xmlns:' + meta_ns,'http://morphml.org/metadata/schema')
        self.neuroml_element.setAttribute('xmlns:' + mml_ns,'http://morphml.org/morphml/schema')
        self.neuroml_element.setAttribute('xmlns:' + bio_ns,'http://morphml.org/biophysics/schema')
        self.neuroml_element.setAttribute('xmlns:' + cml_ns,'http://morphml.org/channelml/schema')
        self.neuroml_element.setAttribute('xmlns:' + net_ns,'http://morphml.org/networkml/schema')
        self.neuroml_element.setAttribute('xmlns:' + xsi_ns,'http://www.w3.org/2001/XMLSchema-instance')
        self.neuroml_element.setAttribute('xmlns:' + schemaLocation_ns,'http://morphml.org/neuroml/schema  NeuroML.xsd')
        self.neuroml_element.setAttribute('lengthUnits','micron')
        self.out_doc.appendChild(self.neuroml_element)
        self.cells_element = self.out_doc.createElement('cells')
        self.neuroml_element.appendChild(self.cells_element)
        self.isHasNeuriteGroup = False
        
    def addCell(self, cell):
        '''
        Add new NeuroMl cell to neuroMlWriter 
        '''
        seg_id = 2
        cell_ellement = self.out_doc.createElement('cell')
        cell_ellement.setAttribute('name', cell.name)
        self.cells_element.appendChild(cell_ellement)
        notes_ellement = self.out_doc.createElement(meta_ns + ':notes')
        ptext = self.out_doc.createTextNode(cell.note)
        notes_ellement.appendChild(ptext)
        cell_ellement.appendChild(notes_ellement)
        segments_ellement = self.out_doc.createElement(mml_ns + ':segments')
        cell_ellement.appendChild(segments_ellement)
        for segment in cell.segments:
            self.addSegment(segments_ellement,segment)
        cables_ellement = self.out_doc.createElement(mml_ns + ':cables')
        cell_ellement.appendChild(cables_ellement)
        self.addSomaGroups(cables_ellement)
        self.addAxonGroups(cables_ellement)
        if cell.numOfDendrite != 0:
            num = 0
            num = cell.numOfDendrite - 1
            for i in range(num):
                self.addDendriteGroups(cables_ellement,seg_id)
                seg_id += 1
        if cell.numOfNeurite != 0:
            num = 0
            if cell.numOfDendrite != 0:
                num = cell.numOfNeurite - cell.numOfDendrite
            else:
                num = cell.numOfNeurite - 1
            for i in range(num):
                self.addNeuriteGroups(cables_ellement,seg_id)
                seg_id += 1
        
            
    def addSegment(self,segments_ellement,segment):
        '''
        Add segments for cell
        '''
        segment_ellement = self.out_doc.createElement(mml_ns + ':segment')
        segment_ellement.setAttribute('id',str(segment.id))
        segment_ellement.setAttribute('name',segment.name)
        if segment.parent != -1:
            segment_ellement.setAttribute('parent',str(segment.parent))
        segment_ellement.setAttribute('cable',str(segment.cable))
        segments_ellement.appendChild(segment_ellement)
        if segment.position.proximal_point != None:
            proximal_ellement = self.out_doc.createElement(mml_ns + ':proximal')
            proximal_ellement.setAttribute('x',str(segment.position.proximal_point.x))
            proximal_ellement.setAttribute('y',str(segment.position.proximal_point.y))
            proximal_ellement.setAttribute('z',str(segment.position.proximal_point.z))
            proximal_ellement.setAttribute('diameter',str(segment.position.proximal_point.diameter))
            segment_ellement.appendChild(proximal_ellement)
        distal_ellement = self.out_doc.createElement(mml_ns + ':distal')
        distal_ellement.setAttribute('x',str(segment.position.distal_point.x))
        distal_ellement.setAttribute('y',str(segment.position.distal_point.y))
        distal_ellement.setAttribute('z',str(segment.position.distal_point.z))
        distal_ellement.setAttribute('diameter',str(segment.position.distal_point.diameter))
        segment_ellement.appendChild(distal_ellement)
        
        
    def addSomaGroups(self, cables_ellement):
        '''
        Add Soma Groups 
        '''
        cable_soma_group_ellement = self.out_doc.createElement(mml_ns + ':cable')
        cable_soma_group_ellement.setAttribute('id', '0')
        cable_soma_group_ellement.setAttribute('name', 'Soma')
        cables_ellement.appendChild(cable_soma_group_ellement)
        group1_soma_group_ellement = self.out_doc.createElement(meta_ns + ':group')
        ptext = self.out_doc.createTextNode('all')
        group1_soma_group_ellement.appendChild(ptext)
        cable_soma_group_ellement.appendChild(group1_soma_group_ellement)
        group2_soma_group_ellement = self.out_doc.createElement(meta_ns + ':group')
        ptext = self.out_doc.createTextNode('soma_group')
        group2_soma_group_ellement.appendChild(ptext)
        cable_soma_group_ellement.appendChild(group2_soma_group_ellement)
        
    def addAxonGroups(self, cables_ellement):
        '''
        Add Axon Groups 
        '''
        cable_axon_group_ellement = self.out_doc.createElement(mml_ns + ':cable')
        cable_axon_group_ellement.setAttribute('id', '1')
        cable_axon_group_ellement.setAttribute('name', 'Axon')
        cables_ellement.appendChild(cable_axon_group_ellement)
        group1_axon_group_ellement = self.out_doc.createElement(meta_ns + ':group')
        ptext = self.out_doc.createTextNode('all')
        group1_axon_group_ellement.appendChild(ptext)
        cable_axon_group_ellement.appendChild(group1_axon_group_ellement)
        group2_axon_group_ellement = self.out_doc.createElement(meta_ns + ':group')
        ptext = self.out_doc.createTextNode('axon_group')
        group2_axon_group_ellement.appendChild(ptext)
        cable_axon_group_ellement.appendChild(group2_axon_group_ellement)
        
    def addNeuriteGroups(self, cables_ellement, numOfGroup):
        '''
        Add neurite Groups 
        '''
        cable_neurite_group_ellement = self.out_doc.createElement(mml_ns + ':cable')
        cable_neurite_group_ellement.setAttribute('id', str(numOfGroup))
        cable_neurite_group_ellement.setAttribute('name', 'Neurite' + str(numOfGroup))
        cables_ellement.appendChild(cable_neurite_group_ellement)
        group1_neurite_group_ellement = self.out_doc.createElement(meta_ns + ':group')
        ptext = self.out_doc.createTextNode('all')
        group1_neurite_group_ellement.appendChild(ptext)
        cable_neurite_group_ellement.appendChild(group1_neurite_group_ellement)
        group2_neurite_group_ellement = self.out_doc.createElement(meta_ns + ':group')
        ptext = self.out_doc.createTextNode('neurite_group')
        group2_neurite_group_ellement.appendChild(ptext)
        cable_neurite_group_ellement.appendChild(group2_neurite_group_ellement)
        
    def addDendriteGroups(self, cables_ellement, numOfGroup):
        '''
        Add dendrite Groups 
        '''
        cable_dendrite_group_ellement = self.out_doc.createElement(mml_ns + ':cable')
        cable_dendrite_group_ellement.setAttribute('id', str(numOfGroup))
        cable_dendrite_group_ellement.setAttribute('name', 'Dendrite' + str(numOfGroup))
        cables_ellement.appendChild(cable_dendrite_group_ellement)
        group1_dendrite_group_ellement = self.out_doc.createElement(meta_ns + ':group')
        ptext = self.out_doc.createTextNode('all')
        group1_dendrite_group_ellement.appendChild(ptext)
        cable_dendrite_group_ellement.appendChild(group1_dendrite_group_ellement)
        group2_dendrite_group_ellement = self.out_doc.createElement(meta_ns + ':group')
        ptext = self.out_doc.createTextNode('dendrite_group')
        group2_dendrite_group_ellement.appendChild(ptext)
        cable_dendrite_group_ellement.appendChild(group2_dendrite_group_ellement)
        
    def printDocument(self):
        '''
        print document to output stream 
        to console
        '''
        print self.out_doc.toprettyxml(indent="  ")
        
    def writeDocumentToFile(self):
        '''
        Write document to xml file
        '''
        try:
            f = open('./Output/' + self.docname + '.xml', 'w')
            f.write(self.out_doc.toprettyxml(indent="  "))
            f.close()
            print 'NeuroMl was save in file %s in folder Output', self.docname + '.xml'
        except IOError as ex:
            print 'NeuroMl wasn''t saved because : %s' % ex.strerror
            