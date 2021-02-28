# -*- coding: utf-8 -*-
"""
Created on Sun Feb 28 12:55:05 2021

@author: Administrator
"""
import os
import sys
import getopt
import pandas as pd
import platform
import datetime
from tqdm import tqdm
import argparse
import datetime

DATE = datetime.datetime.now()
DATE = DATE.strftime("_%m%d%H%M%S")

def Cal_het(input,output,wizs,iname):
    Pandany = pd.read_table(input, sep='\t', header=0)
    Pandany_1 = Pandany.loc[:,['##chr','pos','maa_1','mia_1']]
    #提取maa_1与mia_1                             
    Pandany_1['maa_1'] = Pandany_1['maa_1'].map(lambda x:int(x.split('/')[0]))
    Pandany_1['mia_1'] = Pandany_1['mia_1'].map(lambda x:int(x.split('/')[0]))
    #删除0项
    Pandany_1 = Pandany_1.drop(Pandany_1[Pandany_1.maa_1 == 0].index)
    Pandany_1 = Pandany_1.drop(Pandany_1[Pandany_1.mia_1 == 0].index)
    #分组计算hp
    Pan_NEW = []
    i = int(wizs/2)
    Pandany_1_gy = Pandany_1.groupby(Pandany_1['pos'].map(lambda x:x//wizs))
    for name,group in tqdm(Pandany_1_gy):
        li =[]
        li.append(group.iloc[0,0])
        li.append(i-1)
        li.append(i)
        li.append('snp')
        i_maa1 = group.loc[:,'maa_1'].sum()
        i_mia1 = group.loc[:,'mia_1'].sum()
        Hp = 2*i_maa1*i_mia1/((i_maa1+i_mia1)**2)
        li.append(Hp)
        Pan_NEW.append(li)
        i+=wizs
    Pandany_New = pd.DataFrame(Pan_NEW,columns = ['Chromosome','Start','End','Feature','Hp'])
    #Hp列的标准化
    outputFile_Or = os.path.join(output,iname.split('.')[0]+'_Or.igv')
    outputFile_ls = os.path.join(output,iname.split('.')[0]+'.igv')    
    Pandany_New.to_csv(outputFile_Or, sep='\t', index=False)
    Pandany_New['Hp'] = (Pandany_New['Hp'] - Pandany_New['Hp'].mean())/Pandany_New['Hp'].std(ddof=0)
    Pandany_New.to_csv(outputFile_ls, sep='\t', index=False)
if __name__ == '__main__':
    # 参数解析
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', '-i', help='input file path',type=str)
    parser.add_argument('--output', '-o', help='Output file path,this is an optional parameter',type=str)
    parser.add_argument('--windowsize', '-w', help=' ',type=int)
    args = parser.parse_args()
    inputPath = args.input if args.input else print("输入路径错误")
    outputPathB = os.path.join(os.getcwd(),"New_Cal_het"+DATE)
    outputPath = args.output if args.output else outputPathB
    x = 0 if os.path.exists(outputPath) else os.makedirs(outputPath)
    wsize = args.windowsize if args.windowsize else print("输入wsize错误")
    for i in tqdm(os.listdir(inputPath)):
        inputFile = os.path.join(inputPath,i)
        if os.path.isfile(inputFile):
            Cal_het(inputFile,outputPath,wsize,i)