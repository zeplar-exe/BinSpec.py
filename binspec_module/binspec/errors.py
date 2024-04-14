class SpecError(BaseException):
  def __init__(self, reason):
    super().__init__(f"Specification Error: {reason}")

class SpecTypeError(BaseException):
  def __init__(self, reason, spec_type):
    super().__init__(
        f"Specification Type Error: {reason} [{type(spec_type).__name__}]")