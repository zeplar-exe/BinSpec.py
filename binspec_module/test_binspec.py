import unittest
from io import BytesIO

import binspec
from binspec import Specification
from binspec.types import SpecType, Int, String, Array, Bool, Packed, Bits, Bytes
from binspec.errors import SpecError, SpecTypeError, SpecEofError


def create_specification(*byte_params: list[bytes]):
    data = bytearray()
    for b in byte_params:
        if isinstance(b, bytes):
            data += b
        else:
            data.append(b)
    return Specification(BytesIO(data))


class ErrorTests(unittest.TestCase):
    def testInvalidSpecType(self):
        class InvalidSpecType(SpecType):
            def get_bit_length(self):
                return -1
        
        my_spec = create_specification(0b0)

        self.assertRaises(SpecTypeError, my_spec.expect, InvalidSpecType())
    
    def testEof(self):
        my_spec = create_specification(0b11110000)
        my_spec.expect(Int(bytes=1))

        self.assertRaises(SpecEofError, my_spec.expect, Bits(1))

    def testNoneAtEof(self):
        my_spec = create_specification(0b11110000)
        my_spec.expect(Int(bytes=1))

        value = my_spec.expect(Bits(10), none_at_eof=True)

        self.assertIsNone(value)

    def testAssertEofSuccess(self):
        my_spec = create_specification(0b11110000)
        my_spec.expect(Int(bytes=1))

        my_spec.assert_eof()

    def testAssertEofFail(self):
        my_spec = create_specification(0b11110000)

        self.assertRaises(SpecEofError, my_spec.assert_eof)


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

class StringTests(unittest.TestCase):
    def testUtf8String(self):
        my_spec = create_specification("ABC".encode("utf8"))
        magic = my_spec.expect(String("utf8", length=3))

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
    
    def testNames(self):
        my_spec = create_specification(0b11001100)
        packed = my_spec.expect(
            Packed(
                [
                    Int(bits=2),
                    Int(bits=4),
                    Array(Bool(single_bit=True), length=2)
                ],
                names=[ "a", "b", "c" ]
            ))

        self.assertEqual(packed, { "a": 3, "b": 3, "c": [False, False] })
    
    def testKwargs(self):
        my_spec = create_specification(0b11001100)
        packed = my_spec.expect(
            Packed.from_kwargs(a=Int(bits=2), b=Int(bits=4), c=Array(Bool(single_bit=True), length=2)))

        self.assertEqual(packed, { "a": 3, "b": 3, "c": [False, False] })
    
    def testDict(self):
        my_spec = create_specification(0b11001100)
        packed = my_spec.expect(
            Packed.from_dict({"a": Int(bits=2), "b": Int(bits=4), "c": Array(Bool(single_bit=True), length=2)}))

        self.assertEqual(packed, { "a": 3, "b": 3, "c": [False, False] })


class BooleanTests(unittest.TestCase):
    def testSingleBitBool(self):
        my_spec = create_specification(0b10000000)
        b = my_spec.expect(Bool(single_bit=True))

        self.assertTrue(b)

    def testByteBool(self):
        my_spec = create_specification(0b00000001)
        b = my_spec.expect(Bool())

        self.assertTrue(b)

    def testArbitraryNumberBool(self):
        my_spec = create_specification(0b11110011)
        b = my_spec.expect(Bool())

        self.assertTrue(b)


class BitsTests(unittest.TestCase):
    def testBitsParse(self):
        my_spec = create_specification(0b11000011)
        bits = my_spec.expect(Bits(8))

        self.assertEqual([0 if b == 0 else 1 for b in bits], [ 1, 1, 0, 0, 0, 0, 1, 1 ])

    def testNibble(self):
        my_spec = create_specification(0b11000011)
        bits = my_spec.expect(Bits(4))

        self.assertEqual([0 if b == 0 else 1 for b in bits], [ 1, 1, 0, 0 ])


class ReadmeTests(unittest.TestCase):
    def testBytesAsAString(self):
        class BytesAsAString(SpecType):
            def __init__(self, *, byte_count: int):
                self.byte_count = byte_count

            def get_bit_length(self):
                return self.byte_count * 8

            def parse(self, bits: bytes) -> str:
                s = ""

                for b in bits:
                    if b == 0:
                        s += "0"
                    else:
                        s += "1"

                return s
        
        data = bytearray()
        data.append(0b11110000)
        data.append(0b10101010)

        data.append(0b10101010)
        data.append(0b11110000)

        spec = Specification(data)

        s = spec.expect(BytesAsAString(byte_count=2))

        self.assertEqual(s, "1111000010101010")

        arr = spec.expect(Array(BytesAsAString(byte_count=1), length=2))

        self.assertEqual(arr, [ "10101010", "11110000" ])


if __name__ == '__main__':
    unittest.main()
