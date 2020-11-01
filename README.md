# Simple CSR Generator

- [Simple CSR Generator](#simple-csr-generator)
  - [Introduction](#introduction)
  - [Getting Started](#getting-started)
  - [Specification](#specification)
  - [Future work](#future-work)
  - [Change Log](#change-log)
  - [License](#license)

## Introduction

Simple CSR Generator: A simple **C**onfiguration **S**tatus **R**egister (CSR) generator

It takes the register information coded in yaml file and generates the following collateral:

1. Verilog module
2. HTML based documentation
3. C header file defining register address and field information

### Current Version

Ver 1.3

## Getting Started

### Usage

- Run with Default setting. Output is in the same directory of the yaml file. See [Register Define File Format](#register-define-file-format) section to learn how to write the yml file

```shell
./simple-csr-generator <your-yml-file>
```

- Run with an non-default output directory

```shell
./simple-csr-generator <your-yml-file> -outdir <your-output-directory>
```

### Run the example

```shell
rm -rf example/pio_csr
./simple-csr-generator example/pio.yml
```

### Output

After running the command under [Run the example](#run-the-example) section, you will get the following output

```other
example
├── pio_csr                 - the output directory
│   ├── doc
│   │   └── pio_csr.html    - html document
│   ├── driver
│   │   └── pio_csr.h       - C driver code
│   └── rtl
│       └── pio_csr.v       - rtl file
└── pio.yml                 - the input yaml file
```

## Specification

Ver 1.3 current supports the following feature

- **Register width**
  - Register width is fixed to 32 bits.

- **Address scheme**
  - The input address is byte address and should always align to 4 bytes boundary (lower two bits being zero).
  - CSR module does NOT check address alignment. It's the user's responsibility to input correct address. Wrong address alignment will cause error.

- **Supported Register Access Type**
  - SW: R(RO), W(RW), FIFOR, FIFOW
  - HW: R(RO), W(WO)
  - For more details, please check this doc: [Supported Register Access Type](doc/supported_register_access_type.md)

- **Register spec format**
  - Please check this doc for the register spec: [Register Specification Format](doc/register_spec_format.md)

- **Output Files**
  - Please check this doc for output files: [Output Files](doc/output_file.md)

## Future work

- [ ] Add some basic error checking on the input yaml file
  - Access type combo correct?
  - Reset value can be hold within the field?
  - Register size greater than 32?
- [ ] Add more configuration
- [ ] Add support for HW RW access type
- [ ] Add support for HW logging and SW write clear

## Change Log

[Change log](doc/change_log.md)

## License

This project is under MIT License.

Copyright (c) 2020 Heqing Huang
