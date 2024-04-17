from abc import abstractmethod
from ..errors import SpecError, SpecTypeError
from typing import Union, Any
import math
from itertools import tee, islice


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
    byte_count = math.ceil(len(bits) / 8)
    b = bytearray()

    if not big_endian:
      bits = list(reversed(bits))
    
    for i in range(0, byte_count * 8, 8):
      byte = 0

      for j in range(8):
        byte <<= 1
        
        if (i + j) >= len(bits):
          break # break out because we don't have any bits left 
        else:
          if bits[i + j] == 0:
            pass # bit shift adds the zero
          else:
            byte |= 1

          if (i + j + 1) >= len(bits):
            break # avoid extra bit shift if this is the last bit
      
      b.append(byte)

    if byte_count > 1 and (len(bits) % 8) != 0:
      excess_count = len(bits) % 8
      b[-1] <<= excess_count

      create_pairs = lambda l: [(l[i], l[i + 1], i, i + 1) for i in range(len(l) - 1)]
      shifted_b = bytearray(len(b))

      for byte_right, byte_left, byte_right_index, byte_left_index in create_pairs(list(reversed(b))):
        for i in range(excess_count):
          byte_right >>= 1

          if (byte_left & 1) != 0:
            byte_right |= 128

          byte_left >>= 1
        
        shifted_b[byte_right_index] = byte_right
        shifted_b[byte_left_index] = byte_left
    
      b = bytearray(reversed(shifted_b))

    n = int.from_bytes(b, byteorder="big")

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

  def get_bit_length(self) -> int:
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
  def __init__(self, encoding: str, length: int, *, big_endian: bool=True):
    self.encoding = encoding
    self.length = length
    self.big_endian = big_endian

  def get_bit_length(self) -> int:
    return 8 * self.length

  def parse(self, bits: list[int]) -> Any:
    bytes = SpecType.bits_to_bytes(self, bits, big_endian=self.big_endian)

    return bytes.decode(self.encoding)


class Packed(SpecType):
  def __init__(self, spec_types: list[SpecType], *, names: Union[list[str], None]=None):
    if names is not None and len(spec_types) != len(names):
      raise SpecTypeError("spec_types and names must be the same length.",
                          self)

    self.spec_types = [(spec, spec.get_bit_length()) for spec in spec_types]
    self.names = names

  @staticmethod
  def from_kwargs(**kwargs: dict[str, SpecType]) -> "Packed":
    return Packed.from_dict(kwargs)

  @staticmethod
  def from_type(t: type) -> "Packed":
    raise NotImplementedError("Packed.from_type is not implemented.")

  @staticmethod
  def from_dict(d: dict[str, SpecType]) -> "Packed":
    return Packed(d.values(), names=d.keys())

  def get_bit_length(self) -> int:
    return sum([t[1] for t in self.spec_types])

  def parse(self, bits: list[int]) -> Any:
    values = []
    i = 0

    for spec_type, bit_length in self.spec_types:
      bit_slice = bits[i:i + bit_length]
      values.append(spec_type.parse(bit_slice))
      i += bit_length

    if self.names is None:
      return values
    else:
      return dict(zip(self.names, values))


class Bool(SpecType):
  def __init__(self, *, single_bit: bool=False):
    self.single_bit = single_bit

  def get_bit_length(self) -> int:
    return 1 if self.single_bit else 8

  def parse(self, bits: list[int]) -> Any:
    if self.single_bit:
      return bits[0] != 0
    else:
      return any(b != 0 for b in bits) != 0


class Bytes(SpecType):
  def __init__(self, count: int):
    self.count = count

  def get_bit_length(self) -> int:
    return self.count * 8

  def parse(self, bits: list[int]) -> Any:
    return SpecType.bits_to_bytes(self, bits)


class Bits(SpecType):
  def __init__(self, count: int, *, parse_as_bytes: bool=False):
    self.bit_length = count
    self.parse_as_bytes = parse_as_bytes

  def get_bit_length(self) -> int:
    return self.bit_length

  def parse(self, bits: list[int]) -> Any:
    return SpecType.bits_to_bytes(self, bits) if self.parse_as_bytes else bits


class Array(SpecType):
  def __init__(self, spec_type: SpecType, length: int):
    self.spec_type = spec_type
    self.length = length
    self.item_length = self.spec_type.get_bit_length()

  def get_bit_length(self) -> int:
    return self.item_length * self.length

  def parse(self, bits: list[int]) -> Any:
    values = []

    for i in range(self.length):
      slice = bits[i * self.item_length:(i + 1) * self.item_length]
      values.append(self.spec_type.parse(slice))

    return values