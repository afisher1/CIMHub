# Copyright (C) 2022-2023 Battelle Memorial Institute
# -*- coding: utf-8 -*-
"""
Created on Tue Jan  10 13:34:29 2023

@author: wang109
"""
# translates raw XML (PSLF/PSSE) to CIM XML
#
# using Python 3 XML module as documented at:
#   https://docs.python.org/3/library/xml.etree.elementtree.html
# CIMHub uses lxml:
#   from lxml import etree
#   from lxml.etree import Element, ElementTree, QName

from argparse import ArgumentParser
from copy import deepcopy
import uuid
import os
import re
import numpy as np
import pandas as pd
from lxml import etree as et
import scipy.constants
import math
import sys

#%% 
def getStartEndLinesNo(fileName, stringbegin, stringend):   
  startLine = 0
  endLine = 0
  f = open(fileName,'r')
  lines = f.readlines()
  f.close()  
  for i in range(len(lines)):
    line = lines[i]
    linesplit = [x.strip() for x in line.strip().split(',')]
    if len(linesplit) > 1 :
      if linesplit[1] == stringbegin:
        startLine = i
      if linesplit[0] == stringend:
        endLine = i
    else:
      if linesplit[0] == stringend:
        endLine = i
  if startLine != 0:
    for j in range(10):
      line = lines[startLine+j+1]
      if line[0] !='@':
        startLine = startLine+j
        break
      else:
        print('skip: ', line)
  return [startLine , endLine]

