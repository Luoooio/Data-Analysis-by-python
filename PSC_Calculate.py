# -*- coding: utf-8 -*-
"""
Created on Sat Jan 16 18:11:22 2021

@author: Administrator
"""
"""
参数说明:
    -i  输入文件目录
    -o  输出文件目录
"""
import pandas as pd
import datetime
import argparse
import os
import numpy as np
from tqdm import tqdm
import threading
import queue as Queue
import re
import csv
#创建锁
mutex = threading.Lock()
q = Queue.Queue()
#创建正则对象，匹配文件中的start and end
rx = re.compile("([A-Z]*_\w*\.\w*):(\w*)-(\w*)")

def single_Vcf_analysis(queue,outputPath):
    while True:
        file = queue.get()
        outputFilename = os.path.join(outputPath,os.path.basename(os.path.dirname(file))+'.igv')
        with open(file,'r') as f:
            lines = f.readlines()
            f.seek(0)
            readall = f.read()
        ref = rx.findall(readall)
        chromosome,start,end = ref[0] if ref else print("%s 匹配错误！！！"%(file))
        wsize = int(end)-int(start)+1
        middle = (int(start)+int(end)-1)/2
        for i in lines:
            if i[0:3] == 'PSC':
#                print("提取成功")
                nHets = int(i.split('\t')[5])
                nMissing = int(i.split('\t')[-1])
        try:
#            print(wsize)
            H0 = 1 - round(nHets/(wsize-nMissing),7)
            strd = "%s	%i	%i	snp	%f \n"%(chromosome,middle-1,middle,H0)
            if os.path.exists(outputFilename):
                mutex.acquire()
                with open(outputFilename,'a') as f:
                    f.write(strd)
                mutex.release()
            else:
                mutex.acquire()
                with open(outputFilename,'a') as f:
                    f.write("Chromosome	Start	End	Feature	H0\n")
                    f.write(strd)
                mutex.release()
        except NameError:
            print("%s 无法提取PSC信息，请检查"%s(file))
        queue.task_done()
            
def dir_Vcf_analysis(filedir,outputPath):
    for i in os.listdir(filedir):
        filePath = os.path.join(filedir,i)
#        print(filePath)
        q.put(filePath)
#    print(q.qsize())
    for i in range(4):
        t=threading.Thread(target=single_Vcf_analysis,args=(q,outputPath))
        t.setDaemon(True)
        t.start()
    q.join()
DATE = datetime.datetime.now()
DATE = DATE.strftime("_%m%d%H%M%S")
if __name__ == '__main__':
    # 参数解析
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', '-i', help='Input file path',type=str)
    parser.add_argument('--output', '-o', help='Output file path,this is an optional parameter',type=str)
    args = parser.parse_args()
    inputPath = args.input if args.input else print("输入路径错误")
    outputPathB = os.path.join(os.getcwd(),"Vcf_analysis")
    outputPath = args.output if args.output else outputPathB
    # 计算
    x = 0 if os.path.exists(outputPath) else os.makedirs(outputPath)
    if os.path.exists(inputPath):
        for i in tqdm(os.listdir(inputPath)):
            filedir = os.path.join(inputPath,i)
            if os.path.isdir(filedir):
                dir_Vcf_analysis(filedir,outputPath)
    print('计算完成！！！')
    # 排序
    for i in os.listdir(outputPath):
        filename = os.path.join(outputPath,i)
        pda = pd.read_table(filename)
        pda = pda.sort_values('End')
        pda = pda.drop_duplicates(subset=None,keep='first',inplace=False)
        pda.to_csv(filename,index=False,sep='\t',quoting=csv.QUOTE_NONE)
    print('排序完成！！！')

