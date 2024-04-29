from abc import abstractmethod
from ..errors import SpecError, SpecTypeError
from ..utilities import bits_to_int, bits_to_bytes
from typing import Union, Any
import math
from itertools import tee, islice


class SpecType:
  """Base class for parsable binary types."""
  @abstractmethod
  def get_bit_length(self) -> int:
    """:return: The number of bits to parse and pass to this SpecType."""
    raise NotImplementedError("SpecType.get_bit_length not implemented.")

  @abstractmethod
  def parse(self, bits: bytes) -> Any:
    """Parses the given bits into a python object.

    Arguments
    :param bits: A :class:`bytes` object where every byte is a 0 or a 1 to represent individual bits.
    
    :return: A python object."""
    raise NotImplementedError("SpecType.parse not implemented.")


class Int(SpecType):
  """:class:`SpecType` which parses an integer of the given size in bits and bytes. The resulting integer is `bytes * 8 + bits` bits long. Parses as a python integer.
  
  Arguments
  :param bytes: Number of bytes to read parse.
  :param bits: Number of additional bits to read parse.

  Keyword Arguments
  :param big_endian: Flag whether to parse the integer with big or little endianness, big endian being right-to-left and little endian left-to-right."""
  def __init__(self, bytes: int=0, bits: int=0, *, big_endian: bool=True):
    self.__bit_length = bits + bytes * 8
    self.big_endian = big_endian

  def get_bit_length(self) -> int:
    return self.__bit_length
  
  def parse(self, bits: bytes):
    return bits_to_int(bits, big_endian=self.big_endian)


class Int8(Int):
  """:class:`SpecType` which parses an 8-bit integer.
  
  Keyword Arguments
  :param big_endian: Flag whether to parse the integer with big or little endianness, big endian being right-to-left and little endian left-to-right."""
  def __init__(self, *, big_endian: bool=True):
    super().__init__(bytes=1, big_endian=big_endian)


class Int16(Int):
  """:class:`SpecType` which parses a 16-bit integer.
  
  Keyword Arguments
  :param big_endian: Flag whether to parse the integer with big or little endianness, big endian being right-to-left and little endian left-to-right."""
  def __init__(self, *, big_endian: bool=True):
    super().__init__(bytes=2, big_endian=big_endian)


class Int32(Int):
  """:class:`SpecType` which parses a 32-bit integer.
  
  Keyword Arguments
  :param big_endian: Flag whether to parse the integer with big or little endianness, big endian being right-to-left and little endian left-to-right."""
  def __init__(self, *, big_endian: bool=True):
    super().__init__(bytes=4, big_endian=big_endian)


class Int64(Int):
  """:class:`SpecType` which parses a 64-bit integer.
  
  Keyword Arguments
  :param big_endian: Flag whether to parse the integer with big or little endianness, big endian being right-to-left and little endian left-to-right."""
  def __init__(self, *, big_endian: bool=True):
    super().__init__(bytes=8, big_endian=big_endian)


class String(SpecType):
  """:class:`SpecType` which parses a string of the given character length and encoding.

  Arguments
  :param encoding: The encoding to parse characters in. This value is passed to `bytes.decode`.
  
  Keyword Arguments
  :param big_endian: Flag whether to parse the individual characters with big or little endianness, big endian being right-to-left and little endian left-to-right."""
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
  """:class:`SpecType` which parses an array of the specified varying :class:`SpecType`s.
  
  Arguments
  :param spec_types: An array of :class:`SpecType`s to be parsed in order.

  Keyword Arguments
  :param names: A list of names corresponding to the `spec_types` argument. If this argument is set, a dictionary will be returned instead of an array with each name as a key and the corresponding parsed value as the value. Must be the same length as `spec_types`.
  """
  def __init__(self, spec_types: list[SpecType], *, names: Union[list[str], None]=None):
    if names is not None and len(spec_types) != len(names):
      raise SpecTypeError("spec_types and names must be the same length.", self)

    self.spec_types = [(spec, spec.get_bit_length()) for spec in spec_types]
    self.names = names

  @staticmethod
  def from_kwargs(**kwargs: dict[str, SpecType]) -> "Packed":
    """Created a :class:`Packed` from keyword arguments. Argument values must be :class:`SpecType`s. This will result in a dictionary being parsed with the parsed values of the :class:`SpecType`s as values."""
    return Packed.from_dict(kwargs)

  @staticmethod
  def from_dict(d: dict[str, SpecType]) -> "Packed":
    """Created a :class:`Packed` from a dictionary of name-SpecType pairs. Dictionary values must be :class:`SpecType`s. This will result in a dictionary being parsed with the parsed values of the :class:`SpecType`s as values."""
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
  """:class:`SpecType` which parses a boolean.
  
  Keyword Arguments
  :param single_bit: Flag whether to read only one bit to create a boolean. If false, a whole byte is read instead. If you want differing behavior, just use :class:`Int` instead.
  
  :return: False if the read byte (or bit) is 0, otherwise True."""
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
  """SpecType purely to read raw the given number of bytes. Parses as a bytes object.
  
  Arguments
  :param count: Number of bytes to read.

  Keyword Arguments
  :param big_endian: Flag whether to parse the bytes with big or little endianness, big endian being right-to-left and little endian left-to-right."""
  def __init__(self, count: int, *, big_endian: bool=True):
    self.count = count
    self.big_endian = big_endian

  def get_bit_length(self) -> int:
    return self.count * 8

  def parse(self, bits: bytes) -> bytes:
    return bits_to_bytes(bits, big_endian=self.big_endian)


class Bits(SpecType):
  """SpecType to read the given number of bits. Parses as a :class:`bytes` object wherin every byte is a 1 or 0.
  
  Arguments:
  :param count: Number of bits to read."""
  def __init__(self, count: int):
    self.bit_length = count

  def get_bit_length(self) -> int:
    return self.bit_length

  def parse(self, bits: bytes) -> bytes:
    return bits


class Array(SpecType):
  """SpecType to return an array of `length` size containing the parsed values of the given :class:`SpecType`.
  
  Arguments:
  :param spec_type: :class:`SpecType` to parse.
  :param length: Number of elements to parse using the given :class:`SpecType`."""
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