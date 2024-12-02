# from db.base import BaseEntity
# from db.entities.fields import IntegerField, StringField


# class UserEntity(BaseEntity):
#     id = IntegerField()
#     username = StringField(max_len=50, required=True)

# user = UserEntity.storage.get(id=1)


class Model:
    @classmethod
    def _setup_storage(cls, storage):
        cls.storage = storage

class NeedModel:
    def __init__(self):
        