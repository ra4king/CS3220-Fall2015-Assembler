#!/usr/bin/env python3

from pyparsing import Word, alphas, alphanums, ZeroOrMore, Literal, OneOrMore, Regex


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
print()


class Instruction:
    def __init__(self, op, arg1=None, arg2=None, arg3=None):
        self._op = op
        self._args = [arg for arg in [arg1, arg2, arg3] if arg != None]

    @property
    def args(self):
        return self._args

    @property
    def op(self):
        return self._op

    def __str__(self):
        return "Instruction(%s: %s)" % (self.op, str(self.args))

    def __repr__(self):
        return str(self)


def create_parser():
    opcode = Word(alphas)

    reg = None
    for name, num in REGISTERS.items():
        if reg == None:
            reg = Literal(name)
        else:
            reg = reg | Literal(name)


    # hex_value = Literal('0x') + Word(alphanums)
    # dec_value = Word(alphanums)
    # imm_value = dec_value | hex_value
    instr_r3 = (opcode + ' ' + reg + ' ' + reg).setParseAction(lambda s, l, t: Instruction(t[0], t[2], t[4]))
    # instr_i = opcode + reg + reg + imm_value

    # load_store_instr = (opcode + reg + )

    comment = (Literal(';') + Regex(r'[^\n]*')).setParseAction(lambda s, l, t: {'comment': t[1]})

    # instr = instr_r3 | instr_i
    instr = instr_r3

    statement = instr | comment
    # statement = instr

    prog = ZeroOrMore('\n') + statement + ZeroOrMore(OneOrMore('\n') + statement) + ZeroOrMore('\n')
    prog.leaveWhitespace()

    return prog


def main():
    parser = create_parser()
    # input = "; i'm a comment\nADD R0 R1\nADD R0 R1"
    input = "ADD R0 R1\nADD R0 R1"
    print("Input:\n%s" % input)
    result = parser.parseString(input)
    instructions = list(result)
    print("Result:\n%s" % repr(result))

if __name__ == '__main__':
    main()
