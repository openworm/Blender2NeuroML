'''
Created on 07.06.2011

@author: Sergey
'''

from xml.dom.minidom import Document 
from NeuroMlParser.Constants import *
from NeuroMlEntity.Constants import soma_name, axon_name, dendrite_name, neurite_name
import re

class NeuroMlWriter(object):
    '''
    Definition for NeuroMlWriter
    '''
    def __init__(self,doc_name='', cell_name = ''):
        '''
        Constructor
        '''
        self.docname = doc_name
        self.out_doc = Document()
        self.neuroml_element = self.out_doc.createElement('neuroml')
        self.neuroml_element.setAttribute('xmlns', 'http://www.neuroml.org/schema/neuroml2')
        self.neuroml_element.setAttribute('xmlns:' + xsi_ns,'http://www.w3.org/2001/XMLSchema-instance')
        self.neuroml_element.setAttribute('xsi:' + schemaLocation_ns,'http://www.neuroml.org/schema/neuroml2  https://raw.github.com/NeuroML/NeuroML2/master/Schemas/NeuroML2/NeuroML_v2beta.xsd')
        if cell_name:
            self.neuroml_element.setAttribute('id', cell_name)
        #self.neuroml_element.setAttribute('lengthUnits','micron')
        self.out_doc.appendChild(self.neuroml_element)

        include_ellement = self.out_doc.createElement('include')
        include_ellement.setAttribute('href', 'LeakConductance.nml')
        self.neuroml_element.appendChild(include_ellement)
        #self.cells_element = self.out_doc.createElement('cells')
        #self.neuroml_element.appendChild(self.cells_element)
        self.isHasNeuriteGroup = False
        
    def addCell(self, cell):
        '''
        Add new NeuroMl cell to neuroMlWriter 
        '''
        seg_id = 2
        cell_ellement = self.out_doc.createElement('cell')
        cell_ellement.setAttribute('id', cell.name)
        self.neuroml_element.appendChild(cell_ellement)
        notes_ellement = self.out_doc.createElement('notes')
        ptext = self.out_doc.createTextNode(cell.note)
        notes_ellement.appendChild(ptext)
        cell_ellement.appendChild(notes_ellement)
        morphology_ellement = self.out_doc.createElement('morphology')
        morphology_ellement.setAttribute('id', 'morphology_' + cell.name)
        cell_ellement.appendChild(morphology_ellement)
        for segment in cell.segments:
            self.addSegment(morphology_ellement,segment)
        group_ellement = self.addSomaGroups(morphology_ellement)
        self.addAxonGroups(morphology_ellement, cell.segments)
        group_ellement2 = self.out_doc.createElement('segmentGroup')
        group_ellement2.setAttribute('id', 'dendrite_group')
        if cell.numOfDendrite != 0:
            num = 0
            num = cell.numOfDendrite - 1
            for i in range(num):
                self.addDendriteGroups(morphology_ellement,seg_id, cell.segments)
                include_ellement = self.out_doc.createElement('include')
                include_ellement.setAttribute('segmentGroup', 'Dendrite' + str(seg_id))
                group_ellement.appendChild(include_ellement)

                include_ellement = self.out_doc.createElement('include')
                include_ellement.setAttribute('segmentGroup', 'Dendrite' + str(seg_id))
                group_ellement2.appendChild(include_ellement)
                seg_id += 1
        if cell.numOfNeurite != 0:
            num = 0
            if cell.numOfDendrite != 0:
                num = cell.numOfNeurite - cell.numOfDendrite
            else:
                num = cell.numOfNeurite - 1
            for i in range(num):
                self.addNeuriteGroups(morphology_ellement,seg_id, cell.segments)
                include_ellement = self.out_doc.createElement('include')
                include_ellement.setAttribute('segmentGroup', 'Neurite' + str(seg_id))
                group_ellement.appendChild(include_ellement)
                include_ellement = self.out_doc.createElement('include')
                include_ellement.setAttribute('segmentGroup', 'Neurite' + str(seg_id))
                group_ellement2.appendChild(include_ellement)
                seg_id += 1
        if cell.numOfNeurite != 0 or cell.numOfDendrite != 0:
            morphology_ellement.appendChild(group_ellement2)
        
            
    def addSegment(self,morphology_ellement,segment):
        '''
        Add segments for cell
        '''
        segment_ellement = self.out_doc.createElement('segment')
        segment_ellement.setAttribute('id',str(segment.id))
        segment_ellement.setAttribute('name',segment.name)
        #segment_ellement.setAttribute('cable',str(segment.cable))
        morphology_ellement.appendChild(segment_ellement)
        if segment.parent != -1:
            parent_ellement = self.out_doc.createElement('parent')
            parent_ellement.setAttribute('segment',str(segment.parent))
            segment_ellement.appendChild(parent_ellement)
        if segment.position.proximal_point != None:
            proximal_ellement = self.out_doc.createElement('proximal')
            proximal_ellement.setAttribute('x',str(segment.position.proximal_point.x))
            proximal_ellement.setAttribute('y',str(segment.position.proximal_point.y))
            proximal_ellement.setAttribute('z',str(segment.position.proximal_point.z))
            proximal_ellement.setAttribute('diameter',str(segment.position.proximal_point.diameter))
            segment_ellement.appendChild(proximal_ellement)
        distal_ellement = self.out_doc.createElement('distal')
        distal_ellement.setAttribute('x',str(segment.position.distal_point.x))
        distal_ellement.setAttribute('y',str(segment.position.distal_point.y))
        distal_ellement.setAttribute('z',str(segment.position.distal_point.z))
        distal_ellement.setAttribute('diameter',str(segment.position.distal_point.diameter))
        segment_ellement.appendChild(distal_ellement)
        
        
    def addSomaGroups(self, morphology_ellement):
        '''
        Add Soma Groups 
        '''
        group_ellement = self.out_doc.createElement('segmentGroup')
        group_ellement.setAttribute('id', 'Soma')
        morphology_ellement.appendChild(group_ellement)
        member_ellement = self.out_doc.createElement('member')
        member_ellement.setAttribute('segment', '0')
        group_ellement.appendChild(member_ellement)
        morphology_ellement.appendChild(group_ellement)

        group_ellement = self.out_doc.createElement('segmentGroup')
        group_ellement.setAttribute('id', 'all')
        include_ellement = self.out_doc.createElement('include')
        include_ellement.setAttribute('segmentGroup', 'Soma')
        group_ellement.appendChild(include_ellement)
        include_ellement = self.out_doc.createElement('include')
        include_ellement.setAttribute('segmentGroup', 'Axon')
        group_ellement.appendChild(include_ellement)
        morphology_ellement.appendChild(group_ellement)

        group2_soma_group_ellement = self.out_doc.createElement('segmentGroup')
        group2_soma_group_ellement.setAttribute('id', 'soma_group')
        include_ellement = self.out_doc.createElement('include')
        include_ellement.setAttribute('segmentGroup', 'Soma')
        group2_soma_group_ellement.appendChild(include_ellement)
        morphology_ellement.appendChild(group2_soma_group_ellement)

        return group_ellement
        
    def addAxonGroups(self, morphology_ellement, segments):
        '''
        Add Axon Groups 
        '''
        cable_axon_group_ellement = self.out_doc.createElement('segmentGroup')
        cable_axon_group_ellement.setAttribute('id', 'Axon')
        for seg1 in segments:
            if re.search(axon_name, seg1.name):
                member_ellement = self.out_doc.createElement('member')
                member_ellement.setAttribute('segment', str(seg1.id))
                cable_axon_group_ellement.appendChild(member_ellement)
        morphology_ellement.appendChild(cable_axon_group_ellement)

        group_ellement = self.out_doc.createElement('segmentGroup')
        group_ellement.setAttribute('id', 'axon_group')
        include_ellement = self.out_doc.createElement('include')
        include_ellement.setAttribute('segmentGroup', 'Axon')
        group_ellement.appendChild(include_ellement)
        morphology_ellement.appendChild(group_ellement)

        
    def addNeuriteGroups(self, morphology_ellement, numOfGroup, segments):
        '''
        Add neurite Groups 
        '''
        group_ellement = self.out_doc.createElement('segmentGroup')
        group_ellement.setAttribute('id', 'Neurite' +str(numOfGroup))
        in_this_group = False
        for seg1 in segments:
            if hasattr(seg1, 'neurite_id'):
                neurite_id = seg1.neurite_id
                if neurite_id == numOfGroup:
                    member_ellement = self.out_doc.createElement('member')
                    member_ellement.setAttribute('segment', str(seg1.id))
                    group_ellement.appendChild(member_ellement)
        morphology_ellement.appendChild(group_ellement)

    def addDendriteGroups(self, morphology_ellement, numOfGroup, segments):
        '''
        Add dendrite Groups 
        '''
        group_ellement = self.out_doc.createElement('segmentGroup')
        group_ellement.setAttribute('id', 'Dendrite' +str(numOfGroup))
        in_this_group = False
        for seg1 in segments:
            if re.search(dendrite_name, seg1.name):
                mobj = re.search(dendrite_name + '_(\d+)', seg1.name)
                if mobj and mobj.group(1) != '0':
                    in_this_group = (int(mobj.group(1)) == numOfGroup)
                if in_this_group:
                    member_ellement = self.out_doc.createElement('member')
                    member_ellement.setAttribute('segment', str(seg1.id))
                    group_ellement.appendChild(member_ellement)
        morphology_ellement.appendChild(group_ellement)
        
    def printDocument(self):
        '''
        print document to output stream 
        to console
        '''
        print(self.out_doc.toprettyxml(indent="  "))
        
    def writeDocumentToFile(self):
        '''
        Write document to xml file
        '''
        try:
            f = open('./Output/' + self.docname + '.nml', 'w')
            f.write(self.out_doc.toprettyxml(indent="  "))
            f.close()
            print('NeuroMl was saved in file %s in folder Output' % self.docname + '.xml')
        except IOError as ex:
            print('NeuroMl wasn''t saved because : %s' % ex.strerror)
