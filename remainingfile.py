#coding=utf-8
import os
import pandas as pd
import datetime
import time
import shutil
import subprocess


# ----------------------設定-------------------------
outputpath = '/media/alt41450/SAR/YLDescending/AllTest12-23' # 檔案路徑
runstep = '--steps  --start=startup --end=geocodeoffsets' #執行步驟


# ---------------------------------------------------

runtopsApp = 'topsApp.py' #topsApp.py執行命令



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

remainingdate = []
for j in listdir:
    if not os.path.exists('%s/%s/merged/filt_topophase.unw.geo.vrt'%(outputpath,j)):
        remainingdate.append(j)
        
        with cd("%s/%s" %(outputpath,j)):
            start_dire = r"%s" %(runtopsApp)
            r = os.system("%s topsApp.xml %s" %(start_dire,runstep))
           
print(remainingdate)