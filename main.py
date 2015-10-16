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

# print("System registers: \n  %s" % "\n  ".join(sorted(["%s: %d" % (r, n) for r, n in REGISTERS.items()])))
# print()


# Superclass for Instruction and 
class Statement:
    def __init__(self, statement):
        self._word_address = None
        self._statement = statement

    # Word address of the statement as an int
    @property
    def word_address(self):
        return self._word_address
    @word_address.setter
    def word_address(self, value):
        if value != None and not isinstance(value, int):
            raise TypeError("Word address must be an int")
        self._word_address = value

    @property
    def statement(self):
        return self._statement

    # Returns a string containing the output "mif" format.  Does not include a
    # leading or trailing newline.
    # 
    # @param labels A dictionary mapping label names to values
    def generate_output_code(self, labels={}):
        raise NotImplementedError()


class Label(Statement):
    def __init__(self, statement, label):
        super().__init__(statement)
        self._label = label

    @property
    def label(self):
        return self._label

    def __str__(self):
        return "Label(%s)" % self._label

    def __repr__(self):
        return __str__(self)


# Abstract superclass for the different instruction types.
class Instruction(Statement):
    def __init__(self, statement, op, args=[]):
        super().__init__(statement)
        self._op = op
        self._args = args

    def generate_iword(self, labels):
        raise NotImplementedError()

    def generate_output_code(self, labels={}):
        out = "-- @ 0x" + int2hex(self.word_address, 8) + " : " + self.op + "\t" + ', '.join(self.args)
        out += "\n"
        out += hex(self.word_address)[2:].zfill(8) + ' : ' + self.generate_iword(labels) + ';'
        return out

    @property
    def op(self):
        return self._op

    @property
    def args(self):
        return self._args

    def __str__(self):
        return "0x%08x: %-20s (%5s: %s)" % (self.word_address, self.__class__.__name__, self.op, str(self.args))

    def __repr__(self):
        return str(self)

OPCODES = {
    'ADD': "0000 0000",
    'SUB': "0001 0000",
    'AND':"0100 0000",
    'OR':"0101 0000",
    'XOR':"0110 0000",
    'NAND':"1100 0000",
    'NOR':"1101 0000",
    'XNOR':"1110 0000",

    'ADDI': "0000 1000",
    'SUBI':  "0001 1000",
    'ANDI':  "0100 1000",
    'ORI':  "0101 1000",
    'XORI':  "0110 1000",
    'NANDI':  "1100 1000",
    'NORI':  "1101 1000",
    'XNORI':  "1110 1000",
    'MVHI':   "1011 1000",

    'LW':   "0000 1001",
    'SW': "0000 0101",

    'F': "0000 0010",
    'EQ': "0001 0010",
    'LT': "0010 0010",
    'LTE': "0011 0010",
    'T': "1000 0010",
    'NE': "1001 0010",
    'GTE': "1010 0010",
    'GT': "1011 0010",

    'FI': "0000 1010",
    'EQI': "0001 1010",
    'LTI': "0010 1010",
    'LTEI': "0011 1010",
    'TI': "1000 1010",
    'NEI': "1001 1010",
    'GTEI': "1010 1010",
    'GTI': "1011 1010",

    'BF': "0000 0110",
    'BEQ': "0001 0110",
    'BLT': "0010 0110",
    'BLTE': "0011 0110",
    'BEQZ': "0101 0110",
    'BLTZ': "0110 0110",
    'BLTEZ': "0111 0110",
    'BT': "1000 0110",
    'BNE': "1001 0110",
    'BGTE': "1010 0110",
    'BGT': "1011 0110",
    'BNEZ': "1101 0110",
    'BGTEZ': "1110 0110",
    'BGTZ': "1111 0110",
    'JAL': "0000 1011"
}
# remove spaces and convert to one hex byte (excluding the leading '0x')
OPCODES = {instr: hex(int(val.replace(' ', ''), 2))[2:].zfill(2) for instr, val in OPCODES.items()}
# print(OPCODES)


# Converts register name (lower or uppercase) to an 8-bit hex string (no leading '0x')
def reg2hex(regname):
    return int2hex(REGISTERS[regname.upper()], 2)


def int2hex(val, numchars):
    return hex(val)[2:].zfill(numchars)


# InstructionReg3      - ADD RD, RS1, RS2
class InstructionReg3(Instruction):
    def generate_iword(self, labels):
        return ''.join([reg2hex(self.args[i]) for i in range(3)]) + OPCODES[self.op]

