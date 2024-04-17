from io import BytesIO
from .types import SpecType
from .errors import SpecError, SpecTypeError
from typing import Union, Callable, Any


class Specification:
  def __init__(self, stream: BytesIO, *, track_history: bool=True, track_stream: bool=False, middleware: Callable[SpecType, Any]=None):
    self.stream: BytesIO = stream
    self.track_stream: bool = track_stream
    self.track_history: bool = track_history
    self.middleware: Callable[SpecType, Any] = middleware

    self.__history = []
    self.__tracked_bytes = bytearray()

    self.__bit_offset = 0
    self.__byte_offset = 0
    self.__current_byte = -1

  def get_history(self) -> list[tuple[SpecType, Any, Union[str, None]]]:
    return self.__history

  def get_tracked_bytes(self) -> bytearray:
    return self.__tracked_bytes

  def expect(self, spec_type: SpecType, *, none_at_eof: bool=False, label: Union[str, None]=None) -> Any:
    bit_length = spec_type.get_bit_length()

    if bit_length < 0:
      raise SpecTypeError("Bit length cannot be negative.", spec_type)

    bits = self.__take_bits(bit_length, none_at_eof)

    if bits == None:
      return None

    value = spec_type.parse(bits)

    if self.track_history: 
      self.__history.append((spec_type, value, label))
    
    if self.middleware is not None: 
      middleware(spec_type, value)

    return value

  def assert_eof(self) -> None:
    if len(self.stream.read(1)) > 0:
      self.fail(f"Expected end of file after {self.__byte_offset} bytes.")

  def __take_bits(self, count: int, none_at_eof: bool) -> list[int]:
    def next_byte():
      try:
        self.__current_byte = self.stream.read(1)[0]
        
        if self.track_stream:
          self.__tracked_bytes.append(self.__current_byte)
      except IndexError:
        if none_at_eof:
          return None
        
        self.fail(
            f"Ran out of bytes. Expected byte after {self.__byte_offset} bytes."
        )

    bits = []
    
    if self.__current_byte == -1:
      next_byte()
        
      if self.__current_byte is None:
        return None
    
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

    return bits

  def fail(self, reason: str="Manual failure.") -> None:
    raise SpecError(reason)

  def show(self):
    from flask import Flask
    import webbrowser

    app = Flask("BinSpec")

    def index():
        json_spec_template = "{ bit_length: %s, label: '%s' }"
        spec_history = ",".join(map(lambda s: json_spec_template % (s[0].get_bit_length(), s[2]), self.get_history()))
        binary_string = "".join(map(lambda b: format(b, '#010b'), self.get_tracked_bytes()))

        print("SPEC HISTORY", spec_history)
        print("BINARY STIRNG", binary_string)

        with open("./binspec/ui/page.html") as f:
          html = f.read().replace("/*INSERT_SPEC_HISTORY*/", spec_history).replace("/*INSERT_BINARY_STRING*/", binary_string)
          
          return html

    app.add_url_rule("/", view_func=index)

    webbrowser.open_new_tab("http://localhost:55791")
    app.run(port=55791)
