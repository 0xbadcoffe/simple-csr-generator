#!/usr/bin/python
#########################################################################################
# Copyright 2020 by Heqing Huang (heqinghuangusc@gmail.com)
#
# Project: Simple CSR Generator
# Author: Heqing Huang
# Created: 10/22/2020
#
# Description:
#   Common variable and function
#
#########################################################################################

############################
# Created
############################
from datetime import datetime
YEAR = datetime.now().year
MONTH = datetime.now().month
DAY = datetime.now().day
HOUR = datetime.now().hour
MINUTE = datetime.now().minute

############################
# Global Define
############################

# Other global define
RSVR        = 'RSVR'
RSVR_NOTE   = 'Reserved Field'

RTL_SUFFIX = '_csr'
REG_SUFFIX = '_q'
WEN_SUFFIX = '_wen'

LINE_LIMIT = 100

############################
# Global Function
############################
INDENT = lambda x: '  ' * x

def addSpace(string, maxlen = 10, end=True):
    """
    Add space to the string to make it align
    parameter:
        :param maxlen: the max length after adding the space.
                       If the string is longer then an INDENT is added
        :param end: if True, add the space at the end, else add the space at the front
    """
    lens = len(string)
    if end:
        return string + ' ' * (maxlen - lens) if lens < maxlen else string + INDENT(1)
    else:
        return ' ' * (maxlen - lens) + string if lens < maxlen else INDENT(1) + string



