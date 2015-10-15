#!/usr/bin/env python3

import re

## Assembler specs given in the instructions pdf
#
# Sizing:
#   Opcods are 4 bits
#   Functions (secondary opcodes) are 4 bits
#   Immediate operands are 16 bits
#   Register indices are 4 bits (RS1, RS2, RD)
#
# Output should be big endian and be 2048 32 bit words (8192 bytes total)


# Maps register names to their numbers
REGISTERS = {}

# Registers R0..R15
for i in range(16): REGISTERS["R%d" % i] = i

# Aliases
REGISTERS["A0"] = REGISTERS["R0"]
REGISTERS["A1"] = REGISTERS["R1"]
REGISTERS["A2"] = REGISTERS["R2"]
REGISTERS["A3"] = REGISTERS["R3"]
REGISTERS["RV"] = REGISTERS["R3"]
REGISTERS["T0"] = REGISTERS["R4"]
REGISTERS["T1"] = REGISTERS["R5"]
REGISTERS["S0"] = REGISTERS["R6"]
REGISTERS["S1"] = REGISTERS["R7"]
REGISTERS["S2"] = REGISTERS["R8"]
REGISTERS["GP"] = REGISTERS["R12"]
REGISTERS["FP"] = REGISTERS["R13"]
REGISTERS["SP"] = REGISTERS["R14"]
REGISTERS["RA"] = REGISTERS["R15"]

print("System registers: \n  %s" % "\n  ".join(sorted(["%s: %d" % (r, n) for r, n in REGISTERS.items()])))
print


# Superclass for Instruction and 
class Statement:
    def __init__(self):
        self._word_address = None

    # Word address of the statement as an int
    @property
    def word_address(self):
        return self._word_address
    @word_address.setter
    def word_address(self, value):
        if value != None and not isinstance(value, int):
            raise TypeError("Word address must be an int")
        self._word_address = value

    # Returns a string containing the output "mif" format.  Does not include a
    # leading or trailing newline.
    # 
    # @param labels A dictionary mapping label names to values
    def generate_output_code(self, labels={}):
        raise NotImplementedError()


# Abstract superclass for the different instruction types.
class Instruction(Statement):
    def __init__(self, op, args=[]):
        super().__init__(self)
        self._op = op
        self._args = args

    @property
    def op(self):
        return self._op

    @property
    def args(self):
        return self._args

    def __str__(self):
        return "Instruction(%s: %s)" % (self.op, str(self.args))

    def __repr__(self):
        return str(self)


# InstructionImmReg    - CALL imm(R1)
class InstructionImmReg(Instruction):
    def generate_output_code(self, labels):
        raise NotImplementedError()

# InstructionReg3      - ADD RD, RS1, RS2
class InstructionReg3(Instruction):
    def generate_output_code(self, labels):
        raise NotImplementedError()

# InstructionReg2Imm   - ADDI RD, RS1, imm;  LW RD, imm(RS1)
class InstructionReg2Im(Instruction):
    def generate_output_code(self, labels):
        raise NotImplementedError()

# InstructionRegImm    - MVHI RD, imm
class InstructionRegImm(Instruction):
    def generate_output_code(self, labels):
        raise NotImplementedError()

# InstructionImm       - BR imm
class InstructionImm(Instruction):
    def generate_output_code(self, labels):
        raise NotImplementedError()

# InstructionReg2      - NOT RD, RS
class InstructionReg2(Instruction):
    def generate_output_code(self, labels):
        raise NotImplementedError()



# Produce final output code.
#
# @param statements A list of Instruction and WordStatement objects with their
#        word_address set correctly.  All immediate values will be labels or
#        hex strings without the leading '0x'.
# @param labels Name, value pairs from all labels and .NAME statements
# @return A string containing the formatted output mif code.
def generate_output(statements, labels={}):
    # file header
    result = """WIDTH=32;
DEPTH=2048;
ADDRESS_RADIX=HEX;
DATA_RADIX=HEX;
CONTENT BEGIN
[00000000..0000000f] : DEAD"""

    result += "\n" + "\n".join([stmt.generate_output_code(labels) for stmt in statements])
    result += "\n"

    return result;



def create_parser():
    label = r'(\w+):'
    opcode = r'([a-zA-Z]+)'
    reg = '(' + '|'.join(zip(*REGISTERS.items())[0]) + ')'
    imm = r'(\d+)|(0x[0-9a-fA-F]+)|(\w+)'

    instr = '^\s*(?:' + label + r'\s*)?' + opcode + r'\s+' + reg + r',\s*' + reg + r',\s*' + '(?:' + reg + '|' + imm + r')\s*$'
    print instr
    print

    # ^\s*(?:(\w+):\s*)?([a-zA-Z]+)\s+(R\d),\s*(?:(R\d),\s*)?(?:(R\d)|(\d+)|(0x[0-9a-fA-F]+)|(\w+))?\s*(?:;.*)?$

    return re.compile(instr)

def strip_comments(lines):
    return [l for l in [l.split(';')[0] for l in lines] if l]

def main():
    parser = create_parser()
    input = "; i'm a comment\nHELLO:ADD R0, R1, R3\nADD R2, R1, HELLO; hello!\nAND R4, RA, 4452"
    print "Input:\n%s\n" % input
    lines = strip_comments(input.split('\n'))
    result = zip(lines, [parser.match(l) for l in lines])
    
    for r, i in zip(result, range(len(result))):
        if not r[1]:
            raise Exception("Error with line %d: %s" % (i + 1, r[0]))

    print 'Num groups: %d' % parser.groups

    #instructions = list(result)
    for _, match in result:
        for i in range(1, parser.groups+1):
            if match.group(i):
                print match.group(i),
            print "\t",
        print

if __name__ == '__main__':
    main()
