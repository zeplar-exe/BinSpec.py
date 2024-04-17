import unittest
from binspec import Specification
from io import BytesIO

import binspec
from binspec.types import Int, String, Array, Bool, Packed, Bits, Bytes


def create_specification(*byte_params: list[bytes]):
    data = bytearray()
    for b in byte_params:
        if isinstance(b, bytes):
            data += b
        else:
            data.append(b)
    return Specification(BytesIO(data))


class IntTests(unittest.TestCase):
    def testIntBytes(self):
        my_spec = create_specification(0b00000011)
        n = my_spec.expect(Int(bytes=1))

        self.assertEqual(n, 3)

    def testIntBytesLittleEndian(self):
        my_spec = create_specification(0b00000011)
        n = my_spec.expect(Int(bytes=1, big_endian=False))

        self.assertEqual(n, 192)

    def testIntBits(self):
        my_spec = create_specification(0b10100011)
        n = my_spec.expect(Int(bits=4))

        self.assertEqual(n, 10)

    def testIntBitsLittleEndian(self):
        my_spec = create_specification(0b10100011)
        n = my_spec.expect(Int(bits=4, big_endian=False))

        self.assertEqual(n, 5)

    def testIntBitsAndBytes(self):
        my_spec = create_specification(0b00000011, 0b00110000)
        n = my_spec.expect(Int(bytes=1, bits=4))

        self.assertEqual(n, 51)

    def testIntBitsAndBytesLittleEndian(self):
        my_spec = create_specification(0b00000011, 0b00110000)
        n = my_spec.expect(Int(bytes=1, bits=4, big_endian=False))

        self.assertEqual(n, 3264)

    def testUtf8String(self):
        my_spec = create_specification("ABC".encode("utf8"))
        magic = my_spec.expect(String("utf8", 3))

        self.assertEqual(magic, "ABC")


class ArrayTests(unittest.TestCase):
    def testArrayOfBools(self):
        my_spec = create_specification(0b11001100)
        arr = my_spec.expect(
            Array(
                Bool(single_bit=True),
                8
            ))
        
        self.assertEqual(arr, [True, True, False, False, True, True, False, False])


class PackedTests(unittest.TestCase):
    def testPackedBySpecTypeArray(self):
        my_spec = create_specification(0b11001100)
        packed = my_spec.expect(
            Packed(
                [
                    Int(bits=2),
                    Int(bits=4),
                    Array(Bool(single_bit=True), length=2)
                ]
            ))

        self.assertEqual(packed, [3, 3, [False, False]])


class ShowTests(unittest.TestCase):
    def testPackedBySpecTypeArray(self):
        my_spec = create_specification(0b11001100)
        my_spec.track_stream = True
        a = my_spec.expect(Int(bits=2), label="Int A")
        b = my_spec.expect(Int(bits=4), label="Int B")
        c = my_spec.expect(Array(Bool(single_bit=True), length=2), label="Arr C")
        
        my_spec.show()

        self.assertEqual(packed, [3, 3, [False, False]])


class BitsTests(unittest.TestCase):
    pass


class BytesTests(unittest.TestCase):
    pass


if __name__ == '__main__':
    unittest.main()
