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
from VerilogWriter import VerilogWriter
import os
from shutil import rmtree

def createDir(path):
    """ Create directory """
    try:
        os.makedirs(path)
    except FileExistsError:
        rmtree(path)
        os.makedirs(path)

# Parse the argument
parser = argparse.ArgumentParser(description='Simple CSR Generator.')
parser.add_argument('yml', type=str,
                    help='yml file containing register information')
parser.add_argument('-outdir', type=str,
                    help='Output directory name')
args = parser.parse_args()
yml = args.yml
outdir = args.outdir

fileName = os.path.basename(yml)
filePath = os.path.dirname(yml)
moduleName = fileName.replace('.yml', '')
rtlPath =  filePath + '/' + moduleName + '_csr/rtl' if (outdir == None) else outdir
docPath =  filePath + '/' + moduleName + '_csr/doc' if (outdir == None) else outdir

createDir(rtlPath)
createDir(docPath)

# Parse the yml file
parser = RegParser(yml)
regsInfo = parser.parserAllReg()

# Write the HTML document
hwriter = HtmlWriter(regsInfo, moduleName, docPath)
hwriter.writeAll()

# Write the  Verilog File
vwriter = VerilogWriter(regsInfo, moduleName, rtlPath)
vwriter.writeVerilog()
