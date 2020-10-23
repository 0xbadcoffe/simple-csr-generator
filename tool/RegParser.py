#!/usr/bin/python
#########################################################################################
# Copyright 2020 by Heqing Huang (heqinghuangusc@gmail.com)
#
# Project: Simple CSR Generator
# Author: Heqing Huang
# Date: 10/22/2020
#
# Description:
#   This is the parser for the register yml input. It read the yaml input and
#   create the internal format of the register representation.
#   It also calculated the address of the register and the bit range of the field
#
#   The internal format output by the reg parser is a list structure
#
#   [[reg1,
#       [field1, MSb, LSb, SW_TYPE, HW_TYPE, Reset_value, Description(note)],
#       [field2, MSb, LSb, SW_TYPE, HW_TYPE, Reset_value, Description(note)],
#       ...
#    ],
#    [reg2,
#       [field1, MSb, LSb, SW_TYPE, HW_TYPE, Reset_value, Description(note)]
#       [field2, MSb, LSb, SW_TYPE, HW_TYPE, Reset_value, Description(note)]
#       ...
#    ],
#    ...
#   ]
#
#########################################################################################

import yaml

# Defines the key of the yml file
TOP     = 'register'
SIZE    = 'size'
RESET   = 'reset'
SWTYPE  = 'swtype'
HWTYPE  = 'hwtype'
NOTE    = 'note'

# Other golbal define
RSVR    = 'RSVR'
RSVR_NOTE = 'Reserved Field'
REG_WIDTH   = 32

class RegParser(object):

    def __init__(self, yml):
        """ Takes the yaml file """
        self.yml = yml

    def openYml(self):
        """ Open the yml file """
        stream = open(self.yml, 'r')
        self.regInfoRaw = yaml.load(stream, Loader=yaml.FullLoader)[TOP]

    def getAllReg(self, regInfoRaw) -> list:
        """ Get all the registers defined in the yaml file """
        return list(regInfoRaw.keys())

    def getAllField(self, reg, regInfoRaw) -> list:
        """ Get all the fields defined in a register """
        self.fields = list(regInfoRaw[reg].keys())
        return self.fields

    def parseOneReg(self, reg, regInfoRaw) -> list:
        """
            Parser one register and extract all the information about this register
            The output format is as follow:
            [reg1,
               [field1, MSb, LSb, SW_TYPE, HW_TYPE, Reset_value, Description(note)],
               [field2, MSb, LSb, SW_TYPE, HW_TYPE, Reset_value, Description(note)],
               ...
            ]
        """
        regResult = [reg]
        fields = self.getAllField(reg, regInfoRaw)
        regInfo = regInfoRaw[reg]
        bit = 0
        for field in fields:
            fieldInfo = regInfo[field]
            if field == RSVR:
                fieldLine = [RSVR, bit + size -1, bit,  'NA' , 'NA', 0x0 , RSVR_NOTE]
            else:
                size    = fieldInfo[SIZE]
                reset   = fieldInfo[RESET]
                swtype  = fieldInfo[SWTYPE]
                hwtype  = fieldInfo[HWTYPE]
                note    = fieldInfo[NOTE]
                fieldLine = [field, bit + size -1, bit, swtype, hwtype, reset, note]
            regResult.append(fieldLine)
            bit += size;
        if bit < REG_WIDTH:
            fieldLine = [RSVR, REG_WIDTH-1, bit, 'NA' , 'NA', 0x0, RSVR_NOTE]
            regResult.append(fieldLine)
        return regResult

    def parserAllReg(self):
        """Parse all the registers """
        regsInfo = []
        self.openYml()
        regs = self.getAllReg(self.regInfoRaw)
        for reg in regs:
            regsInfo.append(self.parseOneReg(reg, self.regInfoRaw))
        return regsInfo


if __name__ == "__main__":
    yml = 'pio.yml'
    parser = RegParser(yml)
    print(parser.parserAllReg())