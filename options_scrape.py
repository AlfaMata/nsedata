from urllib.request import Request, urlopen
import pandas as pd
from lxml.html import fromstring

from datetime import datetime
from dateutil.relativedelta import relativedelta, TH
import time

import os.path

def cleanstr(string):
    
    try:
        floatnum = float(string.replace(',', ''))
    except:
        floatnum = 0
    return floatnum

def optionchain(exdate = '30JAN2020'):
    """
    Actual scraping done here
    """
    ocurl = "http://www1.nseindia.com/live_market/dynaContent/live_watch/option_chain/optionKeys.jsp?segmentLink=17&instrument=OPTIDX&symbol=NIFTY&date="+exdate
    headers = {'Accept' : '*/*',
               'Accept-Language' : 'en-US,en;q=0.5',
               'Host': 'www1.nseindia.com',
               'Referer': 'http://www1.nseindia.com/live_market/dynaContent/live_market.htm',
               'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1;WOW64;rv:54.0) Gecko Firefox/54',
               'X-Requested-With': 'XMLHttpRequest'}

    req = Request(ocurl, None, headers)
    response = urlopen(req)
    the_page = response.read() # works upto this; got the page in a string
    ptree = fromstring(the_page)
    tr_nodes = ptree.xpath('//table[@id="octable"]//tr')[1:]
    td_content = [[td.text_content().strip() for td in tr.xpath('td')] for tr in tr_nodes[1:]]
    td_content = [[cleanstr(string) for string in sublist] for sublist in td_content]
    return td_content[:-1]

def getLastThu(date = None):
    
    """
    Either keep the parameters empty which will get last thursday of current month
    else pass a date in the DDMMMYYYY format
    """
    if date is None:
        todayte = datetime.today()
    elif type(date) == str:
        todayte = datetime.strptime(date,"%d%b%Y")
    elif type(date) == datetime:
        todayte = date
    else:
        raise ValueError('badly formatted date input')
    
    cmon = todayte.month
    
    for i in range(1, 6):
        nthu = todayte + relativedelta(weekday=TH(i))
        if nthu.month != cmon:
            # since t is exceeded we need last one  which we can get by subtracting -2 since it is already a Thursday.
            nthu += relativedelta(weekday=TH(-2))
            break
    if nthu.day < todayte.day:
        timid = todayte + relativedelta(weekday=TH(i+1))
        nthu = getLastThu(timid)
        return nthu

    return nthu.strftime('%d%b%Y').upper()

def get_ocdata(exdate = '30JAN2020', start = 9*60*60, stop = (15*60+30)*60, 
               scrapeGap = 5, waitflag = True, nosleep = False, logfile="opt.log"):
    """
    start: Market open time/when the data scraping starts, in seconds elapsed from 12:00 AM
    stop:  Market closing time/when the data scraping stops, in seconds elapsed from 12:00 AM
    waitflag: whether to wait for the time specified in 'start' variable to occur, sleep till then
    nosleep: whether to scrape continually or give 1 sec pause between scrapes,
             will sleep if set to True if scraped before 1 sec interval
             if scrapes take more than 1 sec has no effect
             good to use if too much data traffic/network overloaded
    """

    currtime = time.localtime()
    dct = time.strftime('%d%b%Y', currtime).upper()
    datafile = 'nseOC' + dct + '.csv'
    csvfile = 'OCdata/' + datafile
    
    if not os.path.exists('OCdata/'):
        os.makedirs('OCdata/')
    
    a = ["OI", "changeOI", "volume", "IV", "LTP", "netChange"]
    b = ["bidQ", "bidP", "askP", "askQ"]
    hdr = [s + '.call' for s in a+b] + ["strike"] + [s + '.put' for s in b + list(reversed(a))] + ["timestamp"]
    
    if not os.path.isfile(csvfile):
        dfcolnames = pd.DataFrame(hdr)
        dfcolnames = dfcolnames.T        
        dfcolnames.to_csv(csvfile, index=False, mode='a', header=False)

    ptime = datetime.now()

    if waitflag == True:
        secs = (ptime.hour*60*60 + ptime.minute*60 + ptime.second)
        if secs < start:
            time.sleep(start - secs)

    while True:
        if (ptime.hour*60*60 + ptime.minute*60 + ptime.second) > stop:
            break
        else:
            try:
                ptime = datetime.now()
                scrapedata = pd.DataFrame(optionchain(exdate))
                scrapedata = scrapedata.iloc[:, 1:22]
                scrapedata['timestamp'] = ptime
                scrapedata.to_csv(csvfile, index=False, mode='a', header=False)
                
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


get_ocdata(exdate = getLastThu(), stop = (15*60+45)*60, scrapeGap = 5, nosleep = False, logfile="opt.log")
