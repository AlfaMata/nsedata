# -*- coding: utf-8 -*-
"""
Created on Thu Oct 10 11:00:20 2019

@author: itithilien
"""

from bs4 import BeautifulSoup
import urllib2
from lxml.html import fromstring 
import re
import csv
import requests

import pandas as pd
from lxml.html import parse
from urllib2 import urlopen
from pandas.io.parsers import TextParser

def _unpack(row, kind='td'):
   elts = row.findall('.//%s' % kind)
   return [val.text_content() for val in elts]

def parse_options_data(table):
  rows = table.findall('.//tr')
  header = _unpack(rows[0], kind='th')
  data = [_unpack(r) for r in rows[1:]]
  return TextParser(data, names=header).get_chunk()





fpi = "https://www.fpi.nsdl.co.in/web/Reports/Latest.aspx"
header = {'Accept' : '*/*',
          'Accept-Language' : 'en-US,en;q=0.5',
          'Host': 'nseindia.com',
          'Referer': 'https://nseindia.com/live_market/dynaContent/live_watch/live_index_watch.htm',
          'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1;WOW64;rv:28.0) Gecko Firefox/45',
          'X-Requested-With': 'XMLHttpRequest'}

req = urllib2.Request(fpi,headers=header)
page = urllib2.urlopen(req)
parsed = parse(page)
soup = BeautifulSoup(page)
page.status_code == 200

doc = parsed.getroot()
tables = doc.findall('.//table')
table = parse_options_data(tables[0])



xfc = requests.get(fpi, headers=header)
xfc.status_code == 200
xpage = urllib2.urlopen(xfc.content)
xparse = parse(xfc.content)


xtsf = soup(xfc.content)
tsd = table_to_2d(xtsf)
xtsf.find_all("row")

from itertools import product
def table_to_2d(table_tag):
    rowspans = []  # track pending rowspans
    rows = table_tag.find('tr')

    # first scan, see how many columns we need
    colcount = 0
    for r, row in enumerate(rows):
        cells = row.find(['td', 'th'], recursive=False)
        # count columns (including spanned).
        # add active rowspans from preceding rows
        # we *ignore* the colspan value on the last cell, to prevent
        # creating 'phantom' columns with no actual cells, only extended
        # colspans. This is achieved by hardcoding the last cell width as 1. 
        # a colspan of 0 means “fill until the end” but can really only apply
        # to the last cell; ignore it elsewhere. 
        colcount = max(
            colcount,
            sum(int(c.get('colspan', 1)) or 1 for c in cells[:-1]) + len(cells[-1:]) + len(rowspans))
        # update rowspan bookkeeping; 0 is a span to the bottom. 
        rowspans += [int(c.get('rowspan', 1)) or len(rows) - r for c in cells]
        rowspans = [s - 1 for s in rowspans if s > 1]

    # it doesn't matter if there are still rowspan numbers 'active'; no extra
    # rows to show in the table means the larger than 1 rowspan numbers in the
    # last table row are ignored.

    # build an empty matrix for all possible cells
    table = [[None] * colcount for row in rows]

    # fill matrix from row data
    rowspans = {}  # track pending rowspans, column number mapping to count
    for row, row_elem in enumerate(rows):
        span_offset = 0  # how many columns are skipped due to row and colspans 
        for col, cell in enumerate(row_elem.find(['td', 'th'], recursive=False)):
            # adjust for preceding row and colspans
            col += span_offset
            while rowspans.get(col, 0):
                span_offset += 1
                col += 1

            # fill table data
            rowspan = rowspans[col] = int(cell.get('rowspan', 1)) or len(rows) - row
            colspan = int(cell.get('colspan', 1)) or colcount - col
            # next column is offset by the colspan
            span_offset += colspan - 1
            value = cell.get_text()
            for drow, dcol in product(range(rowspan), range(colspan)):
                try:
                    table[row + drow][col + dcol] = value
                    rowspans[col + dcol] = rowspan
                except IndexError:
                    # rowspan or colspan outside the confines of the table
                    pass

        # update rowspan bookkeeping
        rowspans = {c: s - 1 for c, s in rowspans.items() if s > 1}

    return table


def pre_process_table(table):
    """
    INPUT:
        1. table - a bs4 element that contains the desired table: ie <table> ... </table>
    OUTPUT:
        a tuple of: 
            1. rows - a list of table rows ie: list of <tr>...</tr> elements
            2. num_rows - number of rows in the table
            3. num_cols - number of columns in the table
    Options:
        include_td_head_count - whether to use only th or th and td to count number of columns (default: False)
    """
    rows = [x for x in table.find('tr')]

    num_rows = len(rows)

    # get an initial column count. Most often, this will be accurate
    num_cols = max([len(x.find(['th','td'])) for x in rows])

    # sometimes, the tables also contain multi-colspan headers. This accounts for that:
    header_rows_set = [x.find(['th', 'td']) for x in rows if len(x.find(['th', 'td']))>num_cols/2]

    num_cols_set = []

    for header_rows in header_rows_set:
        num_cols = 0
        for cell in header_rows:
            row_span, col_span = get_spans(cell)
            num_cols+=len([cell.getText()]*col_span)

        num_cols_set.append(num_cols)

    num_cols = max(num_cols_set)

    return (rows, num_rows, num_cols)


def get_spans(cell):
        """
        INPUT:
            1. cell - a <td>...</td> or <th>...</th> element that contains a table cell entry
        OUTPUT:
            1. a tuple with the cell's row and col spans
        """
        if cell.has_attr('rowspan'):
            rep_row = int(cell.attrs['rowspan'])
        else: # ~cell.has_attr('rowspan'):
            rep_row = 1
        if cell.has_attr('colspan'):
            rep_col = int(cell.attrs['colspan'])
        else: # ~cell.has_attr('colspan'):
            rep_col = 1 

        return (rep_row, rep_col)

def process_rows(rows, num_rows, num_cols):
    """
    INPUT:
        1. rows - a list of table rows ie <tr>...</tr> elements
    OUTPUT:
        1. data - a Pandas dataframe with the html data in it
    """
    data = pd.DataFrame(np.ones((num_rows, num_cols))*np.nan)
    for i, row in enumerate(rows):
        try:
            col_stat = data.iloc[i,:][data.iloc[i,:].isnull()].index[0]
        except IndexError:
            print(i, row)

        for j, cell in enumerate(row.find(['td', 'th'])):
            rep_row, rep_col = get_spans(cell)

            #print("cols {0} to {1} with rep_col={2}".format(col_stat, col_stat+rep_col, rep_col))
            #print("\trows {0} to {1} with rep_row={2}".format(i, i+rep_row, rep_row))

            #find first non-na col and fill that one
            while any(data.iloc[i,col_stat:col_stat+rep_col].notnull()):
                col_stat+=1

            data.iloc[i:i+rep_row,col_stat:col_stat+rep_col] = cell.getText()
            if col_stat<data.shape[1]-1:
                col_stat+=rep_col

    return data
