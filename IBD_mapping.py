# -*- coding: utf-8 -*-
"""
Created on Fri Apr  9 14:05:47 2021

@author: Administrator
"""
import os
import pandas as pd
import datetime
from tqdm import tqdm
import argparse
import datetime
import numpy as np
import logging
from multiprocessing import Pool
import time
import gc
import random
import sys
#开启日志记录
logging.basicConfig(level=logging.DEBUG)
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%m/%d/%Y %H:%M:%S %p"
logging.basicConfig(filename='IBD.log', level=logging.DEBUG, format=LOG_FORMAT, datefmt=DATE_FORMAT)
DATE = datetime.datetime.now()
DATE = DATE.strftime("_%m%d%H%M%S")
def exeTime( func ):
    def newFunc( *args, **args2 ):
        t0 = time.time()
        back = func( *args, **args2 )
        t1 = time.time()
        print ( t1 - t0 )
        return back
    return newFunc
def exeTime( func ):
    def newFunc( *args, **args2 ):
        t0 = time.time()
        back = func( *args, **args2 )
        t1 = time.time()
        print ( t1 - t0 )
        return back
    return newFunc

def get_seq(df):
    return tuple(zip(df['start'],df['end']))

@exeTime
def generate_dict(tup):
    tqdm.write('开始统计重复区间......')
    interval_dict = dict(pd.value_counts(tup))
    tqdm.write('区间-重复次数字典生成......')
    #得到所有位点的列表
    element_list = []
    for i in tup:
        element_list.append(i[0])
        element_list.append(i[1])
    element_list = sorted(set(element_list))
    tqdm.write("端点排序完成,正在初始化最小区间-重复次数字典")
    tup_dict = {}
    for i in element_list[1:]:
        iindex = element_list.index(i)
        if i-1==element_list[iindex-1]:
            continue
        else:
            tup_dict[(element_list[iindex-1]+1,i-1)] = 0
    tqdm.write("最小区间-重复次数字典初始化完成")
    tqdm.write("开始对区间进行查询......")
    for key,value in tqdm(tup_dict.items(),mininterval=1,ncols=60,colour='green'):
        #randint生成闭区间
        ntu = 0
        choice = random.randint(key[0],key[1])
        for k,v in interval_dict.items():
            if choice>=k[0] and choice<=k[1]:
                ntu = ntu+v
        tup_dict[key] = ntu
    tqdm.write("最小区间-重复次数字典更新完成")
    tqdm.write("开始对端点进行查询......")
    point_dict = {}
    for i in tqdm(element_list,mininterval=1,ncols=60,colour='green'):
        ntu = 0
        for k,v in interval_dict.items():
            if i>=k[0] and i<=k[1]:
                ntu = ntu +v
        point_dict[i] = ntu
    tqdm.write("开始从字典构建series......")
    finally_series = to_Series(tup_dict,point_dict)
    tqdm.write("series构建完成,开始生成结果文件")
    return finally_series
#    return collect_dict
#转化为series
def to_Series(tup_dict,point_dict):
    series_list = []
    for key,value in tup_dict.items():
        series_list.append(pd.Series([value for i in range(key[0],key[1]+1)],index=[i for i in range(key[0],key[1]+1)],dtype=np.int64))
    series_list.append(pd.Series(point_dict,dtype=np.int64))
    return pd.concat(series_list).sort_index()
#传入series对象,重建igv格式文件,返回df

