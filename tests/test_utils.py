import unittest
from game4.utils import parse_variables

class TestParseVariables(unittest.TestCase):
    def test_parse_integer_variables(self):
        input_str = """health: 100
shields: 50
ammo: 25"""
        expected = {
            'health': 100,
            'shields': 50,
            'ammo': 25
        }
        self.assertEqual(parse_variables(input_str), expected)

    def test_parse_boolean_variables(self):
        input_str = """is_armed: true
shield_active: false
stealth_mode: True"""
        expected = {
            'is_armed': True,
            'shield_active': False,
            'stealth_mode': True
        }
        self.assertEqual(parse_variables(input_str), expected)

    def test_parse_mixed_variables(self):
        input_str = """health: 100
is_armed: true
ammo: 0"""
        expected = {
            'health': 100,
            'is_armed': True,
            'ammo': 0
        }
        self.assertEqual(parse_variables(input_str), expected)

    def test_handle_empty_lines(self):
        input_str = """health: 100

shields: 50

ammo: 25"""
        expected = {
            'health': 100,
            'shields': 50,
            'ammo': 25
        }
        self.assertEqual(parse_variables(input_str), expected)

    def test_handle_whitespace(self):
        input_str = """  health  :  100  
  shields:50
ammo  :  25  """
        expected = {
            'health': 100,
            'shields': 50,
            'ammo': 25
        }
        self.assertEqual(parse_variables(input_str), expected)

if __name__ == '__main__':
    unittest.main() 