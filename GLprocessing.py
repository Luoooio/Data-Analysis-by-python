# -*- coding: utf-8 -*-
"""
Created on Sun Jan 17 12:50:38 2021

@author: Administrator
"""
import pandas as pd
import datetime
import argparse
import os
import numpy as np
from tqdm import tqdm

DATE = datetime.datetime.now()
DATE = DATE.strftime("%m%d%H%M%S")
MATCH_DICT = {'Pool_Barbue_d脮Anvers_quail':'Pool_Barbue_quail',
              'Pool_Barbue_dÕAnvers_quail':'Pool_Barbue_quail',
              'Plymouth_Rock':'Pool_Plymouth_Rock',
              'Sebright':'Pool_Sebright'
        } #lumpy:gatk

def Gatk_maps(strd):   #gatk的映射函数
    if len(strd.split(','))>3 and '/' in strd:
        if strd[0]=='.' and strd[2]=='.':
            return '.'
        elif strd[0]=='0' and strd[2]=='0':
            return 0
        elif strd[0] == strd[2]:
            return 1
        else:
            return 'H'
    else:
        return strd                    
def Gatk_(file,output,st): #处理gatk文件：表头删除与映射
    assert len(file.split('.'))>2,'数据格式错误，非GATK格式文件'
    strdata = []
    #   对表头进行删除
    with open(file,'r') as f:
        lines = f.readlines()
    for i in lines:
        if i[1] != '#':
            i = i.replace('\n','')
            a = i.split('\t')
            strdata.append(a)

    data_1 = pd.DataFrame(strdata)
    #更改列名
    data_1.columns=data_1.iloc[0,:]
    data_1 = data_1[1:]
    #   进行分类映射
    data_1 = data_1.applymap(Gatk_maps)
    
    if st:
        outputfile = os.path.join(output,os.path.basename(file))
        data_1.to_csv(outputfile,sep='\t',index=False)
    else:
        return data_1


def Gatk_dir(path,output,st):  #从文件夹中处理gatk文件
    for i in tqdm(os.listdir(path)):
        if len(i.split('.'))==3:
            Gatk_(os.path.join(path,i),output,st)
        
def Lumpy_maps(strd):  #lumpy 数据的映射函数
    
    if len(strd.split(':'))==4 and '/' in strd:
        if strd == './.:.:.:.':
            return 0
        else:
            return 1
    else:
        return strd        
def Lumpy_(file,output,st): #处理lumpy文件：映射
    assert len(os.path.basename(file).split('.'))==2,'数据格式错误,非Lumpy格式文件'
    strdata = []
    #   对表头进行删除
    with open(file,'r') as f:
        lines = f.readlines()
    for i in lines:
        if i[1] != '#':
            i = i.replace('\n','')
            a = i.split('\t')
            strdata.append(a)
    #更改列名
    data_2 = pd.DataFrame(strdata)
    data_2.columns=data_2.iloc[0,:]
    data_2 = data_2[1:]
    #   进行分类映射
    data_2 = data_2.applymap(Lumpy_maps)
    
    if st:
        outputfile = os.path.join(output,os.path.basename(file))
        data_2.to_csv(outputfile,sep='\t',index=False)
    else:
        return data_2

def Lumpy_dir(path,output,st): #从文件夹中处理lumpy文件
    for i in tqdm(os.listdir(path)):
        if len(i.split('.'))==2:
            Lumpy_(os.path.join(path,i),output,st)
        
def Fileconcat(file1,file2,output):
    data_gatk = Gatk_(file1,output,False)
    data_lumpy = Lumpy_(file2,output,False)
    #修改lumpy的列名
    data_lumpy = data_lumpy.rename(columns=MATCH_DICT) 
    gatk_Error_list = [i for i in list(data_gatk.columns) if i not in list(data_lumpy.columns)]
    lumpy_Error_list = [i for i in list(data_lumpy.columns) if i not in list(data_gatk.columns)]
    if len(gatk_Error_list)>0 or len(lumpy_Error_list)>0:
        print("警告！！！列名无法对应，请在MATCH_DICT中添加对应")
        print("在GATK中错误的列名:")
        print(gatk_Error_list)
        print("在Lumpy中错误的列名:")
        print(lumpy_Error_list)
    else:
        #合并数据
        GLconcat = data_gatk.append(data_lumpy)
        #以gatk列顺序排布
        GLconcat = GLconcat[data_gatk.columns]
    if output:
        filename = os.path.basename(file1).split('.')
        filename[0] += '_C'
        filename = '.'.join(filename)
        outputfile = os.path.join(output,filename)
        GLconcat.to_csv(outputfile,sep='\t',index=False)
    else:
        print("路径错误")

def GLconcat_(path1,path2,output): #将对应的gatk_(path1)与lumpy_(path2)合并
    for i in tqdm(os.listdir(path1)): 
        if len(i.split('.'))==3:
            file1 = os.path.join(path1,i)
            file2 = os.path.join(path2,i.split('.')[0]+'.vcf')
            if os.path.isfile(file1) and os.path.isfile(file2):
                Fileconcat(file1,file2,output)
            elif os.path.isfile(file2) !=True:
                print("%s文件不存在,请检查"%(file2))
        else:
            continue
if __name__ == '__main__':
    # 参数解析
    parser = argparse.ArgumentParser()
    parser.add_argument('--inputGatk', '-ig', help='Gatk input file path',type=str)
    parser.add_argument('--inputLumpy', '-il', help='Lumpy input file path',type=str)
    parser.add_argument('--output', '-o', help='Output file path,this is an optional parameter',type=str)
    parser.add_argument('--mode', '-m', help='Output file path,this is an optional parameter',type=str,choices=['G','L','C'])
    args = parser.parse_args()
    inputGatk = args.inputGatk if args.inputGatk else -1
    inputLumpy = args.inputLumpy if args.inputLumpy else -1
    mode = args.mode
    #不同模式
    if mode == 'G': #处理Gatk文件
        assert os.path.exists(inputGatk),"请检查Gatkfile路径"
        output = args.output if args.output else os.path.join(os.getcwd(),'m-Gatk-'+DATE)
        x = 0 if os.path.exists(output) else os.makedirs(output)
        Gatk_dir(inputGatk,output,True)
    if mode == 'L': #处理Lumpy文件
        print(inputLumpy)
        assert os.path.exists(inputLumpy),"请检查Lumpyfile路径"
        output = args.output if args.output else os.path.join(os.getcwd(),'m-Lumpy-'+DATE)
        x = 0 if os.path.exists(output) else os.makedirs(output)
        Lumpy_dir(inputLumpy,output,True)
    if mode == 'C': #处理Gatk文件，Lumpy文件后合并
        assert os.path.exists(inputGatk),"请检查Gatkfile路径"
        assert os.path.exists(inputLumpy),"请检查Lumpyfile路径"
        output = args.output if args.output else os.path.join(os.getcwd(),'m-GLconcat-'+DATE)
        x = 0 if os.path.exists(output) else os.makedirs(output)
        GLconcat_(inputGatk,inputLumpy,output)