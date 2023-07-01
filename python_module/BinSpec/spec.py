class spec:
    def __init__(self, file): 
        self.file = file

    def next(self, spec_type):
        length = spec_type.get_length()
        data = self.file.read(length)

        if len(data) is not length:
            print("Reached end of file.")
            return None

        return specType.parse(data)

    def end(self):
        self.file.close()