# InstructionReg2Imm   - ADDI RD, RS1, imm;  LW RD, imm(RS1)
# TODO: DON'T FORGET SW RS2, imm(RS1) is stored BACKWARDS: RS1 RS2 imm[15:0]
class InstructionReg2Imm(Instruction):
    def generate_iword(self, labels):
        if self.op == 'SW':
            # TODO(justin)
            # raise NotImplementedError("Handle SW separately")
            return "SW"
        else:
            imm = self.args[2]
            if imm[0:2] == '0x':
                imm = imm[2:].zfill(4)
            else:
                imm = int2hex(labels[imm], 4)
            # print(self.args)
            return ''.join([reg2hex(self.args[i]) for i in range(2)]) + imm + OPCODES[self.op]

# InstructionRegImm    - MVHI RD, imm
class InstructionRegImm(Instruction):
    def generate_iword(self, labels):
        imm = self.args[1]
        if imm[0:2] == '0x':
            imm = imm[2:].zfill(4)
        else:
            imm = int2hex(labels[imm], 4)
        return reg2hex(self.args[0]) + '00' + imm + OPCODES[self.op]

# # InstructionImm       - BR imm
class InstructionImm(Instruction):
    pass

# InstructionReg2      - NOT RD, RS
class InstructionReg2(Instruction):
    pass


# TODO: should this be a subclass of Statement instead?
class Directive(Instruction):
    pass


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

    return result


def create_label_parser():
    label = r'(\w+):'
    return re.compile(label)

opcode = r'([A-Z]+)'
reg = '(' + '|'.join(list(zip(*REGISTERS.items()))[0]) + ')'
imm = r'(0x[0-9A-F]+)|(-?\d+)|(\w+)'

# handles 3 regs, 2 regs, 2 regs + imm, 1 reg + imm
def create_instr_regs_parser():
    instr = r'^' + opcode + r'\s+' + reg + r'(?:,\s*' + reg + r')?,\s*' + r'(?:' + reg + r'|' + imm + r')$'
    return re.compile(instr, re.I)

# handles reg, imm(reg)
def create_instr_addr_parser():
    instr = r'^' + opcode + r'\s+(?:' + reg + r',\s*)?(?:' + imm + r')\s*\(\s*' + reg + r'\s*\)$'
    return re.compile(instr, re.I)

def create_instr_br_parser():
    instr = r'^BR\s*(?:' + imm + ')$'
    return re.compile(instr, re.I)

def create_directive_parser():
    directive = r'^\s*\.(?:ORIG\s+(?:(0x[0-9a-fA-F]+)|(-?\d+))|WORD\s+(?:' + imm + r')|NAME\s+(\w+)\s*=\s*(?:(0x[0-9a-fA-F]+)|(-?\d+)))\s*$'
    return re.compile(directive, re.I)

def clean(lines):
    lines = [l.split(';')[0] for l in lines]
    i = 0
    while i < len(lines):
        idx = lines[i].find(':')
        if idx != -1:
            lines.insert(i+1, lines[i][idx+1:])
            lines[i] = lines[i][0:idx+1]
        i += 1

    return [l.strip() for l in lines if l.strip()]

def parse_statements(lines):
    instr_regs_parser = create_instr_regs_parser()
    instr_addr_parser = create_instr_addr_parser()
    instr_br_parser = create_instr_br_parser()
    label_parser = create_label_parser()
    directive_parser = create_directive_parser()

    statements = []
    for l, i in zip(lines, range(1, len(lines) + 1)):
        match = instr_regs_parser.match(l)
        if match:
            value = hex(int(match.group(5) or match.group(6), 0) & 0xffff) if match.group(5) or match.group(6) else match.group(7)

            instrClass = None
            args = None

            if value:
                if match.group(3):
                    instrClass = InstructionReg2Imm
                    args = [match.group(2), match.group(3), value]
                else:
                    instrClass = InstructionRegImm
                    args = [match.group(2), value]
            else:
                if match.group(3):
                    instrClass = InstructionReg3
                    args = [match.group(2), match.group(3), match.group(4)]
                else:
                    instrClass = InstructionReg2
                    args = [match.group(2), match.group(4)]

            statements.append(instrClass(l, match.group(1).upper(), args))
            continue

        match = instr_addr_parser.match(l)
        if match:
            value = hex(int(match.group(3) or match.group(4), 0) & 0xffff) if match.group(3) or match.group(4) else match.group(5)

            instrClass = None
            args = None

            if match.group(2):
                instrClass = InstructionReg2Imm
                args = [match.group(2), match.group(6), value]
            else:
                instrClass = InstructionRegImm
                args = [match.group(6), value]

            statements.append(instrClass(l, match.group(1).upper(), args))
            continue

        match = instr_br_parser.match(l)
        if match:
            value = hex(int(match.group(1) or match.group(2), 0) & 0xffff) if match.group(1) or match.group(2) else match.group(3)
            statements.append(InstructionImm(l, 'BR', [value]))
            continue

        match = label_parser.match(l)
        if match:
            statements.append(Label(l, match.group(1)))
            continue

        match = directive_parser.match(l)
        if match:
            if match.group(1) != None or match.group(2) != None:
                value = hex(int(match.group(1) or match.group(2), 0) & 0xffffffff)
                statements.append(Directive(l, '.ORIG', [value]))
            elif match.group(3) != None or match.group(4) != None or match.group(5) != None:
                value = hex(int(match.group(3) or match.group(4), 0) & 0xffffffff) if match.group(3) or match.group(4) else match.group(5)
                statements.append(Directive(l, '.WORD', [value]))
            else:
                value = hex(int(match.group(7) or match.group(8), 0) & 0xffffffff)
                statements.append(Directive(l, '.NAME', [match.group(6), value]))

            continue

        match = re.match(r'^(RET)$', l, re.I)
        if match:
            statements.append(Instruction(l, 'RET'))
            continue

        raise Exception("Syntax error at statement %d: %s" % (i, l))

    return statements

