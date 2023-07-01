import unittest
import spec_type

class SampleTest(unittest.TestCase):
    def test(self):
        self.assertIsNotNone(spec_type)

if __name__ == '__main__':
    unittest.main()