def reBuild(series,inputPath,chromosome):
    reData = pd.DataFrame(series)
    # 将index转变为列
    reData["End"] = reData.index
    # 改变列位
    fq = reData.iloc[:,0]
    reData.insert(2,"fq",fq)
    reData.drop(labels=0,axis=1,inplace = True)
    # 格式设置
    rows = reData.shape[0]
    reData.insert(0,"Chromosome",[chromosome]*rows)
    reData.insert(1,"Start",reData.iloc[:,1]-1)
    reData.insert(3,"Feature",["snp"]*rows)
    #排序
    reData = reData.sort_index()
    #缓存目录
    cache = os.path.join(os.getcwd(),"IBD_cache")
    #缓存文件
    cache_file = os.path.join(cache,os.path.basename(inputPath))
    if os.path.exists(cache):
        reData.to_csv('.'.join([cache_file,"igv"]), sep='\t', index=False)
    else:
        os.makedirs(cache)
        reData.to_csv('.'.join([cache_file,"igv"]), sep='\t', index=False)
    return reData
def dataProcessing(dataFrame):
    tup = get_seq(dataFrame)
    dic = generate_dict(tup)
    return dic
# 所有个体
def allData(file):
    Data = pd.read_table(file,names=['chicken1','chicken2','ch','start','end'])
    return (Data.iloc[:,3:],Data.iloc[1,2].strip())
# 欧洲多趾个体
def e_Data(file):
    #欧洲多趾个体列表
    #测试用表
#    e = ['Leghorn1','Black_Java_3','Brown_Layer_18','White_Leghorn22','Brown_Layer_1',]
    e = ["Dorking1","German_Faverolles1","Pool_German_Faverolles_salmon","Pool_VT4H"]
    Data = pd.read_table(file,names=['chicken1','chicken2','ch','start','end'])
    Data = Data[(Data['chicken1'].str.strip().isin(e))&(Data['chicken2'].str.strip().isin(e))]
    if Data.shape[0]<1:
        logging.warning("%s 无特定IBD."%(file))
        return(pd.DataFrame(),False)
    return (Data.iloc[:,3:],Data.iloc[0,2].strip())
if __name__ == "__main__":
    # 参数解析
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', '-i', help='input file path',type=str)
    parser.add_argument('--mode', '-m', help='a or e',type=str)
    parser.add_argument('--output', '-o', help='Output file path,this is an optional parameter',type=str) 
    args = parser.parse_args()
    inputPath = args.input if args.input else print("输入路径错误")
    mode = args.mode if args.mode else print("请输入正确的MODE")
    outputPathB = os.getcwd()
    outputPath = args.output if args.output else outputPathB

    # df 表
    dfList = []
    if os.path.isdir(inputPath):
        for i in tqdm(os.listdir(inputPath),mininterval=1,ncols=80,colour='green'):
            inputFile = os.path.join(inputPath,i)
            try:
                if mode=="a":
                    dataFrame,ch = allData(inputFile)
                elif mode == "e":
                    dataFrame,ch = e_Data(inputFile)
                else:
                    exit("请输入正确的MODE")
                if ch:
                    Series = dataProcessing(dataFrame)
                    dataFrame_sort = reBuild(Series,inputPath,ch)
                    dfList.append(dataFrame_sort)
                else:
                    continue
                gc.collect()
            except ImportError as e:
                print(e)
        if len(dfList)>0: 
            lastDataframe = pd.concat(dfList)
            lastDataframe = lastDataframe.sort_index()
            if lastDataframe.shape[0]<1:
                logging.warning("No result")
            lastDataframe.to_csv(os.path.join(outputPath,'IBD'+DATE+'.igv'), sep='\t', index=False)
        else:
            exit("no result")
    elif os.path.isfile(inputPath):
        inputFile = inputPath
        try:
            if mode=="a":
                dataFrame,ch = allData(inputFile)
            elif mode == "e":
                dataFrame,ch = e_Data(inputFile)
            else:
                exit("请输入正确的MODE")
            if ch:
                Series = dataProcessing(dataFrame)
                dataFrame_sort = reBuild(Series,inputPath,ch)
            else:
                exit()
        except ImportError as e:
            print(e)
        if dataFrame_sort.shape[0]<1:
            logging.warning("No result")
        dataFrame_sort.to_csv(os.path.join(outputPath,'IBD'+DATE+'.igv'), sep='\t', index=False)
    
    