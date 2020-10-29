#!/usr/bin/python
#########################################################################################
# Copyright 2020 by Heqing Huang (heqinghuangusc@gmail.com)
#
# Project: Simple CSR Generator
# Author: Heqing Huang
# Created: 10/22/2020
#
# Description:
#   This is the parser for the register yml input. It read the yaml input and
#   create the internal format of the register representation.
#   It also calculated the address of the register and the bit range of the field
#
#########################################################################################

import yaml
from common import *
from config import *
from math import log2, ceil

getRegName = lambda x: x + REG_SUFFIX

class YmlParser(object):

    def __init__(self, yml):
        """
        Parse the yml file
        Parameters:
            :param name: the name of the register module
        """
        self.yml = yml
        # Overall register info, used by HTML Writer
        self.regsInfo = []
        # Detailed register info, used by Verilog Write
        self.portList = []  # IO port       => [(direction, width, name),]
        self.logics = []    # Logic signal  => [(name, width),]
        self.regs = []      # Reg signal    => [(name, width),]
        self.sw_rd_dec = [] # read decode   => [[reg, addr, field0, field1],]
        self.sw_wr_dec = [] # Write decode  =>  [[reg, addr, field0, field1],]
        self.rd_assign_logic = [] # read [name, ...]
        self.wr_seq_logic = []  # write  [(reg, field, reset, sw_write?, hw_write?, msb, lsb),]
        self.fifo_logic = []    # Logic signal for FIFO  => [(addr, ctrl_signal, data_signal, msb, lsb, type), ...]

    def openYml(self):
        """ Open the yml file """
        stream = open(self.yml, 'r')
        self.regInfoRaw = yaml.load(stream, Loader=yaml.FullLoader)['register']

    def getAllReg(self, regInfoRaw) -> list:
        """ Get all the registers defined in the yaml file """
        return list(regInfoRaw.keys())

    def getAllField(self, reg, regInfoRaw) -> list:
        """ Get all the fields defined in a register """
        self.fields = list(regInfoRaw[reg].keys())
        return self.fields

    def parseField(self, reg, addr, start, field, info, idx, last=False):
        """
        Parse one Field
        Parameter:
            :param: reg: register name
            :param: addr: register address
            :param: start bit of the field
            :param: field: field name
            :param: info: field information
            :param: index of the register
        Return:
            :size of the field
        """
        if field != RSVR:
            size   = info['size']
            reset  = info['reset']
            swtype = info['swtype']
            hwtype = info['hwtype']
            note   = info['note']
            msb = start + int(size) - 1
            lsb = start
            fieldLine = [field, msb, lsb,  swtype , hwtype, reset, note]
            # Register read/write
            if swtype == 'W' or swtype == 'R':
                dir = 'i' if hwtype == 'W' else 'o' # direction is based on hw type
                name = f'{dir}_hw_{reg}_{field}'    # IO name
                name_q = getRegName(name)           # Register name
                self.portList.append((dir, size, name))
                self.regs.append((name_q, size))
                self.sw_rd_dec[idx].append(name_q)
                if swtype == 'W':
                    self.logics.append((name_q + WEN_SUFFIX, 1))
                    self.sw_wr_dec[idx].append(name_q)
                if swtype == 'W' or hwtype == 'W':
                    self.wr_seq_logic.append((reg, name, reset, swtype == 'W',
                                              hwtype == 'W', msb, lsb))
                if hwtype == 'R':
                    self.rd_assign_logic.append(name)

            # FIFO read/write
            if swtype == 'FIFOR' or swtype == 'FIFOW':
                if swtype == 'FIFOR':
                    dir = 'i'
                    op  = 'read'
                if swtype == 'FIFOW':
                    dir = 'o'
                    op  = 'write'
                ctrl_signal = f'o_hw_{reg}_{field}_fifo_{op}'
                data_signal = f'{dir}_hw_{reg}_{field}_fifo_{op}_data'
                self.portList.append(('o', 1, ctrl_signal))
                self.portList.append((dir, size, data_signal))
                self.fifo_logic.append((addr, ctrl_signal, data_signal, msb, lsb, swtype))
                if swtype == 'FIFOR':
                    self.sw_rd_dec[idx].append(data_signal)
                if swtype == 'FIFOW':
                    self.sw_rd_dec[idx].append(f"{size}'h0")
        else:
            size = REG_WIDTH - start if last else info['size']
            self.sw_rd_dec[idx].append(f"{size}'b0")
            fieldLine = [RSVR, start + size -1, start,  'NA' , 'NA', 0x0 , RSVR_NOTE]
        return (size, fieldLine)

    def parseOneReg(self, reg, addr, regInfoRaw, idx):
        """
            Parser one register and extract all the information about this register
            For detailed register info, see __init__ function
        """
        fields = self.getAllField(reg, regInfoRaw)
        regInfo = regInfoRaw[reg]
        nextStart = 0
        regResult = []
        for field in fields:
            fieldInfo = regInfo[field]
            (size, fieldLine) = self.parseField(reg, addr, nextStart, field, fieldInfo, idx)
            regResult.append(fieldLine)
            nextStart += size;
        # deal with left-over bits
        if nextStart < REG_WIDTH:
            (size, fieldLine) = self.parseField(reg, addr, nextStart, RSVR, fieldInfo, idx, True)
            regResult.append(fieldLine)

        self.regsInfo.append((reg, addr, regResult))

    def prepend(self):
        """
        Prepend signals
        """
        self.portList.append(('i', 1, 'clk'))
        self.portList.append(('i', 1, 'reset'))
        self.portList.append(('i',self.addr_width,'i_sw_address')) # TODO
        self.portList.append(('i',1,'i_sw_read'))
        self.portList.append(('i',1,'i_sw_write'))
        self.portList.append(('i',1,'i_sw_select'))
        self.portList.append(('i',REG_WIDTH,'i_sw_wrdata'))
        self.portList.append(('o',REG_WIDTH,'o_sw_rddata'))
        self.logics.append(('o_sw_rddata_next', REG_WIDTH))
        self.regs.append(('o_sw_rddata' + REG_SUFFIX, REG_WIDTH))

    def parserAllReg(self):
        """Parse all the registers """

        self.openYml()
        regs = self.getAllReg(self.regInfoRaw)
        self.addr_width = ceil(log2(len(regs) * 4))
        self.prepend()
        addr = 0x0
        idx = 0
        for reg in regs:
            self.sw_rd_dec.append([reg, addr])
            self.sw_wr_dec.append([reg, addr])
            self.parseOneReg(reg, addr, self.regInfoRaw, idx)
            addr += 0x4
            idx += 1

    def htmlwriter(self):
        """Return information for htmlwriter"""
        return self.regsInfo

    def verilogwriter(self):
        """Return information for verilogwriter"""
        return (
            self.portList,
            self.logics,
            self.regs,
            self.sw_rd_dec,
            self.sw_wr_dec,
            self.rd_assign_logic,
            self.wr_seq_logic,
            self.fifo_logic,
            self.addr_width
        )
