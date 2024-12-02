import json
import os
from typing import Any, Dict, List, Union

from db.base import BaseDataStorage
from db.types import BaseEntity, BaseModelContainer
from src.utils.functions import create_file_force
from utils.settings import lazy_settings


class BaseFileDataStorage(BaseDataStorage):
    def __init__(self, *args, **kwargs) -> None:
        model = kwargs['model']
        self.filepath = os.path.join(
            lazy_settings.DATA_DIR, f"{model.__class__.__name__.lower()}.{self.file_format}"
        )
        super().__init__(*args, **kwargs)
        self.encoding = "utf-8"

    def init_storage(self) -> None:
        create_file_force(self.filepath)

    def ensure_storage(self) -> None:
        if not os.path.exists(self.filepath):
            self.init_storage()

    def _replace_line_in_file(self, line_number: int, new_line: str) -> None:
        """
        Replace a line in the file with a new line.

        :param line_number: int. Line number to replace.
        :param new_line: str. New line content.
        """
        with open(self.filepath, "r", encoding=self.encoding) as file:
            lines = file.readlines()

        lines[line_number] = new_line + "\n"

        with open(self.filepath, "w", encoding=self.encoding) as file:
            file.writelines(lines)

    def _read_file(self) -> List[str]:
        """
        Get all lines from file.

        :return: List[str]. List of lines from file.
        """
        with open(self.filepath, "r", encoding=self.encoding) as file:
            return file.readlines()


class FileDataStorage(BaseFileDataStorage):

    def __getattr__(self, name):
        if not self.model:
            raise ValueError("Model is not set")

    def _init(self, *args, **kwargs):
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
        self.file_format = "txt"
        super()._init(*args, **kwargs)
        self.text_sep = "<-->"
        self.data: List[str] = []
        self.model_fields_map = self.get_sorted_model_fields()
        self.fields_idx_map = self.get_fields_indexes_map()
        self.ensure_storage()
        self.latest_id = self.get_latest_id()

    def get(self, id: int) -> Dict[str, Any]:
        instance = self._get_from_container(id=id)
        if not instance:
            raise ValueError(f"No {self.model.__name__} with id {id}")
        return instance

    def _get_from_container(self, id: int) -> Union[BaseEntity, None]:
        return self.container_class.search(value=id)

    def _parse_instance(self, data: str) -> BaseEntity:
        instance = self.get_model_instance()
        values = data.strip().split(self.text_sep)
        fields_map_list = list(self.fields_idx_map.keys())

        for idx, value in enumerate(values):
            field_name = fields_map_list[idx]
            field = self.model_fields_map[field_name]
            field.validate(value)
            setattr(instance, field_name, value)
        return instance

    def unparse_instance(self, instance: BaseEntity) -> str:
        return self.text_sep.join(
            [str(getattr(instance, title)) for title in self.fields_idx_map.keys()]
        )

    def save(self, instance):
        if not instance.id:
            instance.id = self.latest_id + 1
            self.latest_id += 1
            with open(self.filepath, "a", encoding=self.encoding) as f:
                f.write(self.unparse_instance(instance) + "\n")
        else:
            line_number = self._find_line_number_by_field("id", instance.id)
            print(line_number, instance.id)
            self._replace_line_in_file(line_number, self.unparse_instance(instance))

    def get_latest_id(self):
        data = self._read_file()
        if not data:
            return 0
        last_line = data[-1]
        value = last_line.split(self.text_sep)[self.fields_idx_map["id"]]
        return int(value)

    def _find_line_number_by_field(self, field: str, value: Any) -> Union[int, None]:
        """
        Find line number by field value
        :param field: str. Field name
        :param value: Any. Field value
        :return: int. Line number
        :raises: ValueError if field is not model field
        """
        if field not in self.model_fields_map:
            raise ValueError(f"Field {field} is not field of model {self.model}")

        with open(self.filepath, "r", encoding=self.encoding) as f:
            for index, line in enumerate(f.readlines()):
                if line.split(self.text_sep)[self.fields_idx_map[field]] == value:
                    return index
        return None

    def load_data(self, **model_container_kwargs) -> None:
        self.data = self._load_data()
        self.init_model_container(**model_container_kwargs)
        for line in self.data:
            instance = self._parse_instance(line)
            self.model_container.add(instance)

    def init_model_container(self, **kwargs) -> BaseModelContainer:
        return self.container_class(**kwargs)

    def get_sorted_model_fields(self):
        return {
            field: self.model_fields_map[field]
            for field in sorted(self.model_fields_map.keys())
        }

    def get_fields_indexes_map(self) -> Dict[str, int]:
        return {
            field: index for index, field in enumerate(self.model_fields_map.keys())
        }

    def _load_data(self) -> List[str]:
        return self._read_file()

    def init_storage(self) -> None:
        super().init_storage()
        with open(self.filepath, "w", encoding=self.encoding):
            pass

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
        with open(self.filepath, "r", encoding="utf-8") as file:
            return json.load(file)


