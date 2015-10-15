import unittest
import os
import tempfile

# main assembler module
import main

# import  nose


EXAMPLES = ['Test2', 'Sorter2']

class TestAssembler(unittest.TestCase):
    def setUp(self):
        # We put the assembler output in a tmp folder to not clutter our code files
        self.tempdir = tempfile.mkdtemp()

    def test_examples(self):
        ex_dir = os.path.join(os.path.dirname(__file__), "examples")
        for example in EXAMPLES:
            infile = os.path.join(ex_dir, "%s.a32" % example)
            outname = "%s.mif" % example
            outfile = os.path.join(self.tempdir, outname)
            expected_outfile = os.path.join(ex_dir, outname)

            # Assemble!
            main.assemble(infile, outfile)

            # Make sure that the produced code is the same as 
            with open(expected_outfile) as f:
                expected_bytecode = f.read()
            with open(outfile) as f:
                actual_bytecode = f.read()
            self.assertEqual(expected_bytecode, actual_bytecode)
