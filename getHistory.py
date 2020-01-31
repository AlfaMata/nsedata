# -*- coding: utf-8 -*-
"""
Created on Wed Apr 25 10:57:49 2018

@author: itithilien
"""

from datetime import datetime as ldt
from dateutil import rrule
import requests
from zipfile import ZipFile
from shutil import move


def getNSEfiles(fdate, iFlag = "FO"):

#==============================================================================
#     cmsamp = 'https://www1.nseindia.com/content/historical/EQUITIES/2020/JAN/cm14JAN2020bhav.csv.zip'
#     fosamp = 'https://www1.nseindia.com/content/historical/DERIVATIVES/2020/JAN/fo15JAN2020bhav.csv.zip'
#     dqsamp = 'http://www1.nseindia.com/archives/equities/mto/MTO_09092015.DAT'
#==============================================================================
    
    if iFlag == "FO":
        base = 'http://www1.nseindia.com/content/historical/DERIVATIVES/'
        ftail = 'bhav.csv.zip'
        dirbase = 'D:\\dataset\\nse' + 'FO\\'
    elif iFlag == "CM":
        base = 'http://www1.nseindia.com/content/historical/EQUITIES/'
        ftail = 'bhav.csv.zip'
        dirbase = 'D:\\dataset\\nse' + 'CM\\'
    elif iFlag == "DQ":
        base = 'http://www1.nseindia.com/archives/equities/mto/MTO_'
        ftail = '.DAT'
        dirbase = 'D:\\dataset\\nse' + 'DQ\\'
    else:
        raise ValueError('Instrument code should be either "FO" or "CM" or "DQ"')
    
    
    ey = fdate.strftime("%Y")
    ed = fdate.strftime("%d")
    em = fdate.strftime("%b").upper()
    emn = fdate.strftime("%m")
    
    if iFlag == "FO":
        furl = base + ey + '/' + em + '/' + 'fo' + ed + em + ey + ftail
        fname ='tf.zip' 
    elif iFlag == "EQ":
        furl = base + ey + '/' + em + '/' + 'cm' + ed + em + ey + ftail
        fname ='tf.zip'
    else:
        furl = base + ed + emn + ey + ftail
        fname ='MTO_' + ed + emn + ey + ftail

    
    
    with open(fname, 'wb') as stream:
        xxf = requests.get(furl)
        if xxf.status_code == 200:
            stream.write(xxf.content)
        else:
            return 1
    
    targetdir = dirbase + ey
    
    if iFlag == ("FO" or "CM"):
        with ZipFile(fname,"r") as zip_ref:
            zip_ref.extractall(targetdir)
    else:
        move(fname, targetdir)

    #print("out")
    return 0



start = ldt(2016, 1, 1)
end = ldt(2018, 4, 24)
rule = rrule.rrule(dtstart=start, freq=rrule.DAILY,
    byweekday=[rrule.MO, rrule.TU, rrule.WE, rrule.TH, rrule.FR]
)

daites = rule.between(start, end, inc=True)


for d in daites:
    #getNSEfiles(d)
    #getNSEfiles(d, "CM")
    getNSEfiles(d, "DQ")


start = ldt(1994, 1, 1)
end = ldt(2018, 4, 25)


def getYCfiles(fdate):
    
    # zcsamp = 'https://www1.nseindia.com/archives/debt/zcyc/zcyc_13052013.zip'
    
    base = 'https://www1.nseindia.com/archives/debt/zcyc/zcyc_'
    ftail = '.zip'
    dirbase = 'D:\\dataset\\nse' + 'YC\\'
    
    ey = fdate.strftime("%Y")
    ed = fdate.strftime("%d")
    emn = fdate.strftime("%m")
    
    furl = base + ed + emn + ey + ftail
    fname ='yc.zip'
    
    with open(fname, 'wb') as stream:
            xxf = requests.get(furl)
            if xxf.status_code == 200:
                stream.write(xxf.content)
            else:
                return 1
    
    targetdir = dirbase + ey
    with ZipFile(fname,"r") as zip_ref:
        zip_ref.extractall(targetdir)
    
    return 0

for d in daites:
    getYCfiles(d)