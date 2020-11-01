# Supported Register Access Type

- [Supported Register Access Type](#supported-register-access-type)
  - [Software Access Type](#software-access-type)
  - [Hardware Access Type](#hardware-access-type)
  - [Supported Access type combination](#supported-access-type-combination)

Register access types are split into software side and hardware side. Software side is address based access and is usually accessed by the CPU. Hardware side is signal based and is usually accessed by hardware. Hardware side usually provides configuration for hardware or log the hardware status.

## Software Access Type

Simple CSR supports the following access type

1. **R (RO) - Read Only**
   - SW can only read this field , write to this field will be ignored.
   - When read, SW will read the entire register. Beware if read to a field have side effect.

2. **W (RW) - Write/Read**
   - SW can read or write to the field.
   - When read, SW will read the entire register. Beware if read to a field have side effect.    

3. **FIFOR - FIFO Read**
   - This field is connected to the read side of a FIFO, read to this field will return the data in the FIFO.
   - Write to this field will be ignored.
   - SW is responsible for making sure the FIFO is not empty when read. Reading from an empty FIFO will have undefined behavior depending on the FIFO implementation.
   - The FIFO needs to be a FWFT (First Word Fall Through) FIFO. 


4. **FIFOW - FIFO Write**
    - This field is connected to the write side of a FIFO, write to this field will write the data into the FIFO.
    - SW is responsible for making sure the FIFO is not full when write. Writing to a full FIFO will have undefined behavior depending on the FIFO implementation.
    - Read to this field will return zero.

## Hardware Access Type

Simple CSR supports the following HW access type

1. **R (RO) - Read Only, Status register/field**
   - Hardware logic can only read this field.

2. **W (WO) - Write Only, Control register/field**
   - hardware logic can only write to this field.

## Supported Access type combination

|  SW   |  HW  | Comment          |
| :---: | :--: | ---------------- |
|   R   |  W   | Status Register  |
|   W   |  R   | Control Register |
| FIFOR |  -   | Read from FIFO   |
| FIFOW |  -   | Write to FIFO    |

Other combinations are either not supported or do not match any valid use case.