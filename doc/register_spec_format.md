# Register Specification Format

- [Register Specification Format](#register-specification-format)
  - [Format](#format)
  - [Notes](#notes)
  - [Example](#example)

The register specification is written in yaml file. Here is the format and rules.

## Format

The yaml file is composed of register, field, and field information

```yml
register:       # Fixed word 'register'
    <register_1>:       # Specify Register name
            <field1>:           # Field 1 name in register_1
                size: <size>            # Size of the field
                reset: <reset_value>    # Reset value.
                swtype: <type>          # SW access type
                hwtype: <type>          # HW access type
                note: <description of the field>
            <field2>:           # Field 2 name in register_2
                size:                   # ...
                ...
            ...
    <register_2>:       # Specify second register name
            <field1>:
                size:
                ...
            RSVR:               # Reserved field. Use fixed word 'RSVR'
                size:               # Only size variable is used in reserved field
            <field2>:
                size:
                ...
            ...
```

## Notes

- The address of the registers are calculated automatically based on the order they are defined in the yaml files.
- The field (bits) location within the register is calculated automatically based on the field width and the previous field.
- **RSVR** field indicate this field is not used. Read to **RSVR** will return 0, write to **RSVR** will be ignored
- Unused bits will be treated as reserved.
- Each register can not exceed the maximum bits.
- For **swtype/hwtype**, please check [Supported Register Access Type](supported_register_access_type.md)

## Example

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