def loadRaw(raw_file, savetocsv=False): 
  dflist = []
  filename = raw_file
  if sys.platform == 'win32':
    df_0 = pd.read_csv(filename, header=None, sep='\r\n') 
  else:
    df_0 = pd.read_csv(filename, header=None, sep='\r\n') 
  lineskip = 0

  # Grab case data records
  startLine = 0
  fh = open(raw_file, 'r')
  lines = fh.readlines()
  fh.close
  columns = {0:'IC',1:'SBASE',2:'REV',3:'XFRRAT',4:'NXFRAT',5:'BASFRQ'}
  if '@' not in lines[0]:
    df_tmp = df_0.loc[0:2].reset_index()
  else:
    df_tmp = df_0.loc[1:3].reset_index()
  df_tmp2 = df_tmp[0].str.split(r",", expand=True)
  if len(df_tmp2.columns) > len(columns):
    df_tmp2.drop(columns=range(len(columns),len(df_tmp2.columns)),inplace=True)
  df_tmp2.drop(index=[1,2], inplace=True)
  df_tmp2.iloc[0,5] = df_tmp2.iloc[0,5].split("/")[0].strip()
  df_tmp2.rename(columns=columns,inplace=True)
  df_tmp2 = df_tmp2.map(lambda x: x.strip() if isinstance(x, str) else x)
  dflist.append(df_tmp2)
  psse_version = int(df_tmp2.loc[0,'REV'])
  #%%
  stringbegin = 'BEGIN BUS DATA'
  stringend = '0 / END OF BUS DATA'
  [startLine, endLine] = getStartEndLinesNo(filename, stringbegin, stringend)
  if startLine!=0 and endLine !=0:
    df_tmp = df_0.loc[startLine+1+lineskip : endLine-1].reset_index()
    df_tmp2 = df_tmp[0].str.split(r",", expand=True)
    if len(df_tmp2)>0:
      list_keys = ['I', 'NAME', 'BASKV', 
            'IDE', 'AREA', 'ZONE', 
            'OWNER', 'VM', 'VA', 
            'NVHI', 'NVLO', 'EVHI', 'EVLO']
      df_tmp2.rename(columns={0: list_keys[0], 1: list_keys[1], 2: list_keys[2], 
                  3: list_keys[3], 4: list_keys[4], 5: list_keys[5], 
                  6: list_keys[6], 7: list_keys[7], 8: list_keys[8], 
                  9: list_keys[9], 10: list_keys[10], 
                  11: list_keys[11], 12: list_keys[12]}, inplace=True)
      df_tmp2 = df_tmp2.map(lambda x: x.strip() if isinstance(x, str) else x)
      df_tmp2["NAME"] = df_tmp2["NAME"].apply(lambda x: x.replace("\'", "").strip() if isinstance(x, str) else x)
      print('BUS DATA LOADED')
      print(df_tmp2)
      dflist.append(df_tmp2)
    else:
      dflist.append(df_tmp2)
      print('EMPTY section')
  
  #%%
  stringbegin = 'BEGIN LOAD DATA'
  stringend = '0 / END OF LOAD DATA'
  [startLine, endLine] = getStartEndLinesNo(filename, stringbegin, stringend)
  if startLine!=0 and endLine !=0:
    df_tmp = df_0.loc[startLine+1+lineskip : endLine-1].reset_index()
    df_tmp2 = df_tmp[0].str.split(r",", expand=True)
    if len(df_tmp2)>0:
      if psse_version == 33:
          list_keys = ['I', 'ID', 'STAT', 
              'AREA', 'ZONE', 'PL', 
              'QL', 'IP', 'IQ', 
              'YP', 'YQ', 'OWNER', 
              'SCALE', 'INTRPT']
          df_tmp2.rename(columns={0: list_keys[0], 1: list_keys[1], 2: list_keys[2], 
                    3: list_keys[3], 4: list_keys[4], 5: list_keys[5], 
                    6: list_keys[6], 7: list_keys[7], 8: list_keys[8], 
                    9: list_keys[9], 10: list_keys[10], 11: list_keys[11], 
                    12: list_keys[12], 13: list_keys[13]}, inplace=True)
      elif psse_version == 34:
        list_keys = ['I', 'ID', 'STAT', 
              'AREA', 'ZONE', 'PL', 
              'QL', 'IP', 'IQ', 
              'YP', 'YQ', 'OWNER', 
              'SCALE', 'INTRPT', 'DGENP',
              'DGENQ', 'DGENF']
        df_tmp2.rename(columns={0: list_keys[0], 1: list_keys[1], 2: list_keys[2], 
                    3: list_keys[3], 4: list_keys[4], 5: list_keys[5], 
                    6: list_keys[6], 7: list_keys[7], 8: list_keys[8], 
                    9: list_keys[9], 10: list_keys[10], 11: list_keys[11], 
                    12: list_keys[12], 13: list_keys[13], 14: list_keys[14],
                    15: list_keys[15], 16: list_keys[16]}, inplace=True)
      else:
        raise RuntimeError(f"unsupported PSSE Raw version file provide: {psse_version}. Supported versions are 33 and 34.")
      df_tmp2 = df_tmp2.map(lambda x: x.strip() if isinstance(x, str) else x)
      df_tmp2["ID"] = df_tmp2["ID"].apply(lambda x: x.replace("\'", "").strip() if isinstance(x, str) else x)
      print('LOAD DATA LOADED')
      print(df_tmp2)
      dflist.append(df_tmp2)
    else:
      dflist.append(df_tmp2)
      print('EMPTY section')
    
  #%%
  stringbegin = 'BEGIN FIXED SHUNT DATA'
  stringend = '0 / END OF FIXED SHUNT DATA'
  [startLine, endLine] = getStartEndLinesNo(filename, stringbegin, stringend)
  if startLine!=0 and endLine !=0:
    df_tmp = df_0.loc[startLine+1+lineskip : endLine-1].reset_index()
    df_tmp2 = df_tmp[0].str.split(r",", expand=True)
    if len(df_tmp2)>0:
      list_keys = ['I', 'ID', 'STATUS', 'GL', 'BL']
      df_tmp2.rename(columns={0: list_keys[0], 1: list_keys[1], 2: list_keys[2], 
                  3: list_keys[3], 4: list_keys[4]}, inplace=True)
      df_tmp2 = df_tmp2.map(lambda x: x.strip() if isinstance(x, str) else x)
      df_tmp2["ID"] = df_tmp2["ID"].apply(lambda x: x.replace("\'", "").strip() if isinstance(x, str) else x)
      print('FIXED SHUNT DATA LOADED')
      print(df_tmp2)
      dflist.append(df_tmp2)
    else:
      dflist.append(df_tmp2)
      print('EMPTY section')
    
  #%%
  stringbegin = 'BEGIN GENERATOR DATA'
  stringend = '0 / END OF GENERATOR DATA'
  [startLine, endLine] = getStartEndLinesNo(filename, stringbegin, stringend)
  if startLine!=0 and endLine !=0:
    df_tmp = df_0.loc[startLine+1+lineskip : endLine-1].reset_index()
    df_tmp2 = df_tmp[0].str.split(r",", expand=True)
    if len(df_tmp2)>0:
      list_keys = ['I', 'ID', 'PG', 
            'QG', 'QT', 'QB', 
            'VS', 'IREG', 'MBASE', 
            'ZR', 'ZX', 'RT', 
            'XT', 'GTAP', 'STAT',
            'RMPCT', 'PT', 'PB',
            'O1', 'F1', 'O2', 
            'F2', 'O3', 'F3',
            'O4', 'F4', 'WMOD',
            'WPF','NREG']
      df_tmp2.rename(columns={0: list_keys[0], 1: list_keys[1], 2: list_keys[2], 
                  3: list_keys[3], 4: list_keys[4], 5: list_keys[5], 
                  6: list_keys[6], 7: list_keys[7], 8: list_keys[8], 
                  9: list_keys[9], 10: list_keys[10], 11: list_keys[11], 
                  12: list_keys[12], 13: list_keys[13], 14: list_keys[14],
                  15: list_keys[15], 16: list_keys[16], 17: list_keys[17],
                  18: list_keys[18], 19: list_keys[19], 20: list_keys[20],
                  21: list_keys[21], 22: list_keys[22], 23: list_keys[23],
                  24: list_keys[24], 25: list_keys[25], 26: list_keys[26],
                  27: list_keys[27], 28: list_keys[28]}, inplace=True)
      df_tmp2 = df_tmp2.map(lambda x: x.strip() if isinstance(x, str) else x)
      df_tmp2["ID"] = df_tmp2["ID"].apply(lambda x: x.replace("\'", "").strip() if isinstance(x, str) else x)
      df_tmp2.replace([None],[''],inplace=True)
      print('GENERATOR DATA LOADED')
      print(df_tmp2)
      dflist.append(df_tmp2)
    else:
      dflist.append(df_tmp2)
      print('EMPTY section')
    
  #%%
  stringbegin = 'BEGIN BRANCH DATA'
  stringend = '0 / END OF BRANCH DATA'
  [startLine, endLine] = getStartEndLinesNo(filename, stringbegin, stringend)
  if startLine!=0 and endLine !=0:
    df_tmp = df_0.loc[startLine+1+lineskip : endLine-1].reset_index()
    df_tmp2 = df_tmp[0].str.split(r",", expand=True)
    if len(df_tmp2)>0:
      if psse_version == 33:
        list_keys = ['I', 'J', 'CKT', 'R', 'X', 'B', 
              'RATEA', 'RATEB', 'RATEC', 'GI', 
              'BI', 'GJ', 'BJ', 'ST', 
              'MET', 'LEN', 'O1', 'F1', 
              'O2', 'F2', 'O3', 'F3', 
              'O4', 'F4']
        df_tmp2.rename(columns={0: list_keys[0], 1: list_keys[1], 2: list_keys[2], 
                    3: list_keys[3], 4: list_keys[4], 5: list_keys[5],
                    6: list_keys[6], 7: list_keys[7], 8: list_keys[8],
                    9: list_keys[9], 10: list_keys[10], 11: list_keys[11],
                    12: list_keys[12], 13: list_keys[13], 14: list_keys[14],
                    15: list_keys[15], 16: list_keys[16], 17: list_keys[17],
                    18: list_keys[18], 19: list_keys[19], 20: list_keys[20],
                    21: list_keys[21], 22: list_keys[22], 23: list_keys[23]}, inplace=True)
      elif psse_version == 34:
        list_keys = ['I', 'J', 'CKT', 'R', 'X', 'B', 
              'NAME', 'RATE1', 'RATE2', 'RATE3', 
              'RATE4', 'RATE5', 'RATE6', 'RATE7', 
              'RATE8', 'RATE9', 'RATE10', 'RATE11',
              'RATE12', 'GI', 'BI', 'GJ', 'BJ', 'STAT', 'MET', 'LEN',
              'O1', 'F1', 'O2', 'F2', 'O3', 'F3', 
              'O4', 'F4']
        df_tmp2.rename(columns={0: list_keys[0], 1: list_keys[1], 2: list_keys[2], 
                    3: list_keys[3], 4: list_keys[4], 5: list_keys[5],
                    6: list_keys[6], 7: list_keys[7], 8: list_keys[8],
                    9: list_keys[9], 10: list_keys[10], 11: list_keys[11],
                    12: list_keys[12], 13: list_keys[13], 14: list_keys[14],
                    15: list_keys[15], 16: list_keys[16], 17: list_keys[17],
                    18: list_keys[18], 19: list_keys[19], 20: list_keys[20],
                    21: list_keys[21], 22: list_keys[22], 23: list_keys[23],
                    24: list_keys[24], 25: list_keys[25], 26: list_keys[26],
                    27: list_keys[27], 28: list_keys[28], 29: list_keys[29],
                    30: list_keys[30], 31: list_keys[31], 32: list_keys[32], 
                    33: list_keys[33]}, inplace=True)
      df_tmp2 = df_tmp2.map(lambda x: x.strip() if isinstance(x, str) else x)
      df_tmp2["CKT"] = df_tmp2["CKT"].apply(lambda x: x.replace("\'", "").strip() if isinstance(x, str) else x)
      if 'NAME' in df_tmp2.columns:
        df_tmp2["NAME"] = df_tmp2["NAME"].apply(lambda x: x.replace("\'", "").strip() if isinstance(x, str) else x)
      df_tmp2.replace([None],[''],inplace=True)
      print('BRANCH DATA LOADED')
      print(df_tmp2)
      dflist.append(df_tmp2)
    else:
      dflist.append(df_tmp2)
      print('EMPTY section')
  
  #%% 
  stringbegin = 'BEGIN TRANSFORMER DATA'
  stringend = '0 / END OF TRANSFORMER DATA'
  [startLine, endLine] = getStartEndLinesNo(filename, stringbegin, stringend)
  if startLine!=0 and endLine !=0:
    df_tmp = df_0.loc[startLine+1+lineskip : endLine-1].reset_index()
    df_tmp2 = df_tmp[0].str.split(r",", expand=True)
    if psse_version == 33:
      list_keys_1 = ['I', 'J', 'K', 'CKT', 'CW', 'CZ', 'CM', 'MAG1', 'MAG2', 'NMETR', 'NAME', 'STAT', 'O1', 'F1', 'O2', 'F2', 'O3', 'F3', 'O4', 'F4', 'VECGRP']
      list_keys_2 = ['R1-2', 'X1-2', 'SBASE1-2', 'R2-3', 'X2-3', 'SBASE2-3', 'R3-1', 'X3-1', 'SBASE3-1', 'VMSTAR', 'ANSTAR']
      list_keys_3 = ['WINDV1', 'NOMV1', 'ANG1', 'RATA1', 'RATB1', 'RATC1', 'COD1', 'CONT1', 'RMA1', 'VMA1', 'VMI1', 'NTP1', 'TAB1', 'CR1', 'CX1', 'CNXA1']
      list_keys_4 = ['WINDV2', 'NOMV2', 'ANG2', 'RATA2', 'RATB2', 'RATC2', 'COD2', 'CONT2', 'RMA2', 'VMA2', 'VMI2', 'NTP2', 'TAB2', 'CR2', 'CX2', 'CNXA2']
      list_keys_5 = ['WINDV3', 'NOMV3', 'ANG3', 'RATA3', 'RATB3', 'RATC3', 'COD3', 'CONT3', 'RMA3', 'VMA3', 'VMI3', 'NTP3', 'TAB3', 'CR3', 'CX3', 'CNXA3']
    elif psse_version == 34:
      list_keys_1 = ['I', 'J', 'K', 'CKT', 'CW', 'CZ', 'CM', 'MAG1', 'MAG2', 'NMETR', 'NAME', 'STAT', 'O1', 'F1', 'O2', 'F2', 'O3', 'F3', 'O4', 'F4', 'VECGRP', 'ZCOD']
      list_keys_2 = ['R1-2', 'X1-2', 'SBASE1-2', 'R2-3', 'X2-3', 'SBASE2-3', 'R3-1', 'X3-1', 'SBASE3-1', 'VMSTAR', 'ANSTAR']
      list_keys_3 = ['WINDV1', 'NOMV1', 'ANG1', 'RATE1-1', 'RATE1-2', 'RATE1-3', 'RATE1-4', 'RATE1-5', 'RATE1-6', 'RATE1-7', 'RATE1-8', 'RATE1-9', 'RATE1-10', 'RATE1-11', 'RATE1-12', 'COD1', 'CONT1', 'RMA1', 'VMA1', 'VMI1', 'NTP1', 'TAB1', 'CR1', 'CX1', 'CNXA1', 'NOD1']
      list_keys_4 = ['WINDV2', 'NOMV2', 'ANG2', 'RATE2-1', 'RATE2-2', 'RATE2-3', 'RATE2-4', 'RATE2-5', 'RATE2-6', 'RATE2-7', 'RATE2-8', 'RATE2-9', 'RATE2-10', 'RATE2-11', 'RATE2-12', 'COD2', 'CONT2', 'RMA2', 'VMA2', 'VMI2', 'NTP2', 'TAB2', 'CR2', 'CX2', 'CNXA2', 'NOD2']
      list_keys_5 = ['WINDV3', 'NOMV3', 'ANG3', 'RATE3-1', 'RATE3-2', 'RATE3-3', 'RATE3-4', 'RATE3-5', 'RATE3-6', 'RATE3-7', 'RATE3-8', 'RATE3-9', 'RATE3-10', 'RATE3-11', 'RATE3-12', 'COD3', 'CONT3', 'RMA3', 'VMA3', 'VMI3', 'NTP3', 'TAB3', 'CR3', 'CX3', 'CNXA3', 'NOD3']
    df_tmp3_list = []
    idx = 0
    while idx < df_tmp2.shape[0]:
      transformerDict = {}
      isThreeWinding = False
      if df_tmp2.iloc[idx,2].strip() != '0':
        isThreeWinding = True
      for jdx in range(min(len(df_tmp2.iloc[idx]), len(list_keys_1))):
        if isinstance(df_tmp2.iloc[idx, jdx], str):
          transformerDict[list_keys_1[jdx]] = df_tmp2.iloc[idx, jdx].strip()
        else:
          transformerDict[list_keys_1[jdx]] = df_tmp2.iloc[idx, jdx]
      idx+=1
      for jdx in range(min(len(df_tmp2.iloc[idx]), len(list_keys_2))):
        if isinstance(df_tmp2.iloc[idx, jdx], str):
          transformerDict[list_keys_2[jdx]] = df_tmp2.iloc[idx, jdx].strip()
        else:
          transformerDict[list_keys_2[jdx]] = df_tmp2.iloc[idx, jdx]
      idx+=1
      for jdx in range(min(len(df_tmp2.iloc[idx]), len(list_keys_3))):
        if isinstance(df_tmp2.iloc[idx, jdx], str):
          transformerDict[list_keys_3[jdx]] = df_tmp2.iloc[idx, jdx].strip()
        else:
          transformerDict[list_keys_3[jdx]] = df_tmp2.iloc[idx, jdx]
      idx+=1
      for jdx in range(min(len(df_tmp2.iloc[idx]), len(list_keys_4))):
        if isinstance(df_tmp2.iloc[idx, jdx], str):
          transformerDict[list_keys_4[jdx]] = df_tmp2.iloc[idx, jdx].strip()
        else:
          transformerDict[list_keys_4[jdx]] = df_tmp2.iloc[idx, jdx]
      if isThreeWinding:
        idx+=1
        for jdx in range(min(len(df_tmp2.iloc[idx]), len(list_keys_5))):
          if isinstance(df_tmp2.iloc[idx, jdx], str):
            transformerDict[list_keys_5[jdx]] = df_tmp2.iloc[idx, jdx].strip()
          else:
            transformerDict[list_keys_5[jdx]] = df_tmp2.iloc[idx, jdx]
      idx+=1
      df_tmp3_list.append(deepcopy(transformerDict))
    df_tmp3 = pd.DataFrame(df_tmp3_list)
    df_tmp3.fillna(np.nan,inplace=True)
    df_tmp3.replace(np.nan, '', inplace=True)
    # len_tmp = int((endLine-startLine-1-lineskip)/4)
    # df_tmp3 = pd.DataFrame(0, index=np.arange(len_tmp, dtype=object), columns=(list_keys_1+list_keys_2+list_keys_3))
    # for i in range(len_tmp):
    #   for j in range(len(list_keys_1)):
    #     df_tmp3.iloc[i, j] = df_tmp2.iloc[4*i, j].strip()
    #   for j in range(len(list_keys_2)):
    #     df_tmp3.iloc[i, len(list_keys_1)+j] = df_tmp2.iloc[4*i+1, j].strip()
    #   df_tmp3.loc[i, 'WINDV1'] = df_tmp2.iloc[4*i+2, 0].strip()
    #   df_tmp3.loc[i, 'NOMV1'] = df_tmp2.iloc[4*i+2, 1].strip()
    #   df_tmp3.loc[i, 'WINDV2'] = df_tmp2.iloc[4*i+3, 0].strip()
    #   df_tmp3.loc[i, 'NOMV2'] = df_tmp2.iloc[4*i+3, 1].strip()

    df_tmp3["CKT"] = df_tmp3["CKT"].apply(lambda x: x.replace("\'", "").strip() if isinstance(x, str) else x)
    df_tmp3["NAME"] = df_tmp3["NAME"].apply(lambda x: x.replace("\'", "").strip() if isinstance(x, str) else x)
    df_tmp3["VECGRP"] = df_tmp3["VECGRP"].apply(lambda x: x.replace("\'", "").strip() if isinstance(x, str) else x)
    
    print('TRANSFORMER DATA LOADED')
    if len(df_tmp3)>0:
      print(df_tmp3)
      dflist.append(df_tmp3)
    else:
      dflist.append(df_tmp2)
      print('EMPTY section')
  
  #%%
  stringbegin = 'BEGIN AREA DATA'
  stringend = '0 / END OF AREA DATA'
  [startLine, endLine] = getStartEndLinesNo(filename, stringbegin, stringend)
  if startLine!=0 and endLine !=0:
    df_tmp = df_0.loc[startLine+1+lineskip : endLine-1].reset_index()
    df_tmp2 = df_tmp[0].str.split(r",", expand=True)
    if len(df_tmp2)>0:
      list_keys = ['I', 'ISW', 'PDES', 'PTOL', 'ARNAME']
      df_tmp2.rename(columns={0: list_keys[0], 1: list_keys[1], 2: list_keys[2], 
                  3: list_keys[3], 4: list_keys[4]}, inplace=True)
      df_tmp2 = df_tmp2.map(lambda x: x.strip() if isinstance(x, str) else x)
      df_tmp2["ARNAME"] = df_tmp2["ARNAME"].apply(lambda x: x.replace("\'", "").strip() if isinstance(x, str) else x)
      print('AREA DATA LOADED')
      print(df_tmp2)
      dflist.append(df_tmp2)
    else:
      dflist.append(df_tmp2)
      print('EMPTY section')
  
  #%%
  stringbegin = 'BEGIN ZONE DATA'
  stringend = '0 / END OF ZONE DATA'
  [startLine, endLine] = getStartEndLinesNo(filename, stringbegin, stringend)
  if startLine!=0 and endLine !=0:
    df_tmp = df_0.loc[startLine+1+lineskip : endLine-1].reset_index()
    df_tmp2 = df_tmp[0].str.split(r",", expand=True)
    if len(df_tmp2)>0:
      list_keys = ['I', 'ZONAME']
      df_tmp2.rename(columns={0: list_keys[0], 1: list_keys[1]}, inplace=True)
      df_tmp2 = df_tmp2.map(lambda x: x.strip() if isinstance(x, str) else x)
      df_tmp2["ZONAME"] = df_tmp2["ZONAME"].apply(lambda x: x.replace("\'", "").strip() if isinstance(x, str) else x)
      print('ZONE DATA LOADED')
      print(df_tmp2)
      dflist.append(df_tmp2)
    else:
      dflist.append(df_tmp2)
      print('EMPTY section')

  #%%
  stringbegin = 'BEGIN OWNER DATA'
  stringend = '0 / END OF OWNER DATA'
  [startLine, endLine] = getStartEndLinesNo(filename, stringbegin, stringend)
  if startLine!=0 and endLine !=0:
    df_tmp = df_0.loc[startLine+1+lineskip : endLine-1].reset_index()
    df_tmp2 = df_tmp[0].str.split(r",", expand=True)
    if len(df_tmp2)>0:
      list_keys = ['I', 'OWNAME']
      df_tmp2.rename(columns={0: list_keys[0], 1: list_keys[1]}, inplace=True)
      df_tmp2 = df_tmp2.map(lambda x: x.strip() if isinstance(x, str) else x)
      df_tmp2["OWNAME"] = df_tmp2["OWNAME"].apply(lambda x: x.replace("\'", "").strip() if isinstance(x, str) else x)
      print('OWNER DATA LOADED')
      print(df_tmp2)
      dflist.append(df_tmp2)
    else:
      dflist.append(df_tmp2)
      print('EMPTY section')

  #%%
  stringbegin = 'BEGIN SWITCHED SHUNT DATA'
  stringend = '0 / END OF SWITCHED SHUNT DATA'
  [startLine, endLine] = getStartEndLinesNo(filename, stringbegin, stringend)
  if startLine!=0 and endLine !=0:
    df_tmp = df_0.loc[startLine+1+lineskip : endLine-1].reset_index()
    df_tmp2 = df_tmp[0].str.split(r",", expand=True)
    if len(df_tmp2)>0:
      if psse_version == 33:
        list_keys = ['I', 'MODSW', 'ADJM', 'ST', 'VSWHI', 'VSWLO', 
              'SWREG', 'RMPCT', 'RMIDNT', 'BINIT', 'N1', 'B1', 
              'N2', 'B2', 'N3', 'B3', 'N4', 'B4', 'N5', 'B5', 'N6',
              'B6', 'N7', 'B7', 'N8', 'B8']
        df_tmp2.rename(columns={0: list_keys[0], 1: list_keys[1], 2: list_keys[2], 
                    3: list_keys[3], 4: list_keys[4], 5: list_keys[5], 
                    6: list_keys[6], 7: list_keys[7], 8: list_keys[8], 
                    9: list_keys[9], 10: list_keys[10], 11: list_keys[11],
                    12: list_keys[12], 13: list_keys[13], 14: list_keys[14],
                    15: list_keys[15], 16: list_keys[16], 17: list_keys[17],
                    18: list_keys[18], 19: list_keys[19], 20: list_keys[20],
                    21: list_keys[21], 22: list_keys[22], 23: list_keys[23],
                    24: list_keys[24], 25: list_keys[25]}, inplace=True)
      elif psse_version == 34:
        list_keys = ['I', 'MODSW', 'ADJM', 'ST', 'VSWHI', 'VSWLO', 
              'SWREG', 'RMPCT', 'RMIDNT', 'BINIT', 'N1', 'B1', 
              'N2', 'B2', 'N3', 'B3', 'N4', 'B4', 'N5', 'B5', 'N6',
              'B6', 'N7', 'B7', 'N8', 'B8', 'NREG']
        df_tmp2.rename(columns={0: list_keys[0], 1: list_keys[1], 2: list_keys[2], 
                    3: list_keys[3], 4: list_keys[4], 5: list_keys[5], 
                    6: list_keys[6], 7: list_keys[7], 8: list_keys[8], 
                    9: list_keys[9], 10: list_keys[10], 11: list_keys[11],
                    12: list_keys[12], 13: list_keys[13], 14: list_keys[14],
                    15: list_keys[15], 16: list_keys[16], 17: list_keys[17],
                    18: list_keys[18], 19: list_keys[19], 20: list_keys[20],
                    21: list_keys[21], 22: list_keys[22], 23: list_keys[23],
                    24: list_keys[24], 25: list_keys[25], 26: list_keys[26]}, inplace=True)
      df_tmp2 = df_tmp2.map(lambda x: x.strip() if isinstance(x, str) else x)
      df_tmp2["RMIDNT"] = df_tmp2["RMIDNT"].apply(lambda x: x.replace("\'", "").strip() if isinstance(x, str) else x)
      df_tmp2.replace([None],[''],inplace=True)
      print('SWITCHED SHUNT DATA LOADED')
      print(df_tmp2)
      dflist.append(df_tmp2)
    else:
      dflist.append(df_tmp2)
      print('EMPTY section')
  
  #%%
  if savetocsv:
    for i in range(len(dflist)):
      if not dflist[i].empty:
        csvFile = raw_file.replace('.raw', '')
        dflist[i].to_csv(csvFile+'Section'+str(i)+'Data.csv')
    
  return dflist

