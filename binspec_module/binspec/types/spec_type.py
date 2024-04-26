from abc import abstractmethod
from ..errors import SpecError, SpecTypeError
from ..utilities import bits_to_int, bits_to_bytes
from typing import Union, Any
import math
from itertools import tee, islice


class SpecType:
  @abstractmethod
  def get_bit_length(self) -> int:
    raise NotImplementedError("SpecType.get_bit_length not implemented.")

  @abstractmethod
  def parse(self, bits: bytes):
    raise NotImplementedError("SpecType.parse not implemented.")


class Int(SpecType):
  def __init__(self, *, bits: int=0, bytes: int=0, big_endian: bool=True):
    self.__bit_length = bits + bytes * 8
    self.big_endian = big_endian

  def get_bit_length(self) -> int:
    return self.__bit_length
  
  def parse(self, bits: bytes):
    return bits_to_int(bits, big_endian=self.big_endian)


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

  def parse(self, bits: bytes) -> str:
    bytes = bits_to_bytes(bits, big_endian=self.big_endian)

    return bytes.decode(self.encoding)


class Packed(SpecType):
  def __init__(self, spec_types: list[SpecType], *, names: Union[list[str], None]=None):
    if names is not None and len(spec_types) != len(names):
      raise SpecTypeError("spec_types and names must be the same length.", self)

    self.spec_types = [(spec, spec.get_bit_length()) for spec in spec_types]
    self.names = names

  @staticmethod
  def from_kwargs(**kwargs: dict[str, SpecType]) -> "Packed":
    return Packed.from_dict(kwargs)

  @staticmethod
  def from_dict(d: dict[str, SpecType]) -> "Packed":
    return Packed(d.values(), names=d.keys())

  def get_bit_length(self) -> int:
    return sum([t[1] for t in self.spec_types])

  def parse(self, bits: bytes) -> list:
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

  def parse(self, bits: bytes) -> bool:
    if self.single_bit:
      return bits[0] != 0
    else:
      return any(b != 0 for b in bits) != 0


class Bytes(SpecType):
  def __init__(self, count: int, *, big_endian: bool=True):
    self.count = count
    self.big_endian = big_endian

  def get_bit_length(self) -> int:
    return self.count * 8

  def parse(self, bits: bytes) -> bytes:
    return bits_to_bytes(self, bits, self.big_endian)


class Bits(SpecType):
  def __init__(self, count: int, *, big_endian: bool=True):
    self.bit_length = count
    self.big_endian = big_endian

  def get_bit_length(self) -> int:
    return self.bit_length

  def parse(self, bits: bytes) -> bytes:
    return bits


class Array(SpecType):
  def __init__(self, spec_type: SpecType, length: int):
    self.spec_type = spec_type
    self.length = length
    self.__item_length = self.spec_type.get_bit_length()

  def get_bit_length(self) -> int:
    return self.__item_length * self.length

  def parse(self, bits: bytes) -> Any:
    values = []

    for i in range(self.length):
      slice = bits[i * self.__item_length:(i + 1) * self.__item_length]
      values.append(self.spec_type.parse(slice))

    return values