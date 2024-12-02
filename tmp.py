from db.base import BaseEntity
from db.entities.fields import IntegerField, StringField
from utils.settings import lazy_settings


class UserEntity(BaseEntity):
    storage = lazy_settings.DEFAULT_DATA_STORAGE()

    id = IntegerField()
    username = StringField(max_len=50, required=True)
    age = IntegerField(required=True)

user = UserEntity.create(age=12, username="python")
user.username = "Python1"
user.save()

got_user = UserEntity.storage.get(id=user.id)