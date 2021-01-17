# -*- coding: utf-8 -*-
"""
Created on Fri Jan 15 15:59:50 2021

@author: Administrator
"""

"""
参数说明:
    -i  输入文件目录
    -o  输出文件目录
    -w  window size 滑动窗口大小
    -s  step size 步幅大小，默认等于-w
"""

import pandas as pd
import datetime
import argparse
import os
import numpy as np
from tqdm import tqdm

DATE = datetime.datetime.now()
DATE = DATE.strftime("_%m%d%H%M%S")
ALLSIZE = 149682049
SHSTR = '#!/bin/sh\n'
if __name__ == '__main__':
    # 参数解析
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', '-i', help='Input file path',type=str)
    parser.add_argument('--output', '-o', help='Output file path,this is an optional parameter',type=str)
    parser.add_argument('--windowsize', '-w', help='Output file path,this is an optional parameter',type=int) 
    parser.add_argument('--stepsize', '-s', help='Output file path,this is an optional parameter',type=int)
    args = parser.parse_args()
    wsize = args.windowsize if args.windowsize else print('windowsize error')
    ssize = args.stepsize if args.stepsize else wsize
    inputPath = args.input if os.path.exists(args.input) else print("input 路径错误")
    outputPath = args.output if args.output else os.getcwd()
    # 生成sh
    for i in os.listdir(inputPath):
        if i.split('.')[-1] == 'gz':
            start = 1
            end = start+wsize-1
            inputfilePath = os.path.join(inputPath,i)
            outputdirPath = os.path.join(outputPath,i.split('.')[0]+"_%i_%i"%(wsize,ssize))
            print("%s已存在"%(outputdirPath)) if os.path.exists(outputdirPath) else os.makedirs(outputdirPath)
            while start < ALLSIZE-wsize:
                outputfilePath = os.path.join(outputdirPath,str(start)+'_'+str(end)+'.vcf')
                SHSTR += 'bcftools stats -r NC_006089.5:%i-%i -s - %s > %s \n'%(start,end,inputfilePath,outputfilePath)
                SHSTR += 'echo 已完成百分之%i \n'%(round(start/ALLSIZE,4)*10000)
                start += ssize
                end = start+wsize-1
    # 保存文件
    SHSTRbytes = bytes(SHSTR,encoding='utf-8')
    with open(os.path.join(os.getcwd(),'BcftoolStart%s.sh'%(DATE)),'wb+') as f:
        f.write(SHSTRbytes)
    