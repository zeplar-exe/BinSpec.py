from abc import abstractmethod
from errors import SpecError, SpecTypeError
from typing import Union


class SpecType:
  def bits_to_bytes(self, bits: list[int], big_endian: bool=True) -> bytes:
    b = bytearray()
    extra_bit_count = len(bits) % 8

    for i in range(0, len(bits), 8):
      bit_count = extra_bit_count if (len(bits) - i) < 8 else 8
      n = SpecType.bits_to_int(self, bits[i:i + bit_count], big_endian)
      b.append(n)

    return bytes(b)

  def bits_to_int(self, bits: list[int], big_endian: bool=True) -> int:
    n = 0

    # Raw order of bits just so happens to be little endian... duh
    for bit in reversed(bits) if big_endian else bits:
      n >>= 1

      if bit != 0:
        n |= 128

    return n

  @abstractmethod
  def get_bit_length(self) -> int:
    raise NotImplementedError("SpecType.get_bit_length not implemented.")

  @abstractmethod
  def parse(self, bits: list[int]):
    raise NotImplementedError("SpecType.parse not implemented.")


class Int(SpecType):
  def __init__(self, *, bits: int=0, bytes: int=0, big_endian: bool=True):
    self.bit_length = bits + bytes * 8
    self.big_endian = big_endian

  def get_bit_length(self):
    return self.bit_length

  @abstractmethod
  def parse(self, bits: list[int]):
    return SpecType.bits_to_int(self, bits, self.big_endian)


class Int8(Int):
  def __init__(self, *, big_endian: bool=True):
    super().__init__(bytes=1, big_endian=big_endian)


class Int16(Int):
  def __init__(self, *, big_endian: bool=True):
    super().__init__(bytes=2, big_endian=big_endian)


class Int32(Int):
  def __init__(self, *, big_endian: bool=True):
    super().__init__(bytes=4, big_endian=big_endian)


class Int64(Int):
  def __init__(self, *, big_endian: bool=True):
    super().__init__(bytes=8, big_endian=big_endian)


class String(SpecType):
  def __init__(self, encoding: str, length: int):
    self.encoding = encoding
    self.length = length

  def get_bit_length(self):
    return 8 * self.length

  def parse(self, bits: list[int]):
    bytes = SpecType.bits_to_bytes(self, bits)

    return bytes.decode(self.encoding)


class Packed(SpecType):
  def __init__(self, spec_types, *, names: Union[list[str], None]=None):
    if names is not None and len(spec_types) != len(names):
      raise SpecTypeError("spec_types and names must be the same length.",
                          self)

    self.spec_types = spec_types
    self.names = names

  @staticmethod
  def from_kwargs(**kwargs: dict[str, SpecType]):
    return Packed.from_dict(kwargs)

  @staticmethod
  def from_type(t: type):
    raise NotImplementedError("Packed.from_type is not implemented.")

  @staticmethod
  def from_dict(d: dict[str, SpecType]):
    return Packed(d.values(), names=d.keys())

  def get_bit_length(self):
    return sum([spec.get_bit_length() for spec in self.spec_types])

  def parse(self, bits: list[int]):
    values = []

    for type in self.spec_types:
      values.append(type.parse(bits))

    if self.names is None:
      return values
    else:
      return dict(zip(self.names, values))


class Bool(SpecType):
  def __init__(self, *, single_bit: bool=False):
    self.single_bit = single_bit

  def get_bit_length(self):
    return 1 if self.single_bit else 8

  def parse(self, bits: list[int]):
    if self.single_bit:
      return bits[0]
    else:
      return any(b != 0 for b in bits) != 0


class Bytes(SpecType):
  def __init__(self, count: int):
    self.count = count

  def get_bit_length(self):
    return self.count * 8

  def parse(self, bits: list[int]):
    return SpecType.bits_to_bytes(self, bits)


class Bits(SpecType):
  def __init__(self, count: int):
    self.bit_length = count

  def get_bit_length(self):
    return self.bit_length

  def parse(self, bits: list[int]):
    return bits


class Array(SpecType):
  def __init__(self, spec_type: SpecType, length: int):
    self.spec_type = spec_type
    self.length = length
    self.item_length = self.spec_type.get_bit_length()

  def get_bit_length(self):
    return self.item_length * self.length

  def parse(self, bits: list[int]):
    values = []

    for i in range(self.length):
      slice = bits[i * self.item_length:(i + 1) * self.item_length]
      values.append(self.spec_type.parse(slice))

    return values