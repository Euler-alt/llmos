import unittest

from llmos_core.Prompts import parse_response
from llmos_core.Program.context_program import load_cache_result

class MyTestCase(unittest.TestCase):
    def test_parser_response(self):
        result = load_cache_result()
        call = parse_response(result)


if __name__ == '__main__':
    unittest.main()
