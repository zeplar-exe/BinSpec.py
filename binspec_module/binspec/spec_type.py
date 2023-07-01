from spec_type_base import spec_type_base

class string(spec_type_base):
    def __init__(self, encoding, length):
        self.encoding = encoding

    def get_length(self):
        return self.length

    def parse(self, input_bytes):
        return input_bytes.decode(encoding)

class integer(spec_type_base):
    def __init__(self, byte_length):
        self.byte_length = byte_length

    def get_length(self):
        return self.byte_length

    def parse(self, input_bytes):
        return int.from_bytes(input_bytes, "big")