def convertXML(dflist):
  root = et.Element('root')
  list_subelement = ['CASEDATA', 'BUSDATA', 'LOADDATA', 'FIXEDSHUNTDATA', 
             'GENERATORDATA', 'BRANCHDATA', 'TRANSFORMERDATA', 
             'AREADATA', 'ZONEDATA', 'OWNERDATA', 'SWITCHEDSHUNTDATA']
  
  for i in range(len(list_subelement)):
    df = dflist[i]
    if not df.empty:
      list_keys = df.columns.to_list()
      list_keys_clean = [x.replace("\'", "") for x in list_keys]
      list_keys_clean = [x.replace("-", "") for x in list_keys_clean]
      for row in df.iterrows():
        expression = list_subelement[i]+" = et.SubElement(root, '"+list_subelement[i]+"')"
        # print(expression)
        exec(expression)
        for j in range(len(list_keys)):
          key = list_keys[j]
          key_clean = list_keys_clean[j]
          expression = key_clean+" = et.SubElement("+list_subelement[i]+", '"+key_clean+"')"
          # print(expression)
          exec(expression)
        for j in range(len(list_keys)):
          key = list_keys[j]
          key_clean = list_keys_clean[j]
          expression = key_clean+".text = str(row[1][\""+key+"\"])"
          # print(expression)
          exec(expression)
  return root


