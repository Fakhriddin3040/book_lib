import json
from typing import Any, Dict, List, Union

from db.entities.fields import BaseModelField
from db.layers.repositories import AVLTreeModelContainer, ModelContainerBase
from utils.algorithms import qsort
from utils.functions import file_exists, create_file_force
from environment import env


class BaseDataStorage:
    def __init__(self, model_class, model_container_class: ModelContainerBase) -> None:
        self.model_class = model_class()
        self.model_fields = {}
        self.ensure_storage()
        self.model_fields = self._get_model_fields()
        self.model_container_class = model_container_class
        self.latest_id: int = self.get_latest_id()

    def get_latest_id(self) -> int:
        raise NotImplemented("You should implement get_latest_id method ma brazaaa! Don't be lazy!")

    def get(self, **kwargs):
        raise NotImplemented("Oooooh, you should implement get method!. Let's go!")

    def create(self, **kwargs) -> Any:
        raise NotImplemented("Method create not implemented maaan. Implement it!")

    def update(self, **kwargs) -> Any:
        raise NotImplemented("You should implement update method ma brazaaa! Don't be lazy!")

    def delete(self, **kwargs) -> Any:
        raise NotImplemented("You should implement delete method ma brazaaa! Don't be lazy!")
    
    def save(self, **kwargs) -> Any:
        raise NotImplemented("You should implement save method ma brazaaa! Don't be lazy!")

    def _save_instance(self, instance: Any) -> None:
        raise NotImplemented("You should implement save_instance method ma brazaaa! Don't be lazy!")

    def search(self, **kwargs) -> Any:
        raise NotImplemented("You should implement search method ma brazaaa! Don't be lazy!")

    def get_model_instance(self, *args, **kwargs) -> Any:
        return self.model_class(*args, **kwargs)

    def _build_instance(self, **kwargs) -> Any:
        instance = self.get_model_instance()
        return instance

    def _get_model_fields(self) -> Dict[str, Any]:
        model_fields = {}
        for title, field in self.model_class.__dict__.items():
            if isinstance(field, BaseModelField):
                model_fields[title] = field
        return model_fields

    def load_model_container(self) -> None:
        raise NotImplemented("Nuuuuuuh. Without this method NIKAK. Implement it!")

#HERE: TODO. FIRST IMPLEMENT THIS BIG GIB
    def _parse_instance(self, data: Any) -> BaseModel:
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
            if key in self.model_fields:
                setattr(instance, key, value)
        return instance

    def _create_instance(self, **kwargs) -> BaseModel:
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
            if key not in self.model_fields:
                raise ValueError(f"Field {key} is not field of model {self.model_class}")
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
        raise NotImplemented("You should implement load_data method ma brazaaa! Don't be lazy!")

    def load_data(self) -> None:
        """
        Load data from storage to temporary storage.
        """
        raise NotImplemented("You should implement load_data method ma brazaaa! Don't be lazy!")
        self._load_data()

    def _write_data(self, data: Union[Any, List[Any]]) -> None:
        """
        Write data to temporary storage.
        :param data: Any | List[Any]. Data to save.
            Check for data type in your implementation.
        """
        raise NotImplemented("You should implement write_data method ma brazaaa! Don't be lazy!")

    def _save_data(self, **kwargs) -> None:
        """
        Save data to storage, using temporary storage.
        Use only self props for getting temp storage data.
        For example, when u load all data to from storage,
        you should save it into self.data prop, or smth like that niga.

        :param kwargs: Dict[str, Any]. Optional kwargs,
            if you need some options for saving data.
        """
        raise NotImplemented("You should implement save_data method ma brazaaa! Don't be lazy!")

    def init_storage(self) -> None:
        """
        Initialize storage, if it's not exists.
        """
        pass


