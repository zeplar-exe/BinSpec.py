from io import BytesIO
from .types import SpecType
from .errors import SpecError, SpecTypeError
from typing import Union, Callable, Any


class Specification:
  def __init__(self, stream: BytesIO, *, track_stream: bool=False, middleware: Callable[SpecType, Any]=None):
    self.stream: BytesIO = stream
    self.track_stream: bool = track_stream
    self.middleware: Callable[SpecType, Any] = middleware

    self.__history = []
    self.__tracked_bytes = bytearray()

    self.__bit_offset = 0
    self.__byte_offset = 0
    self.__current_byte = -1

  def get_history(self) -> list[tuple[SpecType, Any]]:
    return self.__history

  def get_tracked_bytes(self) -> bytearray:
    return self.__tracked_bytes

  def expect(self, spec_type: SpecType, *, label: Union[str, None]=None) -> Any:
    bit_length = spec_type.get_bit_length()

    if bit_length < 0:
      raise SpecTypeError("Bit length cannot be negative.", spec_type)

    bits = self.__take_bits(bit_length)
    value = spec_type.parse(bits)

    self.__history.append((spec_type, value))
    if self.middleware is not None: middleware(spec_type, value)

    return value

  def assert_eof(self) -> None:
    if len(self.stream.read(1)) > 0:
      self.fail(f"Expected end of file after {self.__byte_offset} bytes.")

  def __take_bits(self, count: int) -> list[int]:
    def next_byte():
      try:
        self.__current_byte = self.stream.read(1)[0]

        if self.track_stream:
          self.__tracked_bytes.append(self.__current_byte)
      except IndexError:
        self.fail(
            f"Ran out of bytes. Expected byte after {self.__byte_offset} bytes."
        )

    bits = []

    if self.__current_byte == -1:
      next_byte()

    while count > 0:
      count -= 1

      if self.__bit_offset == 8:
        self.__bit_offset = 0
        next_byte()
      
      # Return raw order of original bits
      bit = (self.__current_byte << self.__bit_offset) & 128
      bits.append(bit >> 7) # shift last bit to first position to return a 1
      self.__bit_offset += 1

    return bits

  def fail(self, reason: str="Manual failure.") -> None:
    raise SpecError(reason)
