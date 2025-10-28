import unittest
from operator import truediv

from llmos_core.Program import ContextProgram
from llmos_core.Program import ALFworldProgram

program = ContextProgram()
class TestProgram(unittest.TestCase):
    def test_context_program(self):
        result = program.run(use_cache=True)
        assert(isinstance(result, dict))

if __name__ == '__main__':
    unittest.main()