# =================================================================
# Makefile for running iverilog flow
# Author: Heqing Huang
# Date Created: 10/10/2020
#
# Need to setup the following variable from the source makefile
#
# 	SRC_PATH	: RTL source directories
# 	TOP_DESIGN	: Top level rtl module name
# 	TOP_FILE 	: Top level rtl file
#
# =================================================================

VEXT = .v
TOP_DESIGN = $(TOP)
TOP_FILE   = $(TOP_DESIGN)$(VEXT)


# =============================
# Tool Variable
# =============================
IVERILOG 	= iverilog
VVP 		= vvp
GTKWAVE 	= gtkwave
VERILATOR	= verilator

# =============================
# Variable
# =============================

ALL_SRC_FILES = $(shell find $(SRC_PATH) -type f)
RTL_OUT		  = $(TOP_DESIGN)

# =============================
# Command
# =============================

.PHONY: clean help wave run tb rtl lint clean

help:
	@echo 	"Usage: "
	@echo	"make help 	            - print this message"
	@echo	"make rtl TOP=<top> 	- compile rtl"
	@echo   "make clean	TOP=<top>   - clean all the output"
	@echo	"make lint TOP=<top>	- lint the design using verilator"

$(TB_OUT): $(TB_TOP) $(TOP_FILE) $(ALL_SRC_FILES)
	$(IVERILOG) -o $(TB_OUT) $(TB_TOP) -y $(SRC_PATH)

rtl: $(RTL_OUT)

$(RTL_OUT):	$(TOP_FILE) $(ALL_SRC_FILES)
	$(IVERILOG) -o $(RTL_OUT) $(TOP_FILE)

lint:
	@verilator  -Wall -lint-only $(TOP_FILE)
	@echo "No Issue Found"

clean:
	rm -rf $(RTL_OUT) *.out *.vcd