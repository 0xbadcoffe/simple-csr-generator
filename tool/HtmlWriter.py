#!/usr/bin/python
#########################################################################################
# Copyright 2020 by Heqing Huang (heqinghuangusc@gmail.com)
#
# Project: Simple CSR Generator
# Author: Heqing Huang
# Date: 10/22/2020
#
# Description:
#   This script takes the result from RegParser and write a HTML documentation
#
#########################################################################################

# Global Define
TOP     = 'register'
REGNAME = 0
FNAME   = 0
MSB     = 1
LSB     = 2
SWTYPE  = 3
HWTYPE  = 4
RESET   = 5
NOTE    = 6

INDENT1 = '  '
INDENT2 = INDENT1 * 2

class HtmlWriter(object):

    def __init__(self, regsInfo, name, path):
        """
        Parameters:
            :param regsInfo: the register info array for all register
            :param name: the name of the register module
            :param path: the path of to the document
        """
        self.regsInfo = regsInfo
        self.name = name
        self.path = path

    def htmlPrefix(self, FILE, name):
        """
        Write the header par of the HTML file
        Parameters:
            :param name: the name of the register module
            :param FILE: The file pointer
        """
        string  = '<!DOCTYPE html>\n'
        string += '<html lang="">\n'
        string += INDENT1 + '<head>\n'
        string += INDENT2 + f'<title>Register module for {name}</title>\n'
        string += INDENT1 + '</head>\n'
        string += INDENT1 + '<body>\n'
        FILE.write(string)

    def htmlsuffix(self, FILE):
        """
        Write the tail par of the HTML file
        Parameters:
            :param name: the name of the register module
            :param FILE: The file pointer
        """
        string  = INDENT1 + '</head>\n'
        string += '</html>\n'
        FILE.write(string)

    def tableHeader(self, name):
        """
        Write the header for a table
        Parameters:
            :param name: the name of the register
        """
        string  = INDENT2 + f'<h4>{name}</h4>\n'
        string += INDENT2 + '<table border="4">\n'
        string += INDENT1 + '<tr>\n'
        string += INDENT2 + '<td>Field</td>\n'
        string += INDENT2 + '<td>Range</td>\n'
        string += INDENT2 + '<td>Reset Value</td>\n'
        string += INDENT2 + '<td>SW Access Type</td>\n'
        string += INDENT2 + '<td>HW Access Type</td>\n'
        string += INDENT2 + '<td>Description</td>\n'
        string += INDENT1 + '</tr>\n'
        return string

    def OneFieldStr(self, fieldInfo) -> str:
        """
            Write HTML for one field.
            Returns a string of the content to be written

            Parameters:
                :param regInfo: the register info array for 1 register
        """
        string  = INDENT1 + '<tr>\n'
        string += INDENT2 + f'<td>{fieldInfo[FNAME]}</td>\n'
        string += INDENT2 + f'<td>{fieldInfo[MSB]} - {fieldInfo[LSB]}</td>\n'
        string += INDENT2 + f'<td>{fieldInfo[RESET]}</td>\n'
        string += INDENT2 + f'<td>{fieldInfo[SWTYPE]}</td>\n'
        string += INDENT2 + f'<td>{fieldInfo[HWTYPE]}</td>\n'
        string += INDENT2 + f'<td>{fieldInfo[NOTE]}</td>\n'
        string += INDENT1 + '</tr>\n'
        return string

    def OneRegStr(self, regInfo) -> str:
        """
            Write HTML for one register.
            Returns a string of the content to be written

            Parameters:
                :param regInfo: the register info array for 1 register
        """
        string = self.tableHeader(regInfo[REGNAME])
        for fieldInfo in regInfo[REGNAME+1:]:
            string += self.OneFieldStr(fieldInfo)
        string += INDENT2 + '</table>'
        return string

    def writeAllReg(self, FILE, regsInfo):
        """
            Write all the register.
            Parameters:
                :param FILE: The file pointer
                :param regsInfo: the register info array for all the register
        """
        for regInfo in regsInfo:
            FILE.write(self.OneRegStr(regInfo))

    def writeAll(self):
        """
            Write all the content.
        """
        fullpath = self.path + '/' + self.name + '.html'
        FILE = open(fullpath, "w")
        self.htmlPrefix(FILE, self.name)
        self.writeAllReg(FILE, self.regsInfo)
        self.htmlsuffix(FILE)
        FILE.close()


if __name__ == "__main__":
    regsInfo = [['pio_read', ['data', 31, 0, 'R', 'W', 0, 'pio read data']], ['pio_write', ['data', 31, 0, 'W', 'R', 0, 'pio write data']], ['pio_ctrl_status', ['edge_capture_en', 0, 0, 'W', 'R', 0, 'enable edge capturing'], ['RSVR', 1, 1, 'NA', 'NA', 0, 'Reserved Field'], ['edge_captured', 2, 2, 'R', 'W', 0, 'captured edge activity (if any)'], ['RSVR', 31, 3, 'NA', 'NA', 0, 'Reserved Field']]]
    path = '.'
    name = 'pio'

    hwriter = HtmlWriter(regsInfo, name, path)
    hwriter.writeAll()