def expand_pseudo_ops(statements):
    newStatements = []
    for s in statements:
        if isinstance(s, Instruction):
            if s.op == 'BR':
                newStatements.append(InstructionReg2Imm(s.statement, 'BEQ', ['R6', 'R6', s.args[0]]))
            elif s.op == 'NOT':
                newStatements.append(InstructionReg3(s.statement, 'NAND', [s.args[0], s.args[1], s.args[1]]))
            elif s.op == 'BLE':
                newStatements.append(InstructionReg3(s.statement, 'LTE', ['R9', s.args[0], s.args[1]]))
                newStatements.append(InstructionRegImm(s.statement, 'BNEZ', ['R9', s.args[2]]))
            elif s.op == 'BGE':
                newStatements.append(InstructionReg3(s.statement, 'GTE', ['R9', s.args[0], s.args[1]]))
                newStatements.append(InstructionRegImm(s.statement, 'BNEZ', ['R9', s.args[2]]))
            elif s.op == 'CALL':
                newStatements.append(InstructionReg2Imm(s.statement, 'JAL', ['RA', s.args[0], s.args[1]]))
            elif s.op == 'RET':
                newStatements.append(InstructionReg2Imm(s.statement, 'JAL', ['R9', 'RA', '0x0']))
            elif s.op == 'JMP':
                newStatements.append(InstructionReg2Imm(s.statement, 'JAL', ['R9', s.args[0], s.args[1]]))
            else:
                newStatements.append(s)
        else:
            newStatements.append(s)

    return newStatements

def assign_addresses(statements):
    physical_statements = []
    labels = {}

    current_address = None

    for s in statements:
        if isinstance(s, Directive):
            if s.op == '.ORIG':
                current_address = int(s.args[0], 0)
            elif s.op == '.NAME':
                labels[s.args[0]] = int(s.args[1], 0)
            elif s.op == '.WORD':
                if current_address == None:
                    raise Exception(".WORD directive found before .ORIG %s" % str(s))

                s.word_address = current_address
                physical_statements.append(s)
                current_address += 4
        elif isinstance(s, Instruction):
            if current_address == None:
                raise Exception("Instruction found before .ORIG %s" % str(s))

            s.word_address = current_address
            physical_statements.append(s)
            current_address += 4
        elif isinstance(s, Label):
            if current_address == None:
                raise Exception("Label found before .ORIG %s" % str(s))

            labels[s.label] = current_address

    return (physical_statements, labels)

def assemble(fileIn, fileOut):
    lines = clean([l for l in open(fileIn)])
    print(repr(lines))

    statements = parse_statements(lines)
    statements = expand_pseudo_ops(statements)

    statements, labels = assign_addresses(statements)

    print("\nStatements:")
    for s in statements:
        print(str(s))

    print("\nLabels:")
    for l, v in labels.items():
        print("0x%08x: %s" % (v, l))

    # write output file
    with open(fileOut, 'w') as f:
        f.write(generate_output(statements, labels))


if __name__ == '__main__':
    import sys

    if len(sys.argv) != 3:
        print("Usage: assembler.py inputFile outputFile")
        sys.exit(-1)

    try:
        assemble(sys.argv[1], sys.argv[2])
    except Exception as e:
        print("Error occurred while assembling: %s" % str(e))
        import traceback
        traceback.print_exc(file=sys.stdout)
        sys.exit(-1)
