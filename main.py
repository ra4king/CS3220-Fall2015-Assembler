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


class Instruction:
    def __init__(self, op, arg1=None, arg2=None, arg3=None, arg3Imm=False):
        self._op = op
        self._args = [arg for arg in [arg1, arg2, arg3] if arg != None]
        self.arg3Imm = arg3Imm

    @property
    def args(self):
        return self._args

    @property
    def op(self):
        return self._op

    def __str__(self):
        return "Instruction(%s: %s) %r" % (self.op, str(self.args), self.arg3Imm)

    def __repr__(self):
        return str(self)


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