# class FileDataStorage(BaseFileDataStorage):
#     def __init__(self, *args, **kwargs) -> None:
#         super().__init__(*args, **kwargs)

#         """
#         model_fields_map: Dict[str, BaseEntityField]. Fields of the model,
#             where the key is the field name and the value is the field instance.
#         fields_idx_map: Dict[str, int]. Map of field indexes,
#             where the key is the field name and the value is the field index
#             in the file storage.
#         """
#         self.model_fields_map = self.get_sorted_model_fields()
#         self.fields_idx_map = self.get_fields_indexes_map()
#         self.text_sep = '<-->'
#         self.data = []
#         self.latest_id = 0

#     def _parse_instance(self, data: str) -> BaseEntity:
#         """
#         Parses a line of text into a model instance.
#         """
#         instance = self.get_model_instance()
#         values = data.strip().split(self.text_sep)

#         for index, value in enumerate(values):
#             if index not in self.fields_idx_map.values():
#                 raise ValueError(f"Invalid field index: {index}")

#             field_name = list(self.fields_idx_map.keys())[index]
#             field = self.model_fields_map[field_name]
#             field.validate(value)
#             setattr(instance, field_name, value)

#         return instance

#     def unparse_instance(self, instance: BaseEntity) -> str:
#         """
#         Converts a model instance back to a string representation.
#         """
#         return self.text_sep.join(
#             [str(getattr(instance, field)) for field in self.fields_idx_map.keys()]
#         )

#     def _save_instance(self, instance: BaseEntity) -> None:
#         """
#         Saves a single instance to the file, either by appending it or updating an existing one.
#         """
#         if not instance.id:
#             instance.id = self.latest_id + 1
#             self.latest_id += 1
#             with open(self.filepath, 'a', encoding=self.encoding) as f:
#                 f.write(self.unparse_instance(instance) + '\n')
#         else:
#             line_number = self._find_line_number_by_field("id", instance.id)
#             self._replace_line_in_file(line_number, self.unparse_instance(instance))

#     def get_latest_id(self) -> int:
#         """
#         Retrieves the latest ID from the file.
#         """
#         data = self._read_file()
#         if not data:
#             return 0  # File is empty
#         last_line = data[-1]
#         return int(last_line.split(self.text_sep)[self.fields_idx_map['id']])

#     def _find_line_number_by_field(self, field: str, value: Any) -> int:
#         """
#         Finds the line number by matching a field with a specific value.
#         """
#         if field not in self.model_fields_map:
#             raise ValueError(f"Field {field} is not a field of the model {self.model}.")

#         with open(self.filepath, 'r', encoding=self.encoding) as f:
#             for index, line in enumerate(f):
#                 instance = self._parse_instance(line)
#                 if getattr(instance, field) == value:
#                     return index

#         raise ValueError(f"No line found with {field} = {value}.")

#     def _load_data(self) -> List[str]:
#         """
#         Reads all lines from the file.
#         """
#         try:
#             with open(self.filepath, 'r', encoding=self.encoding) as f:
#                 return f.readlines()
#         except FileNotFoundError:
#             return []

#     def load_data(self) -> None:
#         """
#         Loads all data from the file into the model container.
#         """
#         self.data = self._load_data()
#         self.model_container = self.init_model_container()

#         for line in self.data:
#             instance = self._parse_instance(line)
#             self.model_container.add(instance)

#         self.latest_id = self.get_latest_id()

#     def init_model_container(self) -> ModelContainerBase:
#         """
#         Initializes the model container.
#         """
#         return self.model_container_class()

#     def get_sorted_model_fields(self) -> Dict[str, BaseEntityField]:
#         """
#         Returns the model fields sorted by their names.
#         """
#         return {field: self.model_fields_map[field] for field in sorted(self.model_fields_map.keys())}

#     def get_fields_indexes_map(self) -> Dict[str, int]:
#         """
#         Creates a mapping of field names to their indexes.
#         """
#         return {field: index for index, field in enumerate(self.model_fields_map.keys())}

#     def init_storage(self) -> None:
#         """
#         Initializes the storage by creating an empty file with headers.
#         """
#         super().init_storage()
#         with open(self.filepath, 'w', encoding=self.encoding) as f:
#             headers = self.text_sep.join(self.fields_idx_map.keys())
#             f.write(headers + '\n')

#     def delete_instance_by_id(self, instance_id: int) -> None:
#         """
#         Deletes an instance from the file by ID.
#         """
#         data = self._read_file()
#         updated_data = [
#             line for line in data if int(line.split(self.text_sep)[self.fields_idx_map['id']]) != instance_id
#         ]

#         with open(self.filepath, 'w', encoding=self.encoding) as f:
#             f.writelines(updated_data)

#     def _read_file(self) -> List[str]:
#         """
#         Reads all lines from the file.
#         """
#         return self._load_data()
