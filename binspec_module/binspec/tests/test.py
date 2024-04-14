from io import BytesIO
from main import Specification, Int, Array, Bits

print("Retard")
bits = bytearray()
bits.append(0b10001001)
bits.append(0b11110000)
bits.append(0b00001111)
bits.append(0b01000000)

data = BytesIO(bits)

spec = Specification(data)
n = spec.expect(Array(Int(bytes=1), length=2))

print(n)

n = spec.expect(Int(bytes=1, big_endian=False))

print(n)

n = spec.expect(Bits(count=2))

print(n)