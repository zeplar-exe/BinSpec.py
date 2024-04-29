# BinSpec

BinSpec (short for Binary Specification) is a binary parsing library built with Python 3.
[unit testing badge]

## Installation

Install BinSpec from PyPi:

```
pip install binspec
```

## Usage

BinSpec is based around the `Specification` class which is used in tandem with `SpecType`s to parse and validate binary data.

```py
from binspec import Specification
from binspec.types import String, Int, Array

data = bytearray()
data.append("MAGIC".encode("utf8"))
data.append(0b01110110)
data.append(0b11001100)

spec = Specification(data)
magic = spec.expect(String(length=5, encoding="utf8"))

if magic != "MAGIC":
    spec.fail("Expected magic string: MAGIC") # Manually fail and raise a SpecError.

n = spec.expect(Int(bytes=1))

print(n)
# 0b01110110 -> 118

flags = spec.expect(Array(Int(bits=2), length=4))

print(flags)
# [ 0b11, 0b00, 0b11, 0b00 ] -> [ 3, 0, 3, 0 ]
```

> Currently, the builtin `SpecType`s consist of `String`, `Int`, `Int8`, `Int16`, `Int32`, `Int64`, `Packed`, `Array` `Bytes`, and `Bits`. Refer to their docstrings for more inforomation.

In practice, `data` should come from an outside source, such as `FileIO.read()`. In the best case, a conversion to `BytesIO` is not necessary and stream-like object can be used directly to supply `Specification`.

```py
from binspec import Specification
from binspec.types import String, Int, Array

with open("my_imaginary_file.binary", "rb") as f:
    spec = Specification(f)

    # ...
```

### UI

Additonally, a simple webpage is provided to visualize a specification.

## Creating Custom SpecTypes

To create a custom `SpecType`, create a class which derives from `SpecType`:

```py
from binspec.types import SpecType

class ByteAsAString(SpecType):
    pass
```

For this example, the custom `SpecType` will parse a byte as a string of 1s and 0s.

Continuing, SpecType requires two abstract methods, `get_bit_length` and `parse` to be implemented.

```py
from binspec.types import SpecType

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
```

And voila, now use `ByteAsAString` in `Specification.expect` (or another `SpecType`, like `Array`) to parse it.

```py
from binspec import Specification
from binspec.types import Array

data = bytearray()
data.append(0b11110000)
data.append(0b10101010)

data.append(0b10101010)
data.append(0b11110000)

spec = Specification(data)

s = spec.expect(BytesAsAString(byte_count=2))

print(s)
# "1111000010101010"

arr = spec.expect(Array(BytesAsAString(byte_count=1), length=2))

print(arr)
# [ "10101010", "11110000" ]
```
