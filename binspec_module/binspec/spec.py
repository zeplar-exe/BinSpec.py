from spec_eof import SPEC_EOF

class spec:
    def __init__(self, file): 
        self.file = file
        self.history = list()

    def next(self, spec_type):
        length = spec_type.get_length()
        data = self.file.read(length)

        self.history.append(spec_type)

        if len(data) is not length:
            return SPEC_EOF()

        return spec_type.parse(data)

    def get_history(self):
        return self.history

    def end(self):
        self.file.close()
