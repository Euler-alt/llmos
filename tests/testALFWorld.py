import unittest
from llmos_core.Program import ALFworldProgram

class MyTestCase(unittest.TestCase):
    def test_something(self):
        program = ALFworldProgram()
        result = program.run()
        self.assertIsInstance(result,dict)  # add assertion here


if __name__ == '__main__':
    unittest.main()
