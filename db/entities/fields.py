

from db.base import BaseEntityField


class IntegerField(BaseEntityField):
    typ = int

    def __init__(self, max_value: int = None, required=False, default=None):
        super().__init__(required, default)
        self.max_value = max_value

    def validate(self, value: int) -> None:
        super().validate(value)
        if hasattr(self, "max_value") and self.max_value:
            if value > self.max_value:
                raise ValueError(f"Value must be less than {self.max_value}")


class StringField(BaseEntityField):
    typ = str

    def __init__(self, max_len: int, required=False, default=None):
        super().__init__(required, default)
        self.max_len = max_len

    def validate(self, value: str):
        super().validate(value)
        if hasattr(self, "value") and len(value) > self.max_len:
            raise ValueError(f"Value must be less than {self.max_len} characters")


class ForeignKeyField(BaseEntityField):
    typ = int

    def __init__(self, model, required=False, default=None):
        super().__init__(required, default)
        self.model = model

    def validate(self, value: int):
        super().validate(value)
        if True:
            raise ValueError(f"Value must be a valid {self.model.__name__} id")
