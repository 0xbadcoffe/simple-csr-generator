#!/usr/bin/python
#########################################################################################
# Copyright 2020 by Heqing Huang (heqinghuangusc@gmail.com)
#
# Project: Simple CSR Generator
# Author: Heqing Huang
# Date: 10/22/2020
#
# Description:
#   This script takes the result from RegParser and write the verilog module
#
#########################################################################################


from common import *
from math import log2, ceil

reg_suffix = '_q'
wen_suffix = '_wen'
lines = lambda x: '\n' * x

class VerilogWriter(object):

    def __init__(self, regsInfo, name, path):
        """
        Parameters:
            :param regsInfo: the register info array for all register
            :param name: the name of the register module
            :param path: the path of to the document
        """
        self.regsInfo   = regsInfo
        self.name       = name
        self.path       = path
        self.addr_width = ceil(log2(len(regsInfo) * 4))
        self.portList   = [] # [[direction, width, name], ...]
        self.logics     = [] # [[name, width], ...]
        self.regs       = [] # [[name, width], ...]
        self.sw_rd_dec  = [] # [[addr, [field0, field1, field2, ...]], ...]
        self.sw_wr_dec  = []  # [[addr, [field0, field1, ...]]] the field is sw write only field
        self.wr_seq_logic = [] # [[reg, field, reset, sw_write?, hw_write?, msb, lsb]]
        self.fifo_portList = [] # [[direction, width, name], ...]
        self.fifo_logic = [] # [[addr, [ctrl_signal, data_signal, msb, lsb, type]], ...]

    def parseRegInfo(self):
        """
            Parse the  register information array and generate needed information
        """
        # Predefined prot list
        self.portList  = [['i', 1, 'clk'],['i', 1, 'reset']]
        self.portList += [['i',self.addr_width,'i_sw_address'],
                     ['i',1,'i_sw_read'],   ['i',1,'i_sw_write'],
                     ['i',1,'i_sw_select'], ['i',REG_WIDTH,'i_sw_wrdata'],
                     ['o',REG_WIDTH,'o_sw_rddata']]
        self.logics = [['o_sw_rddata_next', REG_WIDTH]]
        self.regs = [['o_sw_rddata' + reg_suffix, REG_WIDTH]]
        for regInfo in self.regsInfo:
            regName = regInfo[0]
            addr = regInfo[1]
            sw_rd_dec = []
            sw_wr_dec = []
            wr_seq_logic = []
            fifo_logic = []
            for fieldInfo in regInfo[2:]:
                # Extract the field
                fieldName = fieldInfo[FNAME]
                hwtype = fieldInfo[HWTYPE]
                swtype = fieldInfo[SWTYPE]
                lsb = fieldInfo[LSB]
                msb = fieldInfo[MSB]
                reset = fieldInfo[RESET]
                width = msb - lsb + 1

                if fieldName != RSVR:
                    # regular read/write
                    if swtype == 'W' or swtype == 'R':
                        dir = 'i' if hwtype == 'W' else 'o'
                        name = dir + '_hw_' + regName + '_' + fieldName
                        name_q = name + reg_suffix
                        self.portList.append([dir, width, name])
                        self.regs.append([name_q, width])
                        sw_rd_dec.append(name_q)
                        if swtype == 'W':
                            sw_wr_dec.append(name_q)
                            self.logics.append([name_q + wen_suffix, 1])
                        if swtype == 'W' or hwtype == 'W':
                            wr_seq_logic.append([regName, name, reset, swtype == 'W', hwtype == 'W', msb, lsb])
                    # FIFO read/write
                    if swtype == 'FIFOR' or swtype == 'FIFOW':
                        if swtype == 'FIFOR':
                            dir = 'i'
                            op  = 'read'
                        if swtype == 'FIFOW':
                            dir = 'o'
                            op  = 'write'
                        ctrl_signal = f'o_hw_{regName}_{fieldName}_fifo_{op}'
                        data_signal = f'{dir}_hw_{regName}_{fieldName}_fifo_{op}_data'
                        self.fifo_portList.append(['o', 1, ctrl_signal])
                        self.fifo_portList.append([dir, width, data_signal])
                        fifo_logic.append([ctrl_signal, data_signal, msb, lsb, swtype])
                        if swtype == 'FIFOR':
                            sw_rd_dec.append(data_signal)
                        if swtype == 'FIFOW':
                            sw_rd_dec.append(f'{width}\'h0')
                else:
                    sw_rd_dec.append(f"{width}'b0")
            self.sw_rd_dec.append([addr, sw_rd_dec])
            self.sw_wr_dec.append([addr, sw_wr_dec])
            self.wr_seq_logic += wr_seq_logic
            self.fifo_logic.append([addr, fifo_logic])

    def writeSplitter(self, FILE, indent, line, sign='=', width=30):
        """ """
        string  = INDENT(indent) + '//'+ sign * width + '\n'
        string += INDENT(indent) + line
        string += INDENT(indent) + '//' + sign * width + '\n'
        FILE.write(string)


    def writePort(self, FILE):
        """
        Write the verilog IO ports
        parameter:
            :param portList: the IO port list
            :param FILE: File Stream
        """
        string = '(\n'
        for port in self.portList + self.fifo_portList:
            (dir, width, name) = port
            dir = 'input ' if dir == 'i' else 'output'
            addrRange = f'[{width - 1}:0]' if width > 1 else ''
            string += INDENT(1) + addSpace(dir, 7) + addSpace(addrRange, 10) + name + ',\n'
        string = string[:-2] + '\n' '' # get rid of the last ','
        string += ');\n' + lines(2)
        FILE.write(string)

    def writeDeclare(self, FILE):
        """
        Write the verilog signal declaration
        parameter:
            :param portList: the IO port list
            :param FILE: File Stream
        """
        string = INDENT(1) + '// register definition\n'
        for reg in self.regs:
            (name, width) = reg
            addrRange = f'[{width - 1}:0]' if width > 1 else ''
            string += INDENT(1) + addSpace('reg', 7) + addSpace(addrRange, 10) + name + ';\n'
        string += '\n'
        string += INDENT(1) + '// reg type variable definition\n'
        for logic in self.logics:
            (name, width) = logic
            addrRange = f'[{width - 1}:0]' if width > 1 else ''
            string += INDENT(1) + addSpace('reg', 7) + addSpace(addrRange, 10) + name + ';\n'
        string += lines(2)
        FILE.write(string)

    def writeHWRead(self, FILE):
        """
        Assign the hw output with the internal register
        """
        self.writeSplitter(FILE, 1, '// HW Read output\n')
        string  = lines(1)
        string += INDENT(1) + f'assign o_sw_rddata = o_sw_rddata{reg_suffix};\n'
        for info in self.portList:
            (_, __, name) = info
            if name.find('o_hw') != -1:
                string += INDENT(1) + f'assign {name} = {name}{reg_suffix};\n'
        string += lines(2)
        FILE.write(string)

    def writeFIFO(self, FILE):
        """
        Assign the FIFO related signal
        """
        self.writeSplitter(FILE, 1, '// FIFO control\n')
        fifo_read = lines(1) + INDENT(1) + '// FIFO Read logic\n'
        fifo_write = lines(1)  + INDENT(1) + '// FIFO Write logic\n'

        # [addr, [ctrl_signal, data_signal, type]]
        for info in self.fifo_logic:
            addr = info[0]
            for item in info[1]:
                (ctrl_signal, data_signal, msb, lsb, type) = item
                if type == 'FIFOR':
                    fifo_read += INDENT(1) + f'assign {ctrl_signal} = i_sw_select & i_sw_read & '
                    fifo_read += f"(i_sw_address == {self.addr_width}'h{format(addr, 'x')});\n"
                if type == 'FIFOW':
                    fifo_write += INDENT(1) + f'assign {ctrl_signal} = i_sw_select & i_sw_write & '
                    fifo_write += f"(i_sw_address == {self.addr_width}'h{format(addr, 'x')});\n"
                    fifo_write += INDENT(1) + f'assign {data_signal} = i_sw_wrdata[{msb}:{lsb}];\n'
        # end part
        fifo_write += lines(2)
        FILE.write(fifo_read)
        FILE.write(fifo_write)

    def writeReadLogic(self, FILE):
        """ Write the read logic """
        # Sequential part
        self.writeSplitter(FILE, 1, '// Software Read Logic\n')
        string  = lines(1)
        string += INDENT(1) + 'always @(posedge clk) begin\n'
        string += INDENT(2) + f'if (i_sw_read) o_sw_rddata{reg_suffix} <= o_sw_rddata_next;\n'
        string += INDENT(1) + 'end' + lines(2)

        # Combinational part
        string += INDENT(1) + '// read decode logic\n'
        string += INDENT(1) + 'always @(*) begin\n'
        string += INDENT(2) + f'o_sw_rddata_next = o_sw_rddata;\n'
        string += INDENT(2) + 'case(i_sw_address)\n'

        # readlogic => [[addr, [field0, field1, field2, ...]], ...]
        for info in self.sw_rd_dec:
            addr  = format(info[0], 'x')
            line  = INDENT(3) + f'{self.addr_width}\'h{addr}:{INDENT(1)}o_sw_rddata_next = {{'
            for field in reversed(info[1]): # Need to reverse it in the assignment
                # breaks the line if it's too long
                if (len(line) > LINE_LIMIT - len(field)):
                    line += '\n ' + ' ' * line.find('{')
                line += f'{field}, '
            string += line[:-2] + '};\n' # get rid of the last ','
        string += INDENT(3) + f'default:{INDENT(1)}o_sw_rddata_next = o_sw_rddata;\n'
        string += INDENT(2) + 'endcase\n'
        string += INDENT(1) + 'end' + lines(2)

        # end part
        string += lines(2)
        FILE.write(string)

    def writeWriteLogic(self, FILE):
        """
        Write the write logic
        Possible SW and HW combination supported
        HW W, SW W
        HW R, SW W
        """
        #=====================
        # sw decode logic
        #=====================
        decDefault = '' # default assignment
        decCase = ''    # stuff inside case statement
        # [[addr, [field0, field1, ...]]] the field is sw write only field
        for info in self.sw_wr_dec:
            addr = info[0]
            caseContent = ''
            for field in info[1]:
                signal = field + wen_suffix
                decDefault += INDENT(4) + signal + ' = 1\'b0;\n'
                caseContent += INDENT(4) + signal + ' = i_sw_write & i_sw_select;\n'
            if info[1]:
                decCase += INDENT(3) + str(self.addr_width) + '\'h' + str(format(addr, 'x')) + ': begin\n'
                decCase += caseContent
                decCase += INDENT(3) + 'end\n'
        self.writeSplitter(FILE, 1, '// Software/Hardware Write Logic\n')
        decode  = lines(1)
        decode += INDENT(1) + '// software write decode Logic\n'
        decode += INDENT(1) + 'always @(*) begin\n'
        decode += decDefault
        decode += INDENT(2) + 'case(i_sw_address)\n'
        decode += decCase
        decode += INDENT(3) + 'default: begin\n'
        decode += decDefault
        decode += INDENT(3) + 'end\n'
        decode += INDENT(2) + 'endcase\n'
        decode += INDENT(1) + 'end\n'
        decode += lines(1)

        #=============================
        # sequential write logic
        #=============================

        reset = ''
        write = ''
        for info in self.wr_seq_logic: # [[regName, field, reset, sw_write?, hw_write?, msb, lsb]]
            (reg, field, resetVal, swr, hwr, msb, lsb) = info
            field_reg = field + reg_suffix
            width = msb - lsb + 1
            resetVal = str(width) + '\'h' + str(format(resetVal, 'x'))
            reset += INDENT(3) + f'{field_reg} <= {resetVal};\n'
            write += INDENT(3) + f"// Register: {reg} | Field: {field}\n"
            if hwr and swr:
                write += INDENT(3) + f'if ({field_reg}{wen_suffix}) {field_reg} <= i_sw_wrdata[{msb}:{lsb}];\n'
                write += INDENT(3) + f'else {field_reg} <= {field};\n\n'
            elif swr: # sw write only
                write += INDENT(3) + f'if ({field_reg}{wen_suffix}) {field_reg} <= i_sw_wrdata[{msb}:{lsb}];\n\n'
            else: # hw write only
                write += INDENT(3) + f'{field_reg} <= {field};\n\n'

        sequential  = lines(1)
        sequential += INDENT(1) + '// write sequential Logic\n'
        sequential += INDENT(1) + '// Software/Hardware Write Logic\n'
        sequential += INDENT(1) + 'always @(posedge clk) begin\n'
        sequential += INDENT(2) + 'if (reset) begin\n'
        sequential += reset
        sequential += INDENT(2) + 'end\n'
        sequential += INDENT(2) + 'else begin\n'
        sequential += write
        sequential += INDENT(2) + 'end\n'
        sequential += INDENT(1) + 'end\n'
        sequential += lines(1)

        # end part
        #string += lines(2)
        FILE.write(decode)
        FILE.write(sequential)

    def writeHeader(self, FILE):
        """
        Create the header string
        parameter:
            :param FILE: File Stream
        """
        header  = '///////////////////////////////////////////////////////////////\n'
        header += '//\n'
        header += '// Generated by Simple CSR Generator\n'
        header += '//\n'
        header += f'// Name: {self.name}{RTL_SUFFIX}.v\n'
        header += f'// Date: Date: {MONTH}/{DAY}/{YEAR} - {HOUR}:{MINUTE}\n'
        header += '//\n'
        header += '// Description:\n'
        header += f'//  CSR module for {self.name}\n'
        header += '//\n'
        header += '///////////////////////////////////////////////////////////////\n\n\n'
        FILE.write(header)

    def writeVerilog(self):
        """
        Write the verilog File
        """
        self.parseRegInfo()
        fullpath = self.path + '/' + self.name + f'{RTL_SUFFIX}.v'
        FILE = open(fullpath, "w")
        # Header
        self.writeHeader(FILE)
        # Module and IO port
        FILE.write(f'module {self.name}{RTL_SUFFIX}\n')
        self.writePort(FILE)
        self.writeDeclare(FILE)
        self.writeHWRead(FILE)
        self.writeReadLogic(FILE)
        self.writeWriteLogic(FILE)
        self.writeFIFO(FILE)
        FILE.write('endmodule\n')


if __name__ == "__main__":
    regsInfo = [['pio_read', 0, ['data', 31, 0, 'R', 'W', 0, 'pio read data']], ['pio_write', 4, ['data', 31, 0, 'W', 'R', 0, 'pio write data']], ['pio_ctrl_status', 8, ['edge_capture_en', 0, 0, 'W', 'R', 0, 'enable edge capturing'], ['RSVR', 1, 1, 'NA', 'NA', 0, 'Reserved Field'], ['edge_captured', 2, 2, 'R', 'W', 0, 'captured edge activity (if any)'], ['RSVR', 31, 3, 'NA', 'NA', 0, 'Reserved Field']]]
    path = '.'
    name = 'pio'
    vwriter = VerilogWriter(regsInfo, name, path)
    vwriter.writeVerilog()
