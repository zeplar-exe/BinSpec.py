from type_base import type_base

class string(type_base):
    def __init__(self, encoding, length):
        self.encoding = encoding

    def get_length(self):
        return self.length

    def parse(self, input_bytes):
        return input_bytes.decode(encoding)

class integer(type_base):
    def __init__(self, byte_length):
        self.byte_length = byte_length

    def get_length(self):
        return self.byte_length

    def parse(self, input_bytes):
        return int.from_byte(input_bytes)
