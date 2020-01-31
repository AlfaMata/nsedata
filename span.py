# -*- coding: utf-8 -*-
"""
Created on Sun Nov 24 19:15:43 2019

@author: itithilien
"""

import pandas as pd
from collections import defaultdict
import xmltodict
import io
import json
from flatten_json import flatten
from scrapelib import getsize #from cd ehscrape

cd "D:\dataset\nov2019"



with open('nsccl.20191031.s.spn') as f:
    bml = f.read()

gx = xmltodict.parse(bml)
ccx  = gx["spanFile"]["pointInTime"]["clearingOrg"]["ccDef"]
futx = gx["spanFile"]["pointInTime"]["clearingOrg"]["exchange"]["futPf"]
oopx = gx["spanFile"]["pointInTime"]["clearingOrg"]["exchange"]["oopPf"]
phyx = gx["spanFile"]["pointInTime"]["clearingOrg"]["exchange"]["phyPf"]


gx["spanFile"]["pointInTime"]["clearingOrg"]["exchange"].keys()

with open('futx.json', 'w') as f:
    f.write(json.dumps(futx))
with open('futx.json', 'r') as read_file:
    rfutx = json.loads(read_file.read())
    #print(loaded_dictionaries[0])

with open('ccx.json', 'w') as f:
    f.write(json.dumps(ccx))
with open('ccx.json', 'r') as read_file:
    rccx = json.loads(read_file.read())

with open('oopx.json', 'w') as f:
    f.write(json.dumps(oopx))
with open('oopx.json', 'r') as read_file:
    roopx = json.loads(read_file.read())

with open('phyx.json', 'w') as f:
    f.write(json.dumps(phyx))
with open('phyx.json', 'r') as read_file:
    rphyx = json.loads(read_file.read())

futx == rfutx

x = rfutx[1]
with open('test.json', 'w') as f:
    f.write(json.dumps(x))



rfutx_f = (flatten(d) for d in rfutx)
rdf = pd.DataFrame(rfutx_f)
rdf.to_csv("rfutx.csv", index=False)

rccx_f = (flatten(d) for d in rccx)
cdf = pd.DataFrame(rccx_f)
cdf.to_csv("rccx.csv", index=False)

oopx_f = (flatten(d) for d in roopx)
odf = pd.DataFrame(oopx_f).T
odf.to_csv("oopxT.csv", index=False)

rphyx_f = (flatten(d) for d in rphyx)
pdf = pd.DataFrame(rphyx_f)
pdf.to_csv("rphyx.csv", index=False)


getsize(rccx)/(1024*1024) #7
getsize(rfutx)/(1024*1024) #14
getsize(roopx)/(1024*1024) #295
getsize(rphyx)/(1024) #.98




# =============================================================================
# def flatten_obj2(data):
#     def get_vals(d, _path = []):
#         for a, b in getattr(d, 'items', lambda :{})():
#             if isinstance(b, list) and all(isinstance(i, dict) or isinstance(i, list) for i in b):
#                 for c in b:
#                     for tv1 in get_vals(c, _path+[a]):
#                         yield tv1
#                     #yield from get_vals(c, _path+[a])
#             elif isinstance(b, dict):
#                 for tv2 in get_vals(b, _path+[a]):
#                     yield tv2
#                 #yield from get_vals(b, _path+[a])
#             else:
#                 yield ['.'.join(_path+[a]), b]
#     results = [i for b in data for i in get_vals(b)]
#     _c = defaultdict(list)
#     for a, b in results:
#         _c[a].append(b)
#     
#     return [{a:list(b) if len(b) > 1 else b[0] for a, b in _c.items()}]
# 
# def flatten_obj(data):
#     def flatten_item(item, keys):
#         if isinstance(item, list):
#             for v in item:
#                 for tv1 in flatten_item(v, keys):
#                     yield tv1
#                 #yield from flatten_item(v, keys)
#         elif isinstance(item, dict):
#             for k, v in item.items():
#                 for tv2 in flatten_item(v, keys+[k]):
#                     yield tv2
#                 #yield from flatten_item(v, keys+[k])
#         else:
#             yield '.'.join(keys), item
# 
#     res = []
#     for item in data:
#         res_item = defaultdict(list)
#         for k, v in flatten_item(item, []):
#             res_item[k].append(v)
#         res.append({k: (v if len(v) > 1 else v[0]) for k, v in res_item.items()})
#     return res
# 
# yyz = flatten_obj(xx)
# yyu = flatten_obj2(xx)
# =============================================================================


# =============================================================================
# from lxml import etree
# root = etree.parse('nsccl.20191031.s.spn').getroot()
# target_elements = root.findall('.//ccDef/*')
# 
# eccDef = list(set([t.tag for t in root.findall('.//ccDef/*')]))
# efutPf = sorted(list(set([t.tag for t in root.findall('.//futPf/*')])))
# eoopPf = list(set([t.tag for t in root.findall('.//oopPf/*')]))
# ephyPf = list(set([t.tag for t in root.findall('.//phyPf/*')]))
# 
# =============================================================================

# =============================================================================
# =============================================================================
# import xml.etree.ElementTree as ET
# from lxml import etree
# from lxml import objectify
# =============================================================================
# root = ET.parse('sest.xml').getroot()
# 
# target_elements = root.findall('.//futPf/*')
# result = [t.tag for t in target_elements]
# taglist = list(set(result))
# 
# for child in root.iter():
#    print child.tag, child.text
#    break
# 
# for each in root.findall('.//futPf'):
#     for ticker in each.find('.//fut'):
#         #tag = {}
#         #tag["Id"] = ticker.attrib['Id']
#         #price = ticker.find('.//p')
#         print ticker.text
# 
# gdf = list()
# root = etree.parse('nsccl.20191031.s.spn').getroot()
# for each in root.findall('.//futPf'):
#     for ticker in each.find('.//fut'):
#         if ticker is not None:
#             gdf.append(ticker.text)
#             print ticker.text
#     
# 
# 
# root = objectify.parse('sest.xml')
# =============================================================================
