# ASAP Assembler
An assembler for the homemade computer AASAP - Almost As Simple As Possible.

## Description 
Takes in assembly language and outputs machine code as a binary file, or a header file for use with a standalone Arduino bootloader.

Support labels and the following instructions:
* `NOP`: No operation
* `LDA`: Load A from value stored in memory address
* `LDI`: Load A from an immediate value
* `STA`: Store A to a memory address
* `ADD`: Add a value stored in memory address to the A Register
* `ADI`: Add an immediate value to the A Register
* `SUB`: Subtract a value stored in memory address from the A Register
* `SUI`: Subtract an immediate value from the A Register
* `JMP`: Jump to a memory address
* `HLT`: Halt
* `DCM`: Send a value stored in a memory address to the display's command register
* `DCI`: Send an immediate value to the display's command register
* `DOC`: Send a value stored in a memory address to the display's data register
* `DOI`: Send an immediate value to the display's data register

## Usage
`assembler.py` takes the following arguments along with an input file containing assembley code.
* `-o` `--output-file`: Optional: The filename to use for the output file. Defaults to using the input filename with the correct format extension.
* `-f {binary,header}`: Optional: The output format. Defaults to binary.
