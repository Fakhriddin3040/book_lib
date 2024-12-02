from typing import Any, Dict, List, Union
from utils.settings import lazy_settings


class EntityMeta(type):
    def __new__(cls, name, bases, dct):

        new_cls = super().__new__(cls, name, bases, dct)
        new_cls._init_storage()
        return new_cls


class BaseEntity(metaclass=EntityMeta):
    fields = {}

    @classmethod
    def _init_storage(cls) -> "BaseDataStorage":
        if hasattr(cls, "storage"):
            cls.storage._init(cls)

    def __init__(self, **kwargs):
        self.fields = self._get_fields()
        self._set_values(**kwargs)

    def _set_values(self, **kwargs) -> None:
        for f, v in kwargs.items():
            if f not in self.fields:
                raise ValueError(
                    f"Model {self.__class__.__name__} has no attribute {f}"
                )
            self.fields[f].value = v

    @classmethod
    def create(cls, **kwargs) -> "BaseEntity":
        instance = cls(**kwargs)
        instance.save()
        return instance

    def save(self):
        self.storage.save(self)

    def delete(self):
        self.storage.delete(self)

    def update(self, **kwargs):
        for f, v in kwargs.items():
            if f in self.fields:
                self.fields[f].value = v

    def __getattribute__(self, name):
        if name in ("fields", "_get_fields", "__dict__"):
            return object.__getattribute__(self, name)

        fields = object.__getattribute__(self, "__dict__").get("fields", {})
        if name in fields:
            field = fields[name]
            if hasattr(field, "value"):
                return field.value
            raise AttributeError(
                f"'Field' object for '{name}' has no attribute 'value'"
            )
        return object.__getattribute__(self, name)

    def __setattr__(self, name, value):
        fields = self.__dict__.get("fields", {})

        if name in fields:
            field = fields[name]
            if hasattr(field, "value"):
                field.value = value
                return
            raise AttributeError(
                f"'Field' object for '{name}' has no attribute 'value'"
            )

        object.__setattr__(self, name, value)

    @classmethod
    def _get_fields(cls) -> Dict[str, "BaseEntityField"]:
        if hasattr(cls, "_cached_fields"):
            return cls._cached_fields

        fields = {}

        for base in cls.__mro__:
            fields.update(
                {f: v for f, v in vars(base).items() if isinstance(v, BaseEntityField)}
            )
        cls._cached_fields = fields
        return fields


