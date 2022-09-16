#coding=utf-8
import os
import pandas as pd
import datetime
import time
import shutil
import subprocess


# ----------------------設定-------------------------
outputpath = '/media/alt41450/SAR/YLDescending/AllTest24' # 檔案路徑
runstep = '--steps  --start=geocode --end=geocodeoffsets' #執行步驟
area = [23.55,23.68,120.85,120.939]

# ---------------------------------------------------

runtopsApp = 'topsApp.py' #topsApp.py執行命令

#function     
from xml.etree.ElementTree import ElementTree,Element

def read_xml(in_path):
    
    tree = ElementTree()
    tree.parse(in_path)
    return tree

def write_xml(tree, out_path):
    
    tree.write(out_path, encoding="utf-8", xml_declaration=True)

def if_match(node, kv_map):
    
    for key in kv_map:
        if node.get(key) != kv_map.get(key):
            return False
    return True

# ----------------search -----------------
def find_nodes(tree, path):
    
    return tree.findall(path)

def get_node_by_keyvalue(nodelist, kv_map):
    
    result_nodes = []
    for node in nodelist:
        if if_match(node, kv_map):
            result_nodes.append(node)
    return result_nodes

# ---------------change ----------------------
def change_node_properties(nodelist, kv_map, is_delete=False):
    
    for node in nodelist:
        for key in kv_map:
            if is_delete:
                if key in node.attrib:
                    del node.attrib[key]
            else:
                node.set(key, kv_map.get(key))

def change_node_text(nodelist, text, is_add=False, is_delete=False):
    
    for node in nodelist:
        if is_add:
            node.text += text
        elif is_delete:
            node.text = ""
        else:
            node.text = text

def create_node(tag, property_map, content):
    
    element = Element(tag, property_map)
    element.text = content
    return element

def add_child_node(nodelist, element):
    
    for node in nodelist:
        node.append(element)


def del_node_by_tagkeyvalue(nodelist, tag, kv_map):
    
    for parent_node in nodelist:
        children = parent_node.getchildren()
        for child in children:
            if child.tag == tag and if_match(child, kv_map):
                parent_node.remove(child)



class cd:
    """Context manager for changing the current working directory"""
    def __init__(self, newPath):
        self.newPath = os.path.expanduser(newPath)

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)

dirpath = outputpath
listdir = os.listdir(dirpath)
print(listdir)
for i in listdir:
    tree = read_xml("%s/%s/topsApp.xml"%(outputpath,i))
        
    
    #nodes = find_nodes(tree, "component/property")                   
    #result_nodes = get_node_by_keyvalue(nodes, {"name": "geocode bounding box"})###
    
    text_nodes = get_node_by_keyvalue(find_nodes(tree, "component/property"), {"name": "geocode bounding box"}) ###
    change_node_text(text_nodes, "%s" %(area))
    write_xml(tree, "%s/%s/topsApp.xml" %(outputpath,i))
print(listdir)
for j in listdir:
    print(j)
    with cd("%s/%s" %(outputpath,j)):
        start_dire = r"%s" %(runtopsApp)
        r = os.system("%s topsApp.xml %s" %(start_dire,runstep))


#newfilename

twodate = []
for d in os.listdir(dirpath):
    
    twodate.append(d)

print(twodate)



   
#outputTIF

if os.path.exists('%s/OutputTIFnew'%(outputpath)):
    shutil.rmtree('%s/OutputTIFnew'%(outputpath))
os.mkdir('%s/OutputTIFnew' %(outputpath))
for x,y in zip(listdir, twodate):
    if os.path.exists('%s/%s/merged/filt_topophase.unw.geo.vrt'%(outputpath,x)):
        os.mkdir('%s/OutputTIFnew/%s' %(outputpath,y))
        with cd("%s/%s/merged" %(outputpath,x)):
            os.system("gdal_translate topophase.cor.geo -scale 0 1 0 255  -ot Byte  -b 2 %s.geo.cc.tif"%(y))
            #os.system("gdal_translate dense_offsets.bil.geo %s.denseoffset.tif"%(y))
            #os.system("gdal_translate filt_dense_offsets.bil.geo %s.filtdenseoffset.tif"%(y))
            #os.system("gdal_translate los.rdr.geo %s.los.rdr.tif"%(y))
            os.system('gdal_calc.py -A filt_topophase.unw.geo.vrt --A_band=2 --calc="A" --outfile=%s.geo.unw.tif --format=GTiff --NoDataValue=0 --overwrite'%(y))
            source_cc = r'%s/%s/merged/%s.geo.cc.tif' %(outputpath,x,y)
            source_unw = r'%s/%s/merged/%s.geo.unw.tif' %(outputpath,x,y)
            destination = r'%s/OutputTIFnew/%s'%(outputpath,y)
            if os.path.exists('%s/%s/merged/%s.geo.cc.tif'%(outputpath,x,y)):
                shutil.move(source_cc,destination)
            shutil.move(source_unw,destination)
            #source_unw2 = r'%s/%s/merged/%s.geo.unw.tif.aux.xml' %(outputpath,x,y)
            #source_unw3 = r'%s/%s/merged/%s.geo.unw.hdr' %(outputpath,x,y)
            #shutil.move(source_unw2,destination)
            #shutil.move(source_unw3,destination)
            #source_los = r'%s/%s/merged/%s.los.rdr.tif' %(outputpath,x,y)
            #shutil.move(source_los,destination)
            '''
            source_offset1 = r'%s/%s/merged/%s.denseoffset.tif' %(outputpath,x,y)
            source_offset2 = r'%s/%s/merged/%s.filtdenseoffset.tif' %(outputpath,x,y)
            shutil.move(source_offset1,destination)
            shutil.move(source_offset2,destination)
           
	    '''
#outputENU
if os.path.exists('%s/ENUfilenew'%(outputpath)):
    shutil.rmtree('%s/ENUfilenew'%(outputpath))
os.mkdir('%s/ENUfilenew' %(outputpath))
list1 = []
list1 = os.listdir(outputpath)####/Allfile
for x in list1:
    if os.path.exists('%s/%s/merged/los.rdr.geo'%(outputpath,x)):
        with cd("%s/%s/merged" %(outputpath,x)):
            os.system("imageMath.py --eval='sin(rad(a_0))*cos(rad(a_1+90));sin(rad(a_0)) * sin(rad(a_1+90));cos(rad(a_0))' --a=los.rdr.geo -t FLOAT -s BIL -o enu.rdr.geo")
            os.system("gdal_translate -of GMT -b 1 enu.rdr.geo Efile.geo.E.tif")
            os.system("gdal_translate -of GMT -b 2 enu.rdr.geo Nfile.geo.N.tif")
            os.system("gdal_translate -of GMT -b 3 enu.rdr.geo Ufile.geo.U.tif")
            destination = r'%s/ENUfilenew'%(outputpath)
            source_Efile = r'%s/%s/merged/Efile.geo.E.tif' %(outputpath,x)
            source_Nfile = r'%s/%s/merged/Nfile.geo.N.tif' %(outputpath,x)
            source_Ufile = r'%s/%s/merged/Ufile.geo.U.tif' %(outputpath,x)
            shutil.move(source_Efile,destination)
            shutil.move(source_Nfile,destination)
            shutil.move(source_Ufile,destination)
        break











