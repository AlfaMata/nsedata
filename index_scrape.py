# import requests
from urllib.request import Request, urlopen
import pandas as pd
import json

from datetime import datetime
import time
import os.path

# from time import localtime, strftime
# strftime("%Y-%m-%d %H:%M:%S", localtime())

def remcomma(row):
    return row.str.replace(',', '')

def getIndexData():
    
    idxurl = 'https://www1.nseindia.com/live_market/dynaContent/live_watch/stock_watch/liveIndexWatchData.json'
    headers = {'Accept' : '	text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
               'Accept-Language' : 'en-US,en;q=0.5',
               'Host': 'www1.nseindia.com',
               'Referer': 'https://www1.nseindia.com/live_market/dynaContent/live_watch/live_index_watch.htm',
               'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1;WOW64;rv:54.0) Gecko Firefox/54',
               'X-Requested-With': 'XMLHttpRequest'
               }
    
    req = Request(idxurl, None, headers)
    resp = urlopen(req)
    sdata = resp.read().decode('utf-8')
    jdata = json.loads(sdata)
    # r = requests.get(idxurl, headers=headers)
    # jdata = json.loads(r.content)
    pdf = pd.io.json.json_normalize(jdata['data'])
    icols = ['indexName','indexOrder','last','high','low','open','percChange','previousClose','timeVal','yearHigh','yearLow']
    
    idata = pdf[icols]
    idata = idata.apply(remcomma, axis=1)
    ptime = datetime.now()
    idata['timestamp'] = ptime
    
    return idata

def getidxdataIO(start = (9*60)*60, stop = (15*60+30)*60, waitflag = True, 
               scrapeGap = 5, nosleep = False, writegap = 10, logfile="idx.log"):
    
    
    pd.options.mode.chained_assignment = None
    currtime = time.localtime()
    dct = time.strftime('%d%b%Y', currtime).upper()
    datafile = 'nseIdx' + dct + '.csv'
    csvfile = 'Index/' + datafile
    
    if not os.path.exists('Index/'):
        os.makedirs('Index/')
    
    if not os.path.isfile(csvfile):
        dfheaders = pd.DataFrame(columns=['indexName', 'indexOrder', 'last', 
        'high', 'low', 'open', 'percChange', 'previousClose', 
        'timeVal', 'yearHigh', 'yearLow', 'timestamp'])
        dfheaders.to_csv(csvfile, index=False, mode='a', header=True)
    else:
        pass # already exists
    
    ptime = datetime.now()
    
    if waitflag == True:
        secs = (ptime.hour*60*60 + ptime.minute*60 + ptime.second)
        if secs < start:
            time.sleep(start - secs)
    
    #writetime = datetime(2016,1,1,0,0,0)
    nseidx = pd.DataFrame()
    #writeflag = 0
    
    while True:
        if (ptime.hour*60*60 + ptime.minute*60 + ptime.second) > stop:
            break
        else:
            try:
                ptime = datetime.now()
                nseidx = getIndexData()
                nseidx.to_csv(csvfile, index=False, mode='a', header=False)
                
                if not nosleep:
                    end = datetime.now()
                    tdiff = end-ptime
                    
                    tslip = scrapeGap - (tdiff.seconds + tdiff.microseconds*1.0/10**6)
                    if tslip > 0:
                        time.sleep(tslip)
                
            except Exception as e:
                with open("idx.log", "a") as lf:
                    lf.write("Error at {0} \t {1}\n".format(str(ptime), str(e)))
                time.sleep(scrapeGap)
                continue
    
    return 0
	 


getidxdataIO(stop = (15*60+45)*60, scrapeGap = 5, nosleep = False, logfile="idx.log")
