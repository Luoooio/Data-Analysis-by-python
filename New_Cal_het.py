# -*- coding: utf-8 -*-
"""
Created on Sun Feb 28 12:55:05 2021

@author: Administrator
"""
%load_ext Cython
%%cython
import os
import sys
import getopt
import pandas as pd
import platform
import datetime
from tqdm import tqdm
import argparse
import datetime
import time

DATE = datetime.datetime.now()
DATE = DATE.strftime("_%m%d%H%M%S")

def Query_cal_Return(i,wsize,ssize,Pandany):
    groupmin = i*ssize
    groupmax = groupmin+wsize
    local = groupmin+int(wsize/2) 
#    Pandany_cut = Pandany[(Pandany.iloc[:,1]>=groupmin) &
#                              (Pandany.iloc[:,1]<=groupmax)]
    Pandany_cut = Pandany.query('pos>=@groupmin and pos<=@groupmax')
    if Pandany_cut.empty:
        print("%i~%i无数据,进行0填充"%(groupmin,groupmax))
        li =[Pandany.iloc[0,0],local-1,local,'snp',0]
        print("填充结果如下:") 
        print(li)
        return li    
    elif len(Pandany_cut.index)<=10:
        return 0
    else:
        li =[Pandany_cut.iloc[0,0],local-1,local,'snp']
        i_maa1 = Pandany_cut.iloc[:,2].sum()
        i_mia1 = Pandany_cut.iloc[:,3].sum()
        Hp = 2*i_maa1*i_mia1/((i_maa1+i_mia1)**2)
        li.append(Hp)
        return li    
    
def Cal_het(input,output,wizs,iname,ssize):
    Pandany = pd.read_table(input, sep='\t', header=0)
    
    #提取maa_1与mia_1                             
    Pandany_1 = Pandany.iloc[:,[0,1,9,11]]
    Pandany_1['maa_1'] = Pandany_1['maa_1'].map(lambda x:int(x.split('/')[0]))
    Pandany_1['mia_1'] = Pandany_1['mia_1'].map(lambda x:int(x.split('/')[0]))
    #提取maa_2与mia_2   
    Pandany_2 = Pandany.iloc[:,[0,1,10,12]]
    Pandany_2['maa_2'] = Pandany_2['maa_2'].map(lambda x:int(x.split('/')[0]))
    Pandany_2['mia_2'] = Pandany_2['mia_2'].map(lambda x:int(x.split('/')[0]))

    #删除0项
#    Pandany_1 = Pandany_1.drop(Pandany_1[Pandany_1.maa_1 == 0].index)
#    Pandany_1 = Pandany_1.drop(Pandany_1[Pandany_1.mia_1 == 0].index)
    #查询计算hp
    Pan_NEW_1 = []
    Pan_NEW_2 = []
    posmax = Pandany_1.iloc[:,1].max()
    i = 0
    pbar = tqdm(total = posmax/ssize+1)
    while True:
        if i*ssize > posmax:
            break
        li_1 = Query_cal_Return(i,wizs,ssize,Pandany_1)
        li_2 = Query_cal_Return(i,wizs,ssize,Pandany_2)
        if li_1 == 0:
            i+=1
            continue
        Pan_NEW_1.append(li_1)
        Pan_NEW_2.append(li_2)
        pbar.update(1)
        i+=1
    Pandany_New_1 = pd.DataFrame(Pan_NEW_1,columns = ['Chromosome','Start','End','Feature','Hp_S1'])
    Pandany_New_2 = pd.DataFrame(Pan_NEW_2,columns = ['Chromosome','Start','End','Feature','Hp_S2'])

    #Hp列的标准化与保存
    #Pandany_New_1
    outputFile_1_Or = os.path.join(output,iname.split('.')[0]+'_sample_1_Or.igv')
    outputFile_1_St = os.path.join(output,iname.split('.')[0]+'_sample_1_Standard.igv')    
    Pandany_New_1.to_csv(outputFile_1_Or, sep='\t', index=False)
    Pandany_New_1['Hp_S1'] = (Pandany_New_1['Hp_S1'] - Pandany_New_1['Hp_S1'].mean())/Pandany_New_1['Hp_S1'].std(ddof=0)
    Pandany_New_1.to_csv(outputFile_1_St, sep='\t', index=False)
    #Pandany_New_2
    outputFile_2_Or = os.path.join(output,iname.split('.')[0]+'_sample_2_Or.igv')
    outputFile_2_St = os.path.join(output,iname.split('.')[0]+'_sample_2_Standard.igv')    
    Pandany_New_2.to_csv(outputFile_2_Or, sep='\t', index=False)
    Pandany_New_2['Hp_S2'] = (Pandany_New_2['Hp_S2'] - Pandany_New_2['Hp_S2'].mean())/Pandany_New_2['Hp_S2'].std(ddof=0)
    Pandany_New_2.to_csv(outputFile_2_St, sep='\t', index=False)
if __name__ == '__main__':
    time1 = time.time()
    # 参数解析
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', '-i', help='input file path',type=str)
    parser.add_argument('--output', '-o', help='Output file path,this is an optional parameter',type=str)
    parser.add_argument('--windowsize', '-w', help=' ',type=int)
    parser.add_argument('--ssize', '-s', help=' ',type=int)    
    args = parser.parse_args()
    inputPath = args.input if args.input else print("输入路径错误")
    outputPathB = os.path.join(os.getcwd(),"New_Cal_het"+DATE)
    outputPath = args.output if args.output else outputPathB
    x = 0 if os.path.exists(outputPath) else os.makedirs(outputPath)
    wsize = args.windowsize if args.windowsize else print("输入wsize错误")
    ssize = args.ssize if args.ssize else wsize
    for i in tqdm(os.listdir(inputPath)):
        inputFile = os.path.join(inputPath,i)
        if os.path.isfile(inputFile):
            Cal_het(inputFile,outputPath,wsize,i,ssize)
    time2 = time.time()
    print("运行耗时：%s s"%(time2-time1))    