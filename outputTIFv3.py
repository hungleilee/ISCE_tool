#coding=utf-8
import os
import pandas as pd
import datetime
import time
import shutil
import subprocess

# -----------設定--------------

outputpath = '/media/alt41450/SAR/tw/AllTest' #放置成果路徑
 
# -------------------------

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


#newfilename

twodate = []
for d in os.listdir(dirpath):
    
    twodate.append(d)

print(twodate)




#outputTIF
f=0###
if os.path.exists('%s/OutputTIF'%(outputpath)):
    shutil.rmtree('%s/OutputTIF'%(outputpath))
os.mkdir('%s/OutputTIF' %(outputpath))
for x,y in zip(listdir, twodate):
    if os.path.exists('%s/%s/merged/topophase.cor.geo'%(outputpath,x)):
        os.mkdir('%s/OutputTIF/%s' %(outputpath,y))
        f=f+1###
        with cd("%s/%s/merged" %(outputpath,x)):
            os.system("gdal_translate topophase.cor.geo -b 2 %s.geo.cc.tif"%(y))#-scale 0 1 0 255  -ot Byte  -b 2 
            #os.system("gdal_translate dense_offsets.bil.geo %s.denseoffset.tif"%(y))
            #os.system("gdal_translate filt_dense_offsets.bil.geo %s.filtdenseoffset.tif"%(y))
            #os.system("gdal_translate los.rdr.geo %s.los.rdr.tif"%(y))
            #os.system('gdal_calc.py --type Float32 -A filt_topophase.flat.geo.vrt --calc="numpy.angle(A)" --outfile=%s.filt_topophase.flat.geo.tif --NoDataValue=0.0 --overwrite'%(y))
            
            #os.system('gdal_calc.py -A filt_topophase.unw.geo.vrt --A_band=2 --calc="A" --outfile=%s.geo.unw.tif --format=GTiff --NoDataValue=0 --overwrite'%(y))
            source_cc = r'%s/%s/merged/%s.geo.cc.tif' %(outputpath,x,y)
            #source_topo = r'%s/%s/merged/%s.filt_topophase.flat.tif' %(outputpath,x,y)
            #source_unw = r'%s/%s/merged/%s.geo.unw.tif' %(outputpath,x,y)
            destination = r'%s/OutputTIF/%s'%(outputpath,y)
            if os.path.exists('%s/%s/merged/%s.geo.cc.tif'%(outputpath,x,y)):
                shutil.move(source_cc,destination)
            #shutil.move(source_unw,destination)
            #shutil.move(source_topo,destination)
            #source_unw2 = r'%s/%s/merged/%s.geo.unw.tif.aux.xml' %(outputpath,x,y)
            #source_unw3 = r'%s/%s/merged/%s.geo.unw.hdr' %(outputpath,x,y)
            #shutil.move(source_unw2,destination)
            #shutil.move(source_unw3,destination)
            #source_los = r'%s/%s/merged/%s.los.rdr.tif' %(outputpath,x,y)
            #shutil.move(source_los,destination)
            
            
            #source_offset1 = r'%s/%s/merged/%s.denseoffset.tif' %(outputpath,x,y)
            #source_offset2 = r'%s/%s/merged/%s.filtdenseoffset.tif' %(outputpath,x,y)
            #shutil.move(source_offset1,destination)
            #shutil.move(source_offset2,destination)
print(f)   ###        
	    
'''
#outputENU
if os.path.exists('%s/ENUfile'%(outputpath)):
    shutil.rmtree('%s/ENUfile'%(outputpath))
os.mkdir('%s/ENUfile' %(outputpath))
list1 = []
list1 = os.listdir(outputpath)####/Allfile
for x in list1:
    if os.path.exists('%s/%s/merged/los.rdr.geo'%(outputpath,x)):
        with cd("%s/%s/merged" %(outputpath,x)):
            os.system("imageMath.py --eval='sin(rad(a_0))*cos(rad(a_1+90));sin(rad(a_0)) * sin(rad(a_1+90));cos(rad(a_0))' --a=los.rdr.geo -t FLOAT -s BIL -o enu.rdr.geo")
            os.system("gdal_translate -of GTiff -b 1 enu.rdr.geo Efile.geo.E.tif")
            os.system("gdal_translate -of GTiff -b 2 enu.rdr.geo Nfile.geo.N.tif")
            os.system("gdal_translate -of GTiff -b 3 enu.rdr.geo Ufile.geo.U.tif")
            destination = r'%s/ENUfile'%(outputpath)
            source_Efile = r'%s/%s/merged/Efile.geo.E.tif' %(outputpath,x)
            source_Nfile = r'%s/%s/merged/Nfile.geo.N.tif' %(outputpath,x)
            source_Ufile = r'%s/%s/merged/Ufile.geo.U.tif' %(outputpath,x)
            shutil.move(source_Efile,destination)
            shutil.move(source_Nfile,destination)
            shutil.move(source_Ufile,destination)
    if os.path.exists('%s/ENUfile/Ufile.geo.U.tif'%(outputpath)):
        break
'''


 












