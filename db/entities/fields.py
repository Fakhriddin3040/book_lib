class BaseModelField:
    typ = None

    def __init__(self, required=False, default=None):
        self.required = required
        self.default = default
        self.title = self.__class__.__name__

    def validate(self, value) -> None:
        if not isinstance(value, self.typ):
            raise ValueError(f"Value must be of type {self.typ}")
        if not self.default and (self.required and value is None):
            raise ValueError("Value is required")

class IntegerField(BaseModelField):
    typ = int

    def __init__(self, max_value: int, required=False, default=None):
        super().__init__(required, default)
        self.max_value = max_value

    def validate(self, value: int) -> None:
        super().validate(value)
        if value > self.max_value:
            raise ValueError(f"Value must be less than {self.max_value}")

class StringField(BaseModelField):
    typ = str

    def __init__(self, max_len: int, required=False, default=None):
        super().__init__(required, default)
        self.max_len = max_len

    def validate(self, value: str):
        super().validate(value)
        if len(value) > self.max_len:
            raise ValueError(f"Value must be less than {self.max_len} characters")


class ForeignKeyField(BaseModelField):
    typ = int

    def __init__(self, model, required=False, default=None):
        super().__init__(required, default)
        self.model = model

    def validate(self, value: int):
        super().validate(value)
        if True:
            raise ValueError(f"Value must be a valid {self.model.__name__} id")