class BaseFileDataStorage(BaseDataStorage):
    def __init__(self, filepath: str, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.filepath = filepath
        self.encoding = 'utf-8'

    def init_storage(self) -> None:
        create_file_force(self.filepath)

    def _replace_line_in_file(self, line_number: int, new_line: str) -> None:
        """
        Replace a line in the file with a new line.
        
        :param line_number: int. Line number to replace.
        :param new_line: str. New line content.
        """
        with open(self.filepath, 'r', encoding=self.encoding) as file:
            lines = file.readlines()
        
        lines[line_number] = new_line + '\n'
        
        with open(self.filepath, 'w', encoding=self.encoding) as file:
            file.writelines(lines)

    def _read_file(self) -> List[str]:
        """
        Get all lines from file.
        
        :return: List[str]. List of lines from file.
        """
        with open(self.filepath, 'r', encoding=self.encoding) as file:
            return file.readlines()


class FileDataStorage(BaseFileDataStorage):

    def __init__(
        self,
        *args,
        **kwargs
        ) -> None:
        super().__init__(
            *args,
            **kwargs
            )
        """
        model_fields: Dict[str, BaseModelField]. Fields of model,
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
                    'name': 0,
                    'age': 1,
                    'email': 2,
                }
                This done for fast access to fields by index.
                You need not to parse fields names each time,
        """
        self.model_fields_map = self.get_sorted_model_fields()
        self.fields_idx_map = self.get_fields_indexes_map()
        self.text_sep = '<-->'

    def _parse_instance(self, data: str) -> BaseModel:
        instance = self.get_model_instance()
        values = data.strip().split(self.text_sep)
        for index, value in enumerate(data.split(self.text_sep)):
            title = self.fields_idx_map[index]
            field = self.model_fields_map[title]
            field.validate(value)
            setattr(instance, title, value)
        return instance

    def unparse_instance(self, instance: BaseModel) -> str:
        return self.text_sep.join(
            [str(getattr(instance, title)) for title in self.fields_idx_map.keys()]
        )

    def _save_instance(self, instance):
        with open(self.filepath, 'a', encoding=self.encoding) as f:
            if not instance.id:
                instance.id = self.latest_id + 1
                self.latest_id += 1
                f.write(self.unparse_instance(instance) + '\n')
            else:
                line_number = self._find_line_number_by_field('id', instance.id, f)
                self._replace_line_in_file(line_number, self.unparse_instance(instance))

    def get_latest_id(self):
        return self._read_file()[-1].split(self.text_sep)[
            self.fields_idx_map['id']
        ]

    def _find_line_number_by_field(self, field: str, value: Any, f = None) -> int:
        """
        Find line number by field value
        :param field: str. Field name
        :param value: Any. Field value
        :return: int. Line number
        :raises: ValueError if field is not model field
        """
        if field not in self.model_fields_map:
            raise ValueError(f"Field {field} is not field of model {self.model_class}")
        if not f:
            with open(self.filepath, 'r', encoding=self.encoding) as f:
                for index, line in enumerate(f.readlines()):
                    instance = self._parse_instance(line)
                    if getattr(instance, field) == value:
                        return index
        else:
            for index, line in enumerate(f.readlines()):
                instance = self._parse_instance(line)
                if getattr(instance, field) == value:
                    return index

    def load_data(self, **kwargs) -> None:
        self.data = self._load_data()
        for line in self.data:
            instance = self._parse_instance(line)
            self.init_model_container()
            self.model_container.add(instance)

    def init_model_container(self) -> ModelContainerBase:
        return self.model_container_class()

    def get_sorted_model_fields(self):
        new_model_fields = {}
        sorted_titles = qsort(
            arr=self.model_fields_map.keys(),
        )
        for title in sorted_titles:
            new_model_fields[title] = self.model_fields_map[title]
        return new_model_fields

    def get_fields_indexes_map(self) -> Dict[str, int]:
        return {title: index for index, title in enumerate(self.model_fields_map.keys())}

    def _load_data(self) -> List[str]:
        return self._read_file()

    def init_storage(self) -> None:
        super().init_storage()
        with open(self.filepath, 'w', encoding=self.encoding) as f:
            headers = self.text_sep.join(self.fields_idx_map.keys())
            f.write(headers + '\n')

    # def parse(self, **kwargs) -> Any:
    #     """
    #     Filters data by keyword args, where:
    #         key: field name
    #         value: field value
    #     :param kwargs: Dict[str, Any] of course.
    #     :return: Dict[str, Any]
    #     raises: ValueError if no kwargs provided
    #     raises: ValueError if no data found
    #     raises: ValueError if more than one data found
    #     raises: ValueError if key is not model field
    #     """
    #     data = self._read_file()
    #     with open(self.filepath, 'r', encoding=self.encoding) as f:
    #         f.readlines() #TODO: REVIEW



class JsonDataStorage(BaseDataStorage):
    def __init__(self, model, filepath: str) -> None:
        self.filepath = filepath
        super().__init__(model)
        self.init_storage()
        self.data = self.parse()


    def get(self, **kwargs) -> Dict[str, Any]:
        """
        Filters data by keyword args, where:
            key: field name
            value: field value
        :param kwargs: Dict[str, Any] of course.
        :return: Dict[str, Any]
        raises: ValueError if no kwargs provided
        raises: ValueError if no data found
        raises: ValueError if more than one data found
        raises: ValueError if key is not model field
        """
        if not kwargs:
            return self.data
        filtered = []
        for item in self.data:
            for key, value in kwargs.items():
                if item.get(key) == value:
                    filtered.append(item)
                    

    def parse(self) -> Dict[str, Any]:
        with open(self.filepath, 'r', encoding='utf-8') as file:
            return json.load(file)
