#coding=utf-8
import os
import pandas as pd
import datetime
import time
import shutil
import subprocess


# ----------------------設定-------------------------
SLCdatapath = '/media/alt41450/SAR/Descending'  #影像資料路徑
runstep = '--steps  --start=startup --end=geocodeoffsets' #執行步驟
deletfile = 0 #是否刪除merged以外檔案(0:NO/1:YES)
swathnumber = 2
# ---------------------------------------------------



#Initialization
runtopsApp = 'topsApp.py' #topsApp.py執行命令
ASFdatapath = SLCdatapath
Dem = 1 #1:copyDEM
swathnumber = str(swathnumber)
outputpath = os.path.dirname(os.path.abspath(__file__)) #設定檔及放置成果路徑
print(os.path.dirname(os.path.abspath(__file__)))



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

###讀檔案
dirpath = ASFdatapath
list = []
list = os.listdir(dirpath)

date = []
for i in range(len(os.listdir(dirpath))):
    filename = os.listdir(dirpath)[i].split('_')
    date.append(filename[6][0:8])


###做成表格
content = {
    "filename": list,
    "date": date,
    
}
 
df1 = pd.DataFrame(content)
df = df1.sort_values(["date"], ascending=True).reset_index(drop=True)
#print(df)

datecount = []
for i in range(len(df.index)):
    d1a,d1b,d1c = time.strptime(df["date"][0], "%Y%m%d")[:3]
    d2a,d2b,d2c = time.strptime(df["date"][i], "%Y%m%d")[:3]
    d1 = datetime.datetime(d1a,d1b,d1c)   # 第一日期
    d2 = datetime.datetime(d2a,d2b,d2c)   # 第二日期
    interval = d2 - d1                   # 日期差距
    datecount.append(interval.days) 
df.insert(2, column="datecount", value=datecount)
print(df)


###時間基線篩選
day1 = int(input("時間基線區間從"))
day2 = int(input("到"))

timeselect = []
for i in range (len(df.index)):
    for j in range(i,len(df.index)):
        dayrange = df["datecount"][j]-df["datecount"][i]
        
        if dayrange<=day2 and dayrange>=day1:
            timeselect.append((df["filename"][i],df["filename"][j]))

date2 = []
for d in timeselect:
    newfilename1 = d[0].split('_')
    newfilename2 = d[1].split('_')
    date2.append("%s_%s" %(newfilename1[6][0:8],newfilename2[6][0:8]))
  
print(timeselect)

print(date2)
print('count:',len(date2))
base1 = int(input("空間基線區間從"))
base2 = int(input("到"))

###產生設定檔
if os.path.exists('%s/AllTest'%(outputpath)):
    shutil.rmtree('%s/AllTest'%(outputpath))
os.mkdir('%s/AllTest' %(outputpath))

for i,j in zip(range(len(date2)),date2):
    a = j
    os.mkdir('%s/AllTest/%s' %(outputpath,a) )
    if (Dem):
        shutil.copyfile('%s/reprj.dem.wgs84'%(outputpath), '%s/AllTest/%s/reprj.dem.wgs84' %(outputpath,a) )
        shutil.copyfile('%s/reprj.dem.wgs84.vrt' %(outputpath), '%s/AllTest/%s/reprj.dem.wgs84.vrt' %(outputpath,a) )
        shutil.copyfile('%s/reprj.dem.wgs84.xml' %(outputpath), '%s/AllTest/%s/reprj.dem.wgs84.xml' %(outputpath,a))
    #secondary
    tree = read_xml("%s/secondary.xml"%(outputpath))
    
    nodes = find_nodes(tree, "property")                   
    result_nodes = get_node_by_keyvalue(nodes, {"name": "safe"})
    
    text_nodes = get_node_by_keyvalue(find_nodes(tree, "property"), {"name": "safe"}) 
    change_node_text(text_nodes, "%s/%s" %(ASFdatapath,timeselect[i][0]))
    
    write_xml(tree, "%s/AllTest/%s/secondary.xml" %(outputpath,a))
    #reference
    tree2 = read_xml("%s/reference.xml"%(outputpath))
    
    nodes2 = find_nodes(tree2, "property")                   
    result_nodes = get_node_by_keyvalue(nodes2, {"name": "safe"})
    
    text_nodes2 = get_node_by_keyvalue(find_nodes(tree2, "property"), {"name": "safe"}) 
    change_node_text(text_nodes2, "%s/%s" %(ASFdatapath,timeselect[i][1]))
    
    write_xml(tree2, "%s/AllTest/%s/reference.xml" %(outputpath,a))
    #topsApp
    tree3 = read_xml("%s/topsApp.xml"%(outputpath))
    write_xml(tree3, "%s/AllTest/%s/topsApp.xml" %(outputpath,a))
    
    
