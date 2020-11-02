#!/usr/bin/python
#########################################################################################
# Copyright 2020 by Heqing Huang (heqinghuangusc@gmail.com)
#
# Project: Simple CSR Generator
# Author: Heqing Huang
# Created: 10/22/2020
#
# Description:
#   This script takes the result from YmlParser and write the verilog module
#
#########################################################################################


from common import *

lines = lambda x: '\n' * x

class VerilogWriter(object):

    def __init__(self, verilogInfo, name, path):
        """
        Parameters:
            :param verilogInfo: the register info tuple
            :param name: the name of the register module
            :param path: the path of to the document
        """
        self.name       = name
        self.path       = path
        (self.portList,
         self.logics,
         self.regs,
         self.sw_rd_dec,
         self.sw_wr_dec,
         self.rd_assign_logic,
         self.wr_seq_logic,
         self.fifo_logic,
         self.addr_width
        ) = verilogInfo

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
        for port in self.portList:
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
        string += INDENT(1) + f'assign o_sw_rddata = o_sw_rddata{REG_SUFFIX};\n'
        for name in self.rd_assign_logic:
            if name.find('o_hw') != -1:
                string += INDENT(1) + f'assign {name} = {name}{REG_SUFFIX};\n'
        string += lines(2)
        FILE.write(string)

    def writeFIFO(self, FILE):
        """
        Assign the FIFO related signal
        """
        self.writeSplitter(FILE, 1, '// FIFO control\n')
        fifo_read = lines(1) + INDENT(1) + '// FIFO Read logic\n'
        fifo_write = lines(1)  + INDENT(1) + '// FIFO Write logic\n'

        # (addr, ctrl_signal, data_signal, type)
        for item in self.fifo_logic:
            (addr, ctrl_signal, data_signal, msb, lsb, type) = item
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
        string += INDENT(2) + f'if (i_sw_read) o_sw_rddata{REG_SUFFIX} <= o_sw_rddata_next;\n'
        string += INDENT(1) + 'end' + lines(2)

        # Combinational part
        string += INDENT(1) + '// read decode logic\n'
        string += INDENT(1) + 'always @(*) begin\n'
        string += INDENT(2) + f'o_sw_rddata_next = o_sw_rddata;\n'
        string += INDENT(2) + 'case(i_sw_address)\n'

        # readlogic => [[addr, field0, field1],
        for info in self.sw_rd_dec:
            addr  = format(info[1], 'x')
            line  = INDENT(3) + f'{self.addr_width}\'h{addr}:{INDENT(1)}o_sw_rddata_next = {{'
            for field in reversed(info[2:]): # Need to reverse it in the assignment
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
            addr = info[1]
            caseContent = ''
            for field in info[2:]:
                signal = field + WEN_SUFFIX
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
            field_reg = field + REG_SUFFIX
            width = msb - lsb + 1
            resetVal = str(width) + '\'h' + str(format(resetVal, 'x'))
            reset += INDENT(3) + f'{field_reg} <= {resetVal};\n'
            write += INDENT(3) + f"// Register: {reg} | Field: {field}\n"
            if hwr and swr:
                write += INDENT(3) + f'if ({field_reg}{WEN_SUFFIX}) {field_reg} <= i_sw_wrdata[{msb}:{lsb}];\n'
                write += INDENT(3) + f'else {field_reg} <= {field};\n\n'
            elif swr: # sw write only
                write += INDENT(3) + f'if ({field_reg}{WEN_SUFFIX}) {field_reg} <= i_sw_wrdata[{msb}:{lsb}];\n\n'
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
            :param FILE: File Stream
        """
        header  = '///////////////////////////////////////////////////////////////\n'
        header += '//\n'
        header += '// Generated by Simple CSR Generator\n'
        header += '//\n'
        header += f'// Name: {self.name}{RTL_SUFFIX}.v\n'
        header += f'// Date Created: {MONTH}/{DAY}/{YEAR} - {HOUR}:{MINUTE}\n'
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
