# -*- coding: utf-8 -*-
"""
Created on Sun Jan 17 18:42:09 2021

@author: Administrator
"""
from threading import Thread
from subprocess import Popen,PIPE
from queue import Queue
import argparse
q= Queue()

def cmdExecute(i,queue):
    while True:
        cmd = queue.get()
        Pop = Popen(cmd,stdin=PIPE, stdout=PIPE, stderr=PIPE,shell=True,universal_newlines=True)
        Pop.wait(timeout=5)
        print("已完成%f"%((totalsize-queue.qsize())/totalsize*100))
        q.task_done()
if __name__ == '__main__':
    # 参数解析
    parser = argparse.ArgumentParser()
    parser.add_argument('--inputfile', '-i', help='input file path',type=str)
    parser.add_argument('--thread', '-t', help='The number of threads',type=int)
    args = parser.parse_args()
    inputFile = args.inputfile if args.inputfile else -1
    threads = args.thread if args.thread else 4
    if inputFile:
        with open(inputFile,'r') as f:
            cmdlist = f.readlines()
        for i in cmdlist:
            q.put(i)
        totalsize = q.qsize()
        for i in range(threads):
            t=Thread(target=cmdExecute,args=(i,q))
            t.setDaemon(True)
            t.start()
        q.join()
        print('Done')