###空間基線計算
class cd:
    """Context manager for changing the current working directory"""
    def __init__(self, newPath):
        self.newPath = os.path.expanduser(newPath)

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)
import subprocess # just to call an arbitrary command e.g. 'ls'
error = []
for i in date2:
    a = i
    with cd("%s/AllTest/%s" %(outputpath,a)):
        
        
        start_dire = r"%s"%(runtopsApp)
        os.system("%s topsApp.xml --steps  --start=startup --end=computeBaselines" %(start_dire))
        
        
        


#空間基線(讀檔案)
Baselines = []
for i in range(0,int(len(date2)/10+1)):
    a = date2[i]
    with cd("%s/AllTest/%s" %(outputpath,a)):
        path = 'text.txt'
        f = open('isce.log','r')
        lines = f.readlines()
        for k in range(len(lines)):
            name=lines[k].split('=')           
            if name[0]=='baseline.IW-%s Bpar at midrange for first common burst ' %(swathnumber[0]):               
                log_line = k
                print('line=',log_line,a,lines[k])              
        f.close()
print('line=',log_line)

for i in date2:
    d = i
    with cd("%s/AllTest/%s" %(outputpath,d)):
        path = 'text.txt'
        f = open('isce.log','r')
        lines = f.readlines()
        if len(lines)>log_line:
            a = lines[log_line].split('=')
            #print(a)
            Baselines.append(float(a[1][1:-1]))
        else:
            
            Baselines.append(base2+10000)
            print(d,':error')
        f.close()
print(Baselines)

#空間基線篩選(做成表格)
testFile = []
for i in date2:
    a = i###
    testFile.append(a)

content = {
    "testFile": testFile,
    "filename": timeselect,
    "Baselines": Baselines,
    
}

df22 = pd.DataFrame(content)
df2 = df22.reset_index(drop=True)   
print(df2)       

#空間基線(篩選)

baselinedrop = []

for i in range (len(df2.index)):
    if df2["Baselines"][i]>base2 or df2["Baselines"][i]<base1:
        baselinedrop.append(df2["testFile"][i])
        df2drop = df2.drop([i], axis=0)
print('刪除:',baselinedrop)
df2drop = df2
baselineselect = []
for i in range (len(df2.index)):
    if df2["Baselines"][i]<=base2 and df2["Baselines"][i]>=base1:
        baselineselect.append(df2["testFile"][i])
print('待執行:',baselineselect)


#最後計算
#刪除不需要的test/file

for i in baselinedrop:
    if os.path.exists("%s/AllTest/%s" %(outputpath,i)) :
        shutil.rmtree("%s/AllTest/%s" %(outputpath,i))
        
for j in baselineselect:
    with cd("%s/AllTest/%s" %(outputpath,j)):
        start_dire = r"%s" %(runtopsApp)
        r = os.system("%s topsApp.xml %s" %(start_dire,runstep))
        #print(r)
        error.append(r)
        if deletfile:
            os.system('rm -rf %s/AllTest/%s/reprj.dem.wgs84'%(outputpath,j))
            if os.path.exists('%s/AllTest/%s/fine_coreg'%(outputpath,j)):
                os.system('rm -rf %s/AllTest/%s/fine_coreg'%(outputpath,j))
                os.system('rm -rf %s/AllTest/%s/fine_interferogram'%(outputpath,j))
                os.system('rm -rf %s/AllTest/%s/fine_offsets'%(outputpath,j))
                os.system('rm -rf %s/AllTest/%s/geom_reference'%(outputpath,j))
                
                os.system('rm -rf %s/AllTest/%s/merged/secondary.slc.full'%(outputpath,j))
                os.system('rm -rf %s/AllTest/%s/merged/reference.slc.full'%(outputpath,j))      
            
df2new = df2drop.reset_index(drop=True)
print(df2new)


#error
content = {
    "testFile": baselineselect,
    "Error": error,
    
}

df32 = pd.DataFrame(content)
df3 = df32.sort_values(["testFile"], ascending=True).reset_index(drop=True)      
print(df3)        


#newfilename

twodate = []
for d in df2new["filename"]:
    newfilename1 = d[0].split('_')
    newfilename2 = d[1].split('_')
    twodate.append("%s_%s" %(newfilename1[6][0:8],newfilename2[6][0:8]))

print(twodate)
df2new.insert(2, column="newfilename", value=twodate)
#df2new.insert(4, column="error", value=error)
df2new = df2new.drop("filename", axis=1)
print(df2new)


   
#outputTIF

if os.path.exists('%s/OutputTIF'%(outputpath)):
    shutil.rmtree('%s/OutputTIF'%(outputpath))
os.mkdir('%s/OutputTIF' %(outputpath))
for x,y in zip(df2new["testFile"], df2new["newfilename"]):
    if os.path.exists('%s/AllTest/%s/merged/filt_topophase.unw.geo.vrt'%(outputpath,x)):
        os.mkdir('%s/OutputTIF/%s' %(outputpath,y))
        with cd("%s/AllTest/%s/merged" %(outputpath,x)):
            
            #產製TIF

            os.system("gdal_translate topophase.cor.geo -scale 0 1 0 255  -ot Byte  -b 2 %s.geo.cc.tif"%(y))
            os.system("gdal_translate dense_offsets.bil.geo %s.denseoffset.tif"%(y))
            os.system("gdal_translate filt_dense_offsets.bil.geo %s.filtdenseoffset.tif"%(y))
            os.system("gdal_translate los.rdr.geo %s.los.rdr.tif"%(y))
            os.system('gdal_calc.py -A filt_topophase.unw.geo.vrt --A_band=2 --calc="A" --outfile=%s.geo.unw.tif --format=GTiff --NoDataValue=0 --overwrite'%(y))
            source_cc = r'%s/AllTest/%s/merged/%s.geo.cc.tif' %(outputpath,x,y)
            source_unw = r'%s/AllTest/%s/merged/%s.geo.unw.tif' %(outputpath,x,y)
            destination = r'%s/OutputTIF/%s'%(outputpath,y)
            
            #移動TIF

            if os.path.exists('%s/AllTest/%s/merged/%s.geo.cc.tif'%(outputpath,x,y)):
                shutil.move(source_cc,destination)
            shutil.move(source_unw,destination)
            #source_unw2 = r'%s/AllTest/%s/merged/%s.geo.unw.tif.aux.xml' %(outputpath,x,y)
            #source_unw3 = r'%s/AllTest/%s/merged/%s.geo.unw.hdr' %(outputpath,x,y)
            #shutil.move(source_unw2,destination)
            #shutil.move(source_unw3,destination)
            source_offset1 = r'%s/AllTest/%s/merged/%s.denseoffset.tif' %(outputpath,x,y)
            source_offset2 = r'%s/AllTest/%s/merged/%s.filtdenseoffset.tif' %(outputpath,x,y)
            shutil.move(source_offset1,destination)
            shutil.move(source_offset2,destination)
            source_los = r'%s/AllTest/%s/merged/%s.los.rdr.tif' %(outputpath,x,y)
            shutil.move(source_los,destination)

print(df2new)  



#outputENU
if os.path.exists('%s/ENUfile'%(outputpath)):
    shutil.rmtree('%s/ENUfile'%(outputpath))
os.mkdir('%s/ENUfile' %(outputpath))
list1 = []
list1 = os.listdir('%s/AllTest'%(outputpath))####
for x in list1:
    if os.path.exists('%s/%s/merged/los.rdr.geo'%(outputpath,x)):
        with cd("%s/%s/merged" %(outputpath,x)):
            os.system("imageMath.py --eval='sin(rad(a_0))*cos(rad(a_1+90));sin(rad(a_0)) * sin(rad(a_1+90));cos(rad(a_0))' --a=los.rdr.geo -t FLOAT -s BIL -o enu.rdr.geo")
            os.system("gdal_translate -of GMT -b 1 enu.rdr.geo Efile.geo.E.tif")
            os.system("gdal_translate -of GMT -b 2 enu.rdr.geo Nfile.geo.N.tif")
            os.system("gdal_translate -of GMT -b 3 enu.rdr.geo Ufile.geo.U.tif")
            destination = r'%s/ENUfile'%(outputpath)
            source_Efile = r'%s/%s/merged/Efile.geo.E.tif' %(outputpath,x)
            source_Nfile = r'%s/%s/merged/Nfile.geo.N.tif' %(outputpath,x)
            source_Ufile = r'%s/%s/merged/Ufile.geo.U.tif' %(outputpath,x)
            shutil.move(source_Efile,destination)
            shutil.move(source_Nfile,destination)
            shutil.move(source_Ufile,destination)

#delet file
if deletfile:
    if os.path.exists('%s/Allfile'%(outputpath)):
        shutil.rmtree('%s/Allfile'%(outputpath))
    os.mkdir('%s/Allfile' %(outputpath))
    for x,y in zip(df2new["testFile"], df2new["newfilename"]):
        if os.path.exists('%s/AllTest/%s/merged'%(outputpath,x)):
            os.mkdir('%s/Allfile/%s' %(outputpath,y))
            with cd("%s/AllTest/%s" %(outputpath,x)):
                source_merged = r'%s/AllTest/%s/merged' %(outputpath,x)
                destination = r'%s/Allfile/%s'%(outputpath,y)
                shutil.move(source_merged,destination)
        if os.path.exists('%s/Allfile/%s/merged/filt_topophase.unw.geo.vrt'%(outputpath,x)):
            shutil.rmtree('%s/AllTest/%s'%(outputpath,x))


        break


        
print(df3)












