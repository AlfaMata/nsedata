# -*- coding: utf-8 -*-
"""
Created on Thu Apr 04 09:21:19 2019

@author: itithilien
"""

import pandas as pd
# from datetime import datetime
from IVgreeks import impVol, BSM, greeksAll
import seaborn as sns
import matplotlib.pyplot as plt
# from ggplot import *


mdata = {"DateTime":"02-Apr-19 10:45:00","MIBOR":6.25,"Tenor":"O/N"}

cd nsedata
df = pd.read_csv("OCdata/nseOC03APR2019.csv")
df.columns # column names
print sf.head(5)


df = df[(df.strike == 11500)]
sf = df.iloc[:,[2,3,4,10,16,17,18,21]]
sf.columns


sf = sf.set_index(['strike','timestamp'])
sf.columns = pd.MultiIndex.from_tuples([col.split('.', 1) for col in sf.columns])
sf = sf.stack(level=1).reset_index()
sf.rename(columns={'level_2':'optionType'}, inplace=True)
sf.rename(columns={'LTP':'OptPrice'}, inplace=True)


sf['timestamp'] = pd.to_datetime(sf['timestamp'])

# =============================================================================
# Assumption values and description
 
sf["spot"] = 11713.20 # need to be updated with concurrent spot, here it is 1 day closing price
sf["riskFree"] = 6.25/100 # Overnight Mibor rate, taken from FIMMDA website
sf["divYield"] = 1.12/100 # Index divident yield, daily values available in NSE website

sf["mdate"] = pd.Timestamp('20190425') # date of the last thursday of current month

# =============================================================================

sf["ttm"] = (sf['mdate'] - sf['timestamp']).dt.total_seconds()/ (24*60*60 * 365.25)

sf['volatility'] = sf.apply(lambda row: impVol(row["optionType"], row["OptPrice"], row["spot"], row["strike"], row["ttm"], row["riskFree"], row["divYield"]), axis=1)

temp = list(zip(*sf.iloc[:,[0,2,6,7,8,10,11]].apply(lambda row: greeksAll(row["optionType"], row["spot"], row["strike"], row["riskFree"], row["ttm"], row["volatility"], row["divYield"]), axis=1)))

cf = pd.DataFrame(item for item in temp).T
cf.columns = ["price", "delta", "vega", "theta", "rho", "Lambda", 
              "dualDelta", "gamma", "vanna", "charm", "veta", "vomma", 
              "dualGamma", "speed", "zomma", "color", "ultima"]


xf = pd.concat([sf, cf], axis='columns')

xf["pdiff"] = xf["OptPrice"] - xf["price"]

xf["pdiffb"] = pd.cut( xf["pdiff"], 10 )
xf.groupby('pdiffb').size()

sns.distplot( xf["pdiff"] )


g = sns.FacetGrid(xf, col="optionType", margin_titles=True)
g = g.map(plt.plot, "speed", "", color="steelblue", lw=0)


tips = sns.load_dataset("tips")
g = sns.FacetGrid(tips, col="time", row="smoker")
g = g.map(plt.hist, "total_bill")


# code to check trading volumes in market
# needed to find which strike contracts are most active

#x = pd.crosstab(df["strike"],  columns="count")
#x = x.reset_index()
#
#x["putvc"] = 0
#x["putcc"] = 0
#
#for row in range(len(x)):
#    sf = df[(df.strike == x.iloc[row,0])]
#    y = pd.crosstab(sf["volume.call"],  columns="count")
#    z = pd.crosstab(sf["volume.put"],  columns="count")
#    
#    x.loc[row, "putcc"] = len(y)
#    x.loc[row, "putvc"] = len(z)
#
#
#max(x["putcc"])
#max(x["putvc"])