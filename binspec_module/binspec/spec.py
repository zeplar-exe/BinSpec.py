from io import BytesIO
from .types import SpecType
from .errors import SpecError, SpecTypeError, SpecEofError
from typing import Union, Callable, Any


class Specification:
  """This class is the primary interface for parsing binary streams with :class:`SpecTypes`.
  
  Arguments:
  :param stream: BytesIO object or similar which yields bytes from a read() method.

  Keyword Arguments:
  :param track_history: flag whether to keep track of SpecTypes passed to expect(...).
  :param middleware: callable invoked whenever a SpecType successfully parses a value."""
  def __init__(self, stream: BytesIO, *, track_history: bool=True, middleware: Callable[SpecType, Any]=None):
    self.stream: BytesIO = stream
    self.middleware: Callable[SpecType, Any] = middleware

    self.__history = [] if track_history else None

    self.__bit_offset = 0
    self.__byte_offset = 0
    self.__current_byte = -1

  def get_history(self) -> list[tuple[SpecType, Any, Union[str, None]]]:
    """Get the SpecType history of this Specification. This is a list of tuples  If the track_history attribute is false, this method will return an empty array.

    :return: List of tuples containing the SpecType, its parsed value, and the optionally proivded label."""
    return self.__history

  def is_history_enabled(self):
    return self.__history != None

  def expect(self, spec_type: SpecType, *, none_at_eof: bool=False, label: Union[str, None]=None) -> Any:
    """Use the specified SpecType to parse from the bytes stream.
    
    Arguments:
    :param spec_type: the SpecType to use
    
    Keyword Arguments
    :param none_at-eof: if false, this method will raise a SpecError when attempting to read past the end of the stream. If true, this method will return None in that case."""
    bit_length = spec_type.get_bit_length()

    if bit_length < 0:
      raise SpecTypeError("Bit length cannot be negative.", spec_type)

    bits = self.__take_bits(bit_length, none_at_eof)

    if bits == None:
      return None

    value = spec_type.parse(bits)

    if self.is_history_enabled(): 
      self.__history.append((spec_type, value, label))
    
    if self.middleware is not None: 
      middleware(spec_type, value)

    return value

  def assert_eof(self) -> None:
    """Check if there are more bytes left in the stream and raise a SpecEofError if not. This method moves the stream forward by one."""
    if len(self.stream.read(1)) > 0:
      raise SpecEofError(f"Expected end of file after {self.__byte_offset} bytes.")

  def __take_bits(self, count: int, none_at_eof: bool) -> list[int]:
    def next_byte():
      try:
        self.__current_byte = self.stream.read(1)[0]
      except IndexError as err:
        if none_at_eof:
          return None
        
        raise SpecEofError(f"Ran out of bytes. Expected byte after {self.__byte_offset} bytes.") from err
    
    if self.__current_byte == -1:
      next_byte()
        
      if self.__current_byte is None:
        return None
    
    bits = bytearray()
    
    while count > 0:
      count -= 1

      if self.__bit_offset == 8:
        self.__bit_offset = 0
        next_byte()

        if self.__current_byte is None:
          return None
      
      # Return raw order of original bits
      bit = (self.__current_byte << self.__bit_offset) & 128
      bits.append(bit >> 7) # shift last bit to first position to return a 1
      self.__bit_offset += 1

    return bytes(bits)

  def fail(self, reason: str="Manual failure.") -> None:
    """Manually raise a SpecError with the given reason."""
    raise SpecError(reason)