class spec_type_base:
    def get_length(self):
        raise NotImplementedError("get_length() must be implemented.")

    def parse(self, input_bytes):
        raise NotImplementedError("parse(inputBytes) must be implemented.")
