from spec_type_base import spec_type_base

class custom_spec_enum(spec_type_base):
    def __init__(self, name, spec_type, **members):
        self.name = name
        self.spec_type = spec_type
        self.members = members

    def get_length(self):
        return self.spec_type.get_length()

    def parse(self):
        return self.spec_type.parse()
