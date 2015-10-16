import unittest
import os
import tempfile

# assembler module
import assembler


EXAMPLES = ['Test2', 'Sorter2']



def strip_comments(assembly):
    lines = [line for line in assembly.split('\n') if len(line) < 2 or line[0:2] != '--']
    return '\n'.join(lines)


class TestAssembler(unittest.TestCase):
    def setUp(self):
        # We put the assembler output in a tmp folder to not clutter our code files
        self.tempdir = tempfile.mkdtemp()
        self.maxDiff = None

    def test_examples(self):
        ex_dir = os.path.join(os.path.dirname(__file__), "examples")
        for example in EXAMPLES:
            infile = os.path.join(ex_dir, "%s.a32" % example)
            outname = "%s.mif" % example
            outfile = os.path.join(self.tempdir, outname)
            expected_outfile = os.path.join(ex_dir, outname)

            # Assemble!
            assembler.assemble(infile, outfile)

            # Make sure that the produced code is the same as 
            with open(expected_outfile) as f:
                expected_bytecode = strip_comments(f.read())
            with open(outfile) as f:
                actual_bytecode = strip_comments(f.read())
            self.assertEqual(expected_bytecode, actual_bytecode)