def main(raw_file: str, xml_file: str):
  #%% load raw file as DataFrame
  dflist = loadRaw(raw_file, savetocsv=False)
  
  #%% find unique id for load and generator
  tmp = [dflist[1].iloc[:, [1, 2]], dflist[3].iloc[:, [1, 2]]]
  tmp2 = pd.concat(tmp).reset_index()
  list_uni_id = []
  for i in range(len(tmp2)):
    id_tmp = str(tmp2.iloc[i, 1])+str(tmp2.iloc[i, 2])
    if id_tmp not in list_uni_id:
      list_uni_id.append(id_tmp)
  print('unique id length: ', len(list_uni_id), ' vs. length of load & generator data: ', len(tmp2))

  #%% write DataFrame as xml file
  root = convertXML(dflist)
  print(et.tostring(root, pretty_print=True).decode('utf-8'))
  tree = et.ElementTree(root)
  tree.write(xml_file, pretty_print=True)

#%%
if __name__ == "__main__":
  
  parser = ArgumentParser()
  parser.add_argument("raw_file", help="The full file path to the PSSE raw file to convert.")
  parser.add_argument("xml_file_name", help="The desired xml output file name. If you want the file generated in a specific path please provide a full file path in the argument.")
  args = parser.parse_args()
  main(args.raw_file, args.xml_file_name)
  # user selected model
