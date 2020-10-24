#!/usr/bin/python
#########################################################################################
# Copyright 2020 by Heqing Huang (heqinghuangusc@gmail.com)
#
# Project: Simple CSR Generator
# Author: Heqing Huang
# Date: 10/22/2020
#
# Description:
#   Main program of the Simple CSR Generator
#
#########################################################################################

import sys
sys.dont_write_bytecode = True
import argparse
from RegParser import RegParser
from HtmlWriter import HtmlWriter
import os
from shutil import rmtree

# Parse the argument
parser = argparse.ArgumentParser(description='Simple CSR Generator.')
parser.add_argument('yml', type=str,
                    help='yml file defining containing information')
parser.add_argument('-outdir', type=str,
                    help='Output directory name')
args = parser.parse_args()
yml = args.yml
outdir = args.outdir

fileName = os.path.basename(yml)
filePath = os.path.dirname(yml)
moduleName = fileName.replace('.yml', '')
path =  filePath + '/' + moduleName + '_csr' if (outdir == None) else outdir

try:
    os.mkdir(path)
except FileExistsError:
    rmtree(path)
    os.mkdir(path)

# Parse the yml file
parser = RegParser(yml)
regsInfo = parser.parserAllReg()

# Write the HTML document
hwriter = HtmlWriter(regsInfo, moduleName, path)
hwriter.writeAll()