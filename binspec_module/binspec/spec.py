from io import BytesIO
from spec_type import SpecType
from errors import SpecError, SpecTypeError
from typing import Union, Callable, Any


class Specification:
  def __init__(self, stream: BytesIO, *, track_stream: bool=False, middleware: Callable[SpecType, Any]=None, **kwargs):
    self.stream = stream
    self.track_stream = track_stream
    self.__dict__.update(kwargs)

    self.tracked_spec = []
    self.tracked_bytes = bytearray()

    self.__bit_offset = 0
    self.__byte_offset = 0
    self.__current_byte = -1

  def expect(self, spec_type: SpecType, *, label: Union[str, None]=None):
    bit_length = spec_type.get_bit_length()

    if bit_length < 0:
      raise SpecTypeError("Bit length cannot be negative.", spec_type)

    bits = self.__take_bits(bit_length)
    value = spec_type.parse(bits)

    self.tracked_spec.append((spec_type, value))
    if middleware is not None: middleware(spec_type, value)

  def assert_eof(self):
    if len(self.stream.read(1)) > 0:
      raise SpecError(f"Expected end of file after {self.__byte_offset} bytes.")

  def __take_bits(self, count: int):
    def next_byte():
      try:
        self.__current_byte = self.stream.read(1)[0]

        if self.track_stream:
          self.tracked_bytes.append(self.__current_byte)
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
      bit >>= 7  # shift last bit to first position to return a 1
      bits.append(bit)
      self.__bit_offset += 1

    return bits

  def fail(self, reason: str="Manual failure."):
    raise SpecError(reason)
