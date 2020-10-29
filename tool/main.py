#!/usr/bin/python
#########################################################################################
# Copyright 2020 by Heqing Huang (heqinghuangusc@gmail.com)
#
# Project: Simple CSR Generator
# Author: Heqing Huang
# Created: 10/22/2020
#
# Description:
#   Main program of the Simple CSR Generator
#
#########################################################################################

import sys
sys.dont_write_bytecode = True
import argparse
from YmlParser import YmlParser
from HtmlWriter import HtmlWriter
from VerilogWriter import VerilogWriter
from DriverWriter import DriverWriter
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
filePath = os.path.dirname(os.path.abspath(yml))
moduleName = fileName.replace('.yml', '')
rtlPath =  filePath + '/' + moduleName + '_csr/rtl' if (outdir == None) else outdir
docPath =  filePath + '/' + moduleName + '_csr/doc' if (outdir == None) else outdir
driPath =  filePath + '/' + moduleName + '_csr/driver' if (outdir == None) else outdir

createDir(rtlPath)
createDir(docPath)
createDir(driPath)

# Parse the yml file
parser = YmlParser(yml)
parser.parserAllReg()

# Write the HTML document
hwriterInfo = parser.htmlwriter()
hwriter = HtmlWriter(hwriterInfo, moduleName, docPath)
hwriter.writeHtml()

# Write the  Verilog File
verilogInfo = parser.verilogwriter()
vwriter = VerilogWriter(verilogInfo, moduleName, rtlPath)
vwriter.writeVerilog()

# Write the Driver document
hwriterInfo = parser.htmlwriter()
dwriter = DriverWriter(hwriterInfo, moduleName, driPath)
dwriter.writeDriver()