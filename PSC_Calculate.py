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
#创建锁
mutex = threading.Lock()
q = Queue.Queue()

def single_Vcf_analysis(queue,outputPath):
    while True:
        file = queue.get()
        wsizel = os.path.basename(file).split('.')[0].split('_')
        wsize = int(wsizel[1]) - int(wsizel[0]) + 1
        outputFilename = os.path.join(outputPath,os.path.basename(os.path.dirname(file))+'.txt')
        with open(file,'r') as f:
            lines = f.readlines()
        for i in lines:
            if i[0:3] == 'PSC':
#                print("提取成功")
                nHets = int(i.split('\t')[5])
                nMissing = int(i.split('\t')[-1])
        try:
            H0 = 1 - round(nHets/(wsize-nMissing),16)
#            print(H0)
            mutex.acquire()
            with open(outputFilename,'a') as f:
                f.write(str(H0)+'\n')
            mutex.release()
        except NameError:
            print("%s 无法提取PSC信息，请检查"%s(file))
        queue.task_done()
            
def dir_Vcf_analysis(filedir,outputPath):
    for i in os.listdir(filedir):
        filePath = os.path.join(filedir,i)
#        print(filePath)
        q.put(filePath)
    print(q.qsize())
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
    x = 0 if os.path.exists(outputPath) else os.makedirs(outputPath)
    if os.path.exists(inputPath):
        for i in tqdm(os.listdir(inputPath)):
            filedir = os.path.join(inputPath,i)
            if os.path.isdir(filedir):
                dir_Vcf_analysis(filedir,outputPath)
    
    print('Done')
                
    

