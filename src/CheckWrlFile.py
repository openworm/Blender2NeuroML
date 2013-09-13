'''
Created on 10.05.2011

@author: Sergey Khayrulin
'''
import xlrd
import zipfile
import xml.parsers.expat
import xml.dom.minidom

xlsFileName = './Data/NeuronConnect.xls'
wrlFileName = './Data/Virtual_Worm_March_2011.wrl'
wrlFileName_test = './Data/test_neuron.wrl'
odsFileName = './Data/302.ods'
num = ['01','02','03','04','05','06','07','08','09']
neuroNameFromExcel = []
neuroNameFromOds = []
checkedNeuronWithExcel = []
checkedNeuronWithOds = []

def CheckStrToConvert(num):
    '''
    Check num if it int 
    '''
    try:
        int(num)
        return True
    except (ValueError, IndexError):
        return False

def numberLowThatTen(s=""):
    '''
    Check string s if it contains a number
    if this number less that 10 it replaces 
    from this formant 01 to 1
    '''
    if(len(s)>2):
        num = s[len(s)-2] + s[len(s)-1]
        if CheckStrToConvert(num): 
            if int(num)<10:
                return s[:len(s) - 2] + str(int(num))
            else:
                return s   
        else:
            return s 
    return s 
        

def readDataFromOdsFile(fileName):
    '''
    Read data from Ods file 
    '''
    ziparchive = zipfile.ZipFile(fileName, "r")
    xmldata = ziparchive.read("content.xml")
    ziparchive.close()
    xmldoc = xml.dom.minidom.parseString(xmldata)
    for node in xmldoc.getElementsByTagName('table:table-row')[1:]:
        if len(node.childNodes) > 2 :
            neuroName = node.childNodes[1].getElementsByTagName("text:p")[0].childNodes[0].toxml()
            if not neuroNameFromOds.__contains__(neuroName):
                neuroNameFromOds.append(neuroName.strip('*'))
    
def readFromXlsFile(fileName):
    '''
    Read data from Xls file uses a xlrd library 
    '''
    wb = xlrd.open_workbook(fileName)
    sh = wb.sheet_by_name(u'NeuronConnect.csv')
    for rownum in range(sh.nrows):
        if(rownum != 0):
            if not(neuroNameFromExcel.__contains__(sh.row_values(rownum)[0].upper())):
                if(sh.row_values(rownum)[0] != 'NMJ'):
                    neuroNameFromExcel.append(sh.row_values(rownum)[0].upper())
            if not(neuroNameFromExcel.__contains__(sh.row_values(rownum)[1].upper())):
                if(sh.row_values(rownum)[1] != 'NMJ'):
                    neuroNameFromExcel.append(sh.row_values(rownum)[1].upper())
    checkNeuroCollection()
    
def checkNeuroCollection():
    '''
    Check collection of neurons name if name has a number in name
    '''
    for i in range(len(neuroNameFromExcel)):
        neuroNameFromExcel[i] = numberLowThatTen(neuroNameFromExcel[i])
    
def readFormWrlFile(fileName):
    '''
    Read data from WrlFile
    '''
    wrlFile =open(fileName,'r')
    for line in wrlFile:
        s = str(line)
        if(s.startswith('\tDEF')):
            if(neuroNameFromExcel.__contains__(s[5:].strip('\n'))):
                checkedNeuronWithExcel.append(s[5:].strip('\n'))
            if(neuroNameFromOds.__contains__(s[5:].strip('\n'))):
                checkedNeuronWithOds.append(s[5:].strip('\n')) 
                
    wrlFile.close()  

def readFormWrlFile_new(fileName):
    '''
    Read data from WrlFile format 2.0
    '''
    wrlFile =open(fileName,'r')
    for line in wrlFile:
        s = str(line)
        if(s.startswith('DEF ')):
            neuronName = s[4:s[4:].index(' ')+4]
            if s == 'DEF SAADL Shape {\n':
                pass
            if(neuroNameFromExcel.__contains__(neuronName)):
                checkedNeuronWithExcel.append(neuronName)
            if(neuroNameFromOds.__contains__(neuronName)):
                checkedNeuronWithOds.append(neuronName) 
                
    wrlFile.close()
    
if __name__ == '__main__':
    print '===================== Program Start ====================='
    
    readDataFromOdsFile(odsFileName)
    print 'In Ods File(' + odsFileName + ') Was find:' + str(len(neuroNameFromOds)) + ' Neuron name'
    readFromXlsFile(xlsFileName)
    print 'In Excel File(' + xlsFileName + ') Was find:' + str(len(neuroNameFromExcel)) + ' Neuron name'
    
    readFormWrlFile_new(wrlFileName_test)
    print '===================== Comparing with Excel File ' + xlsFileName + '======================='
    for neuron in neuroNameFromExcel:
        if not checkedNeuronWithExcel.__contains__(neuron):
            print 'Neuron with name ' +neuron+ ' was find in ' + xlsFileName + ' file, but was not find in ' + wrlFileName + 'file'
    print '===================== Comparing with Ods File ' + odsFileName + '========================='
    for neuron in neuroNameFromOds:
        if not checkedNeuronWithOds.__contains__(neuron):
            print 'Neuron with name ' +neuron+ ' was find in ' + odsFileName + ' file, but was not find in ' + wrlFileName + ' file'
    
    print '===================== Exit ================================'
    print list(neuroNameFromOds)
    print list(checkedNeuronWithOds)