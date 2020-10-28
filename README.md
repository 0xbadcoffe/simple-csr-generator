# Simple CSR Generator

- [Simple CSR Generator](#simple-csr-generator)
  - [Introduction](#introduction)
  - [Getting Started](#getting-started)
  - [Supported Feature](#supported-feature)
  - [Access Type](#access-type)
  - [Register Define File Format](#register-define-file-format)
  - [Output Verilog Module](#output-verilog-module)
  - [Limitation](#limitation)
  - [Change Log](#change-log)
  - [License](#license)

## Introduction

Simple CSR Generator: A simple **C**onfiguration **S**tatus **R**egister (CSR) generator

This is a small python based tool to generate verilog CSR module.

It takes the register information coded in yaml file and generates verilog module, and a HTML based document.



### Current Version

Ver 1.1



## Getting Started

### Usage

- Run with Default setting. Output is in the same directory of the yaml file. See [Register Define File Format](#register-define-file-format) section to learn how to write the yml file

```shell
$ ./simple-csr-generator <your-yml-file>
```

- Run with an non-default output directory

```shell
$ ./simple-csr-generator <your-yml-file> -outdir <your-output-directory>
```

### Run the example

```shell
$ ./simple-csr-generator example/pio.yml
```

### Output

The script will generate two output files: a RTL file and a HTML based document.

After running the command under [Run the example](#run-the-example) section, you will get the following
```
example
├── pio_csr                 - the output directory
│   ├── doc
│   │   └── pio_csr.html    - html document
│   └── rtl
│       └── pio_csr.v       - rtl file
└── pio.yml                 - the input yaml file
```



## Supported Feature

Ver 1.1 current support the following feature (or you may want to call some of them limitation)

1. **Register width** Register width is fixed to 32 bits for Ver 1.1.

2. **Address** 
   1. The input address is byte address and should always align to 4 bytes boundary (lower two bits being zero). 
   2. CSR module does NOT check address alignment. It's the user's responsibility to input correct address. Wrong address alignment will cause error.

3. **SW access**
   2. SW always read or write to the entire register.
      1. When read, CSR will return the value for the whole register regardless of the access type of the field.
      2. When write, CSR will write to the entire register, however, only field with W access type will have their value updated. R-only field will ignore the write value
      3. Field access is not supported yet. If you want to write to a specific field, you can do a read-modified-write. (unless there is a side effect to read a field but we don't have this feature right now)

4. **HW access**
   2. For W type field, the hardware is responsible for driving the correct value to CSR all the time, register value will be updated to the value driven by HW at every clock




## Access Type

### Software Access Type

CSR supports the following access type

1. **R - Read Only** SW can only read this field , write to this field will be ignored.

2. **W - Write/Read** SW can read or write to the field.

3. **FIFOR - FIFO Read** This field is connected to a FIFO, read to this field will return the data in the FIFO.

    - The FIFO needs to be a FWFT (First Word Fall Through) FIFO. 
    - SW is responsible for making sure the FIFO is not empty when read. Reading from an empty FIFO will have undefined behavior depending on the FIFO implementation.
    - Write to this field will be ignored

4. **FIFOW - FIFO Write** This field is connected to a FIFO, write to this field will write the data into the FIFO

    - SW is responsible for making sure the FIFO is not full when write. Writing to a full FIFO will have undefined behavior depending on the FIFO implementation.

    - Read to this field will return zero

### Hardware Access Type

CSR supports the following HW access type

1. **R - Read Only** (status register/field) means hardware logic can only read this field.
2. **W - Write Only** (control register/field) means hardware logic can only write to this field. (HW can NOT read the field)
3. Both R and W are not supported yet  for HW in Ver 1.1

### Supported access type combination

|  SW   |  HW  | Comment          |
| :---: | :--: | ---------------- |
|   R   |  W   | Status Register  |
|   W   |  R   | Control Register |
| FIFOR |  -   | Read from FIFO   |
| FIFOW |  -   | Write to FIFO    |



## Register Define File Format

The register define file is written in the yaml. Here is the format and rules

### Format

```yml
register:
    <register_1>:                               # Register name
            <field1>:                               # Field 1 name in register_1
                size: <size>                        # Size of the field
                reset: <reset_value>                # Reset value.
                swtype: <R|W>                       # SW access type, can be R or W
                hwtype: <R|W>                       # HW access type, can be R or W
                note: <description of the field>
            <field2>:
                size:
                ...
            ...
    <register_2>:
            <field1>:
                size:
                ...
            RSVR:
                size:
            <field2>:
                size:
                ...
            ...
```

### Note

- The address of the registers are calculated automatically based on the order they are defined in the yaml files.
- The field location is calculated automatically based on the field width.
- **RSVR** field is indicate this field is not used and reserved. Read to **RSVR** will return 0, write to **RSVR** will be ignored
- Since register width is fixed to 32 bit, unused bits will be treated as reserved and each register can not have more thant 32 bit.
- See [Supported Feature](#supported-feature) for information about access type.

### Example

Register definition for PIO: pio.yml

```yml
register:
  pio_read:
    data:
      size: 32
      reset: 0x0
      swtype: R
      hwtype: W
      note: pio read data
  pio_write:
      data:
          size: 32
          reset: 0xdeadbeef
          swtype: W
          hwtype: R
          note: pio write data
  pio_ctrl_status:
      level_capture_en:
          size: 1
          reset: 0x1
          swtype: W
          hwtype: R
          note: enable level capturing
      RSVR:
          size: 15
      level_captured:
          size: 1
          reset: 0x0
          swtype: R
          hwtype: W
          note: level edge activity (if any)
      sample:
          size: 14
          reset: 0xab
          swtype: W
          hwtype: W
          note: a sample field
```

## Output Verilog Module

The verilog module support 2 main interface: SW interface and HW interface.

- The SW interface is the address based or memory mapped interface. It performs read and write operation to the internal register.
- The HW interface provides the configuration value for the hardware logic and records the hardware status.

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
input  [WIDTH-1:0]          i_hw_<register_name>_<field_name>   // Status Register
output [WIDTH-1:0]          o_hw_<register_name>_<field_name>   // Configuration Register
...
```

### Other signals

```verilog
input                       clk         // clock signal
input                       reset       // reset signal
```

## Limitation

1. **No error checking in the input yml file**
2. **CSR module does not checks any error.**  
   Possible error includes: unaligned address, access to non existing register


### Future work

- [ ] Add some basic error checking on the input yaml file
  - Access type combo correct?
  - Reset value can be hold within the field?
  - Register size greater than 32?
- [ ] Add support for HW RW access type
- [ ] Add support for HW logging and SW write clear
- [ ] Register the input  request signal for better timing? - should be an optional feature



## Change Log

- 10/27/2020 - version (Ver 1.1) 
    1. Added new SW access type: FIFOR and FIFOW.

- 10/24/2020 - Inital version (Ver 1.0) Created



## License

This project is under MIT License.

Copyright (c) 2020 Heqing Huang
