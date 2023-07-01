from type_base import type_base

class custom_spec_type(type_base):
    def __init__(self, name, **members):
        self.name = name
        self.members = members

    def get_length(self):
        length = 0

        for key, spec_type in self.members.items():
            length += spec_type.get_length()
        
        return length

    def parse(self, input_bytes):
        result = {}
        start_index = 0

        for key, spec_type in self.members:
            length = spec_type.get_length()
            result[key] = spec_type.parse(input_bytes[start_index:length])
            
            start_index += length

        return result