class BaseDataStorage:

    def _init(self, model_class: BaseEntity, *args, **kwargs):
        """
        model_fields: Dict[str, BaseEntityField]. Fields of model,
            where key is field name and value is field instance.
        fields_idx_map: Dict[str, int]. Map of fields indexes,
            where key is field name and value is field index
            on file storage, where fields are separated by separator.

            For example:
                model_fields = {
                    'name': StrField(),
                    'age': IntField(),
                    'email': EmailField(),
                    }
                fields_idx_map will equal to:
                {
                    'age': 0,
                    'email': 1,
                    'name': 2,
                }
                This done for fast access to fields by index.
                You need not to parse fields names each time,
        """
        self.model_class = model_class
        self.model_fields_map = self._get_model_fields()
        self.container_class: BaseModelContainer = lazy_settings.DEFAULT_MODEL_CONTAINER

    def get_latest_id(self) -> int:
        raise NotImplementedError(
            "You should implement get_latest_id method ma brazaaa! Don't be lazy!"
        )

    def get(self, **kwargs):
        raise NotImplementedError("Oooooh, you should implement get method!. Let's go!")

    def create(self, **kwargs) -> Any:
        raise NotImplementedError("Method create not implemented maaan. Implement it!")

    def update(self, **kwargs) -> Any:
        raise NotImplementedError(
            "You should implement update method ma brazaaa! Don't be lazy!"
        )

    def delete(self, **kwargs) -> Any:
        raise NotImplementedError(
            "You should implement delete method ma brazaaa! Don't be lazy!"
        )

    def save(self, instance) -> Any:
        raise NotImplementedError(
            "You should implement save method ma brazaaa! Don't be lazy!"
        )

    def _save_instance(self, instance: Any) -> None:
        raise NotImplementedError(
            "You should implement save_instance method ma brazaaa! Don't be lazy!"
        )

    def search(self, **kwargs) -> Any:
        raise NotImplementedError(
            "You should implement search method ma brazaaa! Don't be lazy!"
        )

    def get_model_instance(self, *args, **kwargs) -> Any:
        return self.model_class(*args, **kwargs)

    def _build_instance(self, **kwargs) -> Any:
        instance = self.get_model_instance()
        return instance

    def _get_model_fields(self) -> Dict[str, Any]:
        return self.model_class._get_fields()

    def load_model_container(self) -> None:
        raise NotImplementedError("Nuuuuuuh. Without this method NIKAK. Implement it!")

    # HERE: TODO. FIRST IMPLEMENT THIS BIG GIB
    def _parse_instance(self, data: Any) -> BaseEntity:
        """
        Parse model instance from data

        :params data: Any. Source for model instance creation
        :return: Any. Model instance
        :validation:
            - data should be dict
            - data should have all model fields
            - data should have only model fields
        """
        instance = self.get_model_instance()
        for key, value in data.items():
            if key in self.model_fields_map:
                setattr(instance, key, value)
        return instance

    def _create_instance(self, **kwargs) -> BaseEntity:
        """
        Create model instance from kwargs

        :params kwargs: Dict[str, Any]. Fields values
        :return: Any. Model instance
        :validation:
            - kwargs should have all model fields
            - kwargs should have only model fields
        """
        instance = self.get_model_instance()
        for key, value in kwargs.items():
            if key not in self.model_fields_map:
                raise ValueError(f"Field {key} is not field of model {self.model}")
            setattr(instance, key, value)
        self.model_container.add(instance)
        self._save_instance(instance)
        return instance

    def _load_data(self) -> Any:
        """
        Obtain data from storage. Its additional abstraction layer
        for loading data from storage. Implement only for getting data
        as it is. No parsing, no filtering, no sorting, no nothing.
        Just load data from storage and return it.

        :return: I thing niga, it must be List[str] or List[Dict[str, Any]].
            At all, i don't know bro, it's up to you.
        """
        raise NotImplementedError(
            "You should implement load_data method ma brazaaa! Don't be lazy!"
        )

    def _load_instances(self) -> None:
        """
        Load data from storage to temporary storage.
        """
        raise NotImplementedError(
            "You should implement load_data method ma brazaaa! Don't be lazy!"
        )
        self._load_data()

    def _write_data(self, data: Union[Any, List[Any]]) -> None:
        """
        Write data to temporary storage.
        :param data: Any | List[Any]. Data to save.
            Check for data type in your implementation.
        """
        raise NotImplementedError(
            "You should implement write_data method ma brazaaa! Don't be lazy!"
        )

    def _save_data(self, **kwargs) -> None:
        """
        Save data to storage, using temporary storage.
        Use only self props for getting temp storage data.
        For example, when u load all data to from storage,
        you should save it into self.data prop, or smth like that niga.

        :param kwargs: Dict[str, Any]. Optional kwargs,
            if you need some options for saving data.
        """
        raise NotImplementedError(
            "You should implement save_data method ma brazaaa! Don't be lazy!"
        )

    def init_storage(self) -> None:
        """
        Initialize storage, if it's not exists.
        """
        pass


class BaseEntityField:
    typ = None

    def __init__(self, required=False, default=None):
        self.required = required
        self.default = default
        self.title = self.__class__.__name__
        self.value = default

    def set_default(self):
        if self.default:
            self.value = self.default

    def validate(self, value) -> None:
        if not isinstance(value, (self.typ, type(None))):
            raise ValueError(f"Value must be of type {self.typ}")

    def __setattr__(self, name, value):
        if name == "value":
            self.validate(value)
        super().__setattr__(name, value)


class BaseModelContainer:
    def insert(self, value):
        raise NotImplementedError("Method insert not implemented maaan. Implement it!")

    def search(self, value):
        raise NotImplementedError("Method search not implemented maaan. Implement it!")

    def delete(self, value):
        raise NotImplementedError("Method delete not implemented maaan. Implement it!")

    def __str__(self):
        """
        Optional method for string representation of container
        """
        return "Whatassssup! I'm a container! Huhuhu! Enough info for you! o_o Ahahaha!"