"""   for model in ["IEEE118", "WECC240"]:
  
    if model == "IEEE118": 
      rawpath = 'ieee118/'
      rawname = 'ieee-118-bus-v4.raw'
      xmlname = 'IEEE118.xml'
    elif model == "WECC240":
      rawpath = 'wecc240/'
      rawname = '240busWECC_2018_PSS.raw'
      xmlname = 'WECC240.xml'
    else:
      sys.exit("this model is not supported")
    
    #%% load raw file as DataFrame
    dflist = loadRaw(rawpath, rawname, savetocsv=False)
    
    #%% find unique id for load and generator
    tmp = [dflist[1].iloc[:, [1, 2]], dflist[3].iloc[:, [1, 2]]]
    tmp2 = pd.concat(tmp).reset_index()
    list_uni_id = []
    for i in range(len(tmp2)):
      id_tmp = str(tmp2.iloc[i, 1])+str(tmp2.iloc[i, 2])
      if id_tmp not in list_uni_id:
        list_uni_id.append(id_tmp)
    print('unique id length: ', len(list_uni_id), ' vs. length of load & generator data: ', len(tmp2))

    #%% write DataFrame as xml file
    root = convertXML(dflist)
    print(et.tostring(root, pretty_print=True).decode('utf-8'))
    tree = et.ElementTree(root)
    tree.write(xml_file, pretty_print=True) """
    
  