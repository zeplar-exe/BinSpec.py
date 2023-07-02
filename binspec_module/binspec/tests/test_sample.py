import unittest
from spec import spec
import spec_type

class SampleTest(unittest.TestCase):
    def test1(self):
        with open("tests/files/base_test_file.bin", "rb") as f:
            my_spec = spec(f)
            my_spec.next(spec_type.integer(1))

            self.assertEqual(len(my_spec.get_history()), 1)

    def test2(self):
        with open("tests/files/base_test_file.bin", "rb") as f:
            my_spec = spec(f)
            magic = my_spec.next(spec_type.integer(1))

            self.assertEqual(len(my_spec.get_history()), 1)
            self.assertEqual(magic, 27)

if __name__ == '__main__':
    unittest.main()
