import argparse
import os.path
import sys
import re

#A simple custom exception we can use for input-file syntax errors. 
#SyntaxError is already taken
class AssemblyError(Exception): pass

opcode_dictionary = {
    'NOP' : {
        'number' : 0,
        'operand_num_bytes' : 0
        },
    'LDA' : {
        'number' : 1,
        'operand_num_bytes' : 1
        },
    'LDI' : {
        'number' : 2,
        'operand_num_bytes' : 2
        },
    'STA' : {
        'number' : 3,
        'operand_num_bytes' : 1
        },
    'ADD' : {
        'number' : 4,
        'operand_num_bytes' : 2
        },
    'ADI' : {
        'number' : 5,
        'operand_num_bytes' : 1
        },
    'SUB' : {
        'number' : 6,
        'operand_num_bytes' : 2
        },
    'SUI' : {
        'number' : 7,
        'operand_num_bytes' : 1
        },
    'JMP' : {
        'number' : 8,
        'operand_num_bytes' : 2
        },
    'HLT' : {
        'number' : 9,
        'operand_num_bytes' : 0
        },
    'DCM' : {
        'number' : 11,
        'operand_num_bytes' : 2
        },
    'DCI' : {
        'number' : 12,
        'operand_num_bytes' : 2
        },
    'DOC' : {
        'number' : 13,
        'operand_num_bytes' : 2
        },
    'DOI' : {
        'number' : 14,
        'operand_num_bytes' : 2
        }
    }

def continue_question(explanation = ''):
    """Asks the user if they want to continue with an optional explanation
        for why they are being asked. Returns 'y' or 'n' from the user."""
    if explanation:
        question = explanation + ', do you wish to continue? [Y/n]:'
    else:
        question = 'Do you wish to continue? [Y/n]:'
        
    answer = input(question).strip().lower()[0]
    while answer not in ('y','n'):
        answer = input(question).strip().lower()[0]
        
    return answer

def open_file(filename, mode):
    """Helper for opening files. Checks for common issues and asks for
        confirmation if a file already exisits for writing"""
    if 'w' in mode and os.path.exists(output_filename):
        if 'n' == continue_question('File ' + output_filename 
                                    + ' already exists'):
            sys.exit(1)

    try: 
        file = open(filename, mode)
    except FileNotFoundError:
        print('File', input_filename, '''does not exist or you do not
            have permission to read it''')
        sys.exit(1)
    except PermissionError:
        print('You do not have permission to write to', output_filename)
        sys.exit(1)

    return file
    
def strip_lines(lines):
    """A generator that returns non-empty lines once comments and 
    start/end spaces have been removed"""
    for line_num, line in enumerate(lines, start=1):
        line = line.split(';')[0]
        line = line.strip()
        if len(line) > 0:
            yield line_num, line
            
def num_bytes(int):
    """Works out how many bytes are needed to represent a number"""
    num_bits = int.bit_length()
    #Python has no ceiling division so use a floor division trick
    num_bytes = (num_bits + 7) // 8
    return num_bytes
            
def parse_number(number):
    """Parse a Binary, Hex, or Decimal number and return as decimal"""
    if number.startswith(('0x', '0X')):
        number = int(number[2:], 16);
    elif number.startswith(('0b', '0B')):
        number = int(number[2:], 2);
    elif number.isdecimal():
        number = int(number)
    elif number == '':
        raise AssemblyError('Expected a number, got EOL')
    else:
        raise AssemblyError('Expected a number, got {0}'.format(number))
        
    return number, num_bytes(number);
    
def parse_label(line):
    """Checks a label to make sure it's the correct syntax"""
    label, extra_characters = line.split(':', maxsplit = 1)
    if extra_characters != '':
        raise AssemblyError('Expected EOL after ":"')
    else:
        return label
    

def parse_opcode(line):
    """Check that the Opcode exists and contains a value if needed"""
    fields = line.split(maxsplit=1)
    opcode = fields[0]
    if len(fields) > 1:
        operand = fields[1]
    else:
        operand = ''
    if opcode in opcode_dictionary.keys():
        opcode_details = opcode_dictionary.get(opcode)
        return (opcode_details['number'], operand,
                opcode_details['operand_num_bytes'])
    else:
        raise AssemblyError('Unknown opcode')
        
def get_symbol_value(symbol, symbols):
    """Checks a symbol exists and returns it's value"""
    if symbol in symbols.keys():
        value = symbols.get(symbol)
    else:
        raise AssemblyError('Unknown symbol')
        
    return value
        
def parse_assembly_code(filename):
    """Parse assembly code into a list of labels, variables and opcodes. 
        Opcodes are returned along with their given operands"""
        
    file = open_file(filename, 'r')
    opcodes = []
    symbols = {}
    current_memory_address = 0
    label_pattern = re.compile(r'[a-zA-Z_][a-zA-Z0-9_]*:')
    opcode_pattern = re.compile(r'[A-Z]{3}\s*')
        
    for line_num, line in strip_lines(file):
        try:
            if label_pattern.match(line):
                label = parse_label(line)
                symbols[label] = current_memory_address
            elif opcode_pattern.match(line):
                opcode_num, operand, operand_num_bytes = parse_opcode(line)
                opcodes.append((line_num, opcode_num, operand, operand_num_bytes))
                current_memory_address += operand_num_bytes + 1
            else:
                raise AssemblyError('Unknown input')
        except (AssemblyError, ValueError) as error:
            print('Line {0}: {1}\r\nError: {2}'.format(line_num, line,
                                                        error))
            sys.exit(1)
            
    file.close()
    
    return symbols, opcodes
        
def generate_machine_code(symbols, opcodes):
    """Parse opcodes and operands and output them as machine code"""

    high_byte = lambda byte : (byte & 0xff00) >> 8
    low_byte = lambda byte : byte & 0xff

    symbol_pattern = re.compile(r'[a-zA-Z_][a-zA-Z0-9_]*')
    machine_code = []
    try:
        for line_num, opcode_num, operand, expected_bytes in opcodes:
        
            machine_code.append(opcode_num)
        
            #Symbols are always memory addresses which are 2 bytes
            if expected_bytes == 2 and symbol_pattern.match(operand):
                operand_value = get_symbol_value(operand, symbols)
                operand_num_bytes = 2;
            else:
                operand_value, operand_num_bytes = parse_number(operand);
                
            if operand_num_bytes <= expected_bytes:
                if expected_bytes == 2:
                    machine_code.append(high_byte(operand_value))
                if expected_bytes >= 1:
                    machine_code.append(low_byte(operand_value))    
            else:
                err = 'Expected {0} byte(s), got {1}'.format(expected_bytes, operand_num_bytes)
                raise AssemblyError(err)

    except (AssemblyError, ValueError) as error:
        print('Line {0}: Error: {1}'.format(line_num, error))
        sys.exit(1)
                
    return machine_code

def write_machine_code(filename, machine_code, format):
    """Writes the machine code to the output file in the format specified"""
    
    file = open_file(filename, 'w')
    if format == '.h':
            file.write('char program[] = {\n\t')
            for index, byte in enumerate(machine_code[:-1], start = 1):
                file.write('{0:03}, '.format(byte))
                if (index % 8) == 0:
                    file.write('\n\t')
            file.write('{0:03}\n\t}}'.format(byte))
            
    file.close()

def main(input_filename, output_filename, output_format):
    """Take a file containing assembly language and convert it in to
        machine code"""

    symbols, opcodes = parse_assembly_code(input_filename)
    
    machine_code = generate_machine_code(symbols, opcodes)
    
    write_machine_code(output_filename, machine_code, output_format)

if '__main__' == __name__:
    """Parse the arguments given and hand these off to the main function"""
    
    parser = argparse.ArgumentParser()
    parser.add_argument('file', type = str, 
                        help = '''specify the name of the file containing
                        the assembly code to compile''')
    parser.add_argument('-o', '--output-file', type = str, 
                        help = 'specify the output file')
    parser.add_argument('-f', '--output-format', type = str, 
                        choices = ['binary', 'header'],
                        help = 'specify the format of the output file')
    args = parser.parse_args()

    input_filename = args.file

    #The default file format is .bin, unless it's set by the user
    output_format = '.bin'
    if 'header' == args.output_format:
        output_format = '.h'
    else: 
        if args.output_file is not None:
            output_filename_extension = os.path.splitext(args.output_file)[1]
            if '.h' == output_filename_extension:
                output_format = output_filename_extensions

    #Use the same name as the input file if an output file isn't given
    if args.output_file is not None:
        output_filename = args.output_file
    else :
        output_filename = os.path.splitext(args.file)[0]
        output_filename += output_format
    
    main(input_filename, output_filename, output_format)