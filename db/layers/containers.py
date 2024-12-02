from typing import Union
from db.base import BaseEntity, BaseModelContainer
from src.utils.data_structures.binary_search_tree import AVLTree


class AVLTreeModelContainer(BaseModelContainer):

    def __init__(self, entity_class: BaseEntity):
        self.entity_class = entity_class
        self.key_getter = lambda x: x.id
        self.tree = AVLTree(key_getter=self.key_getter)

    def _get_key(self, instance) -> Union[int, str]:
        return self.key_getter(instance)

    def insert(self, value):
        self._ensure_instance(value)
        self.tree.insert(value)

    def _ensure_instance(self, value):
        if not isinstance(value, self.entity_class):
            raise ValueError(f"Value must be instance of {self.entity_class.__name__}")

    def _call_action(self, action, value):
        if isinstance(value, int):
            return action(value)
        if isinstance(value, self.entity_class):
            return action(self._get_key(value))
        self._ensure_instance(value)

    def search(self, value):
        return self._call_action(self.tree.search, value)

    def delete(self, value):
        return self._call_action(self.tree.delete, value)

    def __str__(self):
        return str(self.tree)
