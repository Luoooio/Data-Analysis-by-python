# -*- coding: utf-8 -*-
"""
Created on Fri Jan 15 13:42:00 2021

@author: Administrator
"""
"""
-o 是可选参数,如果不指定输出目录,则在当前目录自动创建一个新的文件夹。
"""
import pandas as pd
import datetime
import argparse
import os
import numpy as np
from tqdm import tqdm

DATE = datetime.datetime.now()
DATE = DATE.strftime("_%m%d%H%M%S")

def FST_TO_Z(inputFile,outputFile):
    if os.path.basename(inputFile).split('.')[-1]=='igv':# 格式检查
        fst_bed = pd.read_table(inputFile, sep='\t', header=0)
        fst_bed = fst_bed[['Chromosome','Start','End','Feature','1:2']]
        fst_bed['1:2'] = fst_bed['1:2'].map(lambda x: 0 if x=="na" else x ).astype(np.float64)
        fst_bed['Fst_zscore'] = (fst_bed['1:2'] - fst_bed['1:2'].mean())/fst_bed['1:2'].std(ddof=0)
        fst_z_bed = fst_bed[['Chromosome','Start','End','Feature','Fst_zscore']]
#        print(fst_z_bed.head())   
        fst_z_bed.to_csv(outputFile, sep='\t', index=False)
    else:
        print('%s 文件格式错误，请检查'%(os.path.basename(inputFile)))
"""  
        fst_z_bed = fst_bed[['#chr','position','fst_zscore']]
        fst_only_bed = fst_bed[['#chr','position','weighted_fst']]
        fst_top_bed = fst_bed.loc[(fst_bed['fst_zscore'] >= 5)]
"""
if __name__ == '__main__':
    # 参数解析
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', '-i', help='Input file path',type=str)
    parser.add_argument('--output', '-o', help='Output file path,this is an optional parameter',type=str)
    args = parser.parse_args()
    inputPath = args.input
    outputPath = args.output if args.output else -1 
    if  os.path.exists(outputPath) :
        outputPath = args.output
    else:
        outputPath = os.path.join(os.getcwd(),os.path.basename(inputPath)+DATE)
        os.makedirs(outputPath)
    print(outputPath)
    # 数据处理
    if os.path.exists(inputPath):
        for i in tqdm(os.listdir(inputPath)):
            inputFile = os.path.join(inputPath,i)
            outputFile = os.path.join(outputPath,i)
            if os.path.isfile(inputFile):
                FST_TO_Z(inputFile,outputFile)
            
    else:
        print("路径错误")
    
    