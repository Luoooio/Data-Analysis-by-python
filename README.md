# Data-Analysis-by-python
## GLprocessing.py 参数说明
```
-m 模式,有G、L、C三种模式。G 为 对GATK的数据进行处理，L 为 对Lumpy的数据进行处理，C 为分别处理后合并成新的文件。
-ig GATK文件路径
-il Lumpy文件路径
-o  可选参数，输出文件路径,如果无此参数，则自动在当前工作目录下新建文件夹储存得到的文件。
```
eg：

`python3 GLprocessing.py -m G -ig /home/Lunwen/GatkDate`

这条命令会对`/home/Lunwen/GatkDate`下的所有以`.g.vcf`结尾的文件进行处理，然后在当前工作目录下生成`m-Gatk-DATA`文件夹，内存储所有处理好的同名Gatk文件。

`python3 GLprocessing.py -m L -il /home/Lunwen/LumpyDate -o /home/Lunwen/LumpyTest`

这条命令会对`/home/Lunwen/LumpyDate`下的所有以`.vcf`结尾的文件进行处理，然后在`/home/Lunwen/LumpyTest`内存储所有处理好的同名Lumpy文件。

`python3 GLprocessing.py -m C -ig /home/Lunwen/GatkDate -il /home/Lunwen/LumpyDate`

这条命令会对`/home/Lunwen/GatkDate`下的所有以`.g.vcf`结尾的文件进行处理，在`/home/Lunwen/LumpyDate`中寻找同名的以`.vcf`结尾的文件然后分别处理后合并，在当前工作目录下生成`m-GLconcat-DATA`文件夹，内存储所有处理好的合并文件。

PS:

1.如果运行中提示列名无法对应的情况，可以更改添加源码开头的MATCH_DICT字典。

## FST_to_Z.py 参数说明
**对.igv格式文件进行z转化**
```
-i 文件路径
-o  可选参数，输出文件路径,如果无此参数，则自动在当前工作目录下新建文件夹储存得到的文件。
```
eg:

`python3 FST_to_Z.py -i /home/Lunwen/FSTest`

该命令会处理 `/home/Lunwen/FSTest`下的所有以`.igv`结尾的文件，然后存储在`FSTest_DATE`文件中。

## PSC_Build_sh.py 参数说明

**生成用bcftool处理的sh脚本**
```
    -i  输入文件目录
    -o  输出文件目录，无则默认在当前工作目录
    -w  window size 滑动窗口大小
    -s  step size 步幅大小，默认等于-w
```
eg:

`python3 PSC_Build_sh.py -i /home/Lunwen -s 10000 -w 50000`

该命令会检测所有`/home/Lunwen`目录下以`.gz`结尾的文件，并在当前工作目录生成sh脚本，并且在输出文件目录/当前工作目录新建类似`Pool_VT4H_50000_10000`的文件夹，以准备存放bcftools处理后的`vcf`文件。

## PSC_Calculate.py 参数说明
**计算所有vcf文件，并生成对应的文件**
```
    -i  输入文件目录
    -o  输出文件目录，无则默认在当前工作目录
```
eg：

`python3 PSC_Calculate.py -i /home/Lunwen/Calu`

该命令会检测Calu下的所有目录，然后对每个文件夹计算平均纯合度，对应保存在`Vcf_analysis`文件下。Calu应具有如下结构
```
|--Calu
  |--Pool_VT4H_50000_50000
    |--1_50000.vcf
    |--50001_100000.vcf
    ……
  |--Pool_VT4H_50000_10000
    ……
```

## Sh_exec.py 参数说明
**该脚本可以执行.sh脚本，并给出命令执行情况**
```
-i sh脚本路径
-t 线程数
```
