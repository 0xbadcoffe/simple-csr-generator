# Simple CSR Generator

A simple **C**onfiguration **S**tatus **R**egister (CSR) generator

## Introduction

This is a small tool to generate verilog CSR module. It takes the register information coded in yaml file and generates verilog module, and a HTML based document.

## Usage

TBD

## Supported Feature in version 1.0

1. The register width is fixed to 32 bits (4 bytes). The actual hardware implementation may not use the 32 bits depending on the field.
2. The address is byte addressable and always aligned to 4 bytes boundary.
3. SW access to the register is always 32 bit meaning SW always read or write to the entire 32 bit. Field access is not supported yet.
4. For simplicity, all the registers are SW accessible but user can define if it's RW (read-write) or RO (read-only).

## Input Format

The register information are written manually in the yaml. Here is the format.

### Format

```yml
register:
    <register_1>:                       # Register name
            <field1>:                   # Field 1 name
                size: <size>            # Size of the field
                reset: <reset_value>    # Reset value.
                swtype: <R|W>           # SW access type, can be R or W
                hwtype: <R|W>           # HW access type, can be R or W
                note: <description of the field>
            <field2>:
                size: <>
                ...
            ...
    <register_2>:
            <field1>:
                size: <>
                ...
            RSVR:
                size: <>
            <field2>:
                size: <>
                ...
            ...
```

### Note

- The address of the registers are calculated automatically based on the order they are defined in the yaml files.
  In the example below, pio_read_data is 0, pio_write_data is 4, pio_status is 8.
- The field location is calculated automatically based on the field width. Since register width is fixed to 32 bit, unused bits will be treated as reserved and each register can't have more thant 32 bit
- SW access type can be *R* or *W*. *R* means read only, writing to the the *R* field has no effect. *W* means write-able field. SW read to the register will automatically return the entire register value, regardless of the SW access type.
- HW access type can be *R* or *W*. *R* means this field is used for configuration. *W* means this field is used for reporting status.
- **RSVR** keyword is indicate this field is reserved.

### Example

Register definition for PIO: pio.yml

```yml
register:
    pio_read:
        data:
            size:32
            reset: 0x0
            swtype:R
            hwtype:W
    pio_write:
        data:
            size:32
            reset:      # tool will infer zero for the reset value
            swtype:W
            hwtype:R
    pio_ctrl_status:
        edge_capture_en:
            size:1
            reset: 0x0
            swtype:W
            hwtype:R
        RSVR:
            size:15
        edge_captured:
            size:1
            reset: 0x0
            swtype:R
            hwtype:W
```

## Output Verilog Module

The verilog module support 2 main interface: SW interface and HW interface.

- The SW interface is the address based or memory mapped interface. It performs read and write operation to the internal register.
- The HW interface provides the configuration value for the hardware logic and register the hardware status.

### SW interface

```verilog
input  [ADDR_WIDTH-1:0]     i_sw_address    // address, ADDR_WIDTH: Address width
input                       i_sw_read       // read access
input                       i_sw_write      // write access
input                       i_sw_select     // select this CSR module
input  [DATA_WIDTH-1:0]     i_sw_wrdata     // input write data
output [DATA_WIDTH-1:0]     o_sw_rddata     // output read data
```

Note:
- `sw_read` and `sw_write` can not be asserted at the same clock cycle

### HW interface

```verilog
input  [WIDTH-1:0]          i_hw_<register_name>_<field_name>   // input status 
output [WIDTH-1:0]          o_hw_<register_name>_<field_name>   // output configuration
...
```

### Other signals

```verilog
input                       clk         // clock signal
input                       reset       // reset signal
```

### TBD Feature

- [ ] Adde some basic error checking on the input yaml file