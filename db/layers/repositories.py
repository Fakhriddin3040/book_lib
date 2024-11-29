from typing import Any, Callable, Union
from src.utils.data_structures.binary_search_tree import AVLTree, Node


class ModelContainerBase:
    def insert(self, instance):
        raise NotImplemented("Method insert not implemented maaan. Implement it!")

    def search(self, instance):
        raise NotImplemented("Method search not implemented maaan. Implement it!")

    def delete(self, instance):
        raise NotImplemented("Method delete not implemented maaan. Implement it!")

    def __str__(self):
        """
        Optional method for string representation of container
        """
        return "Whatassssup! I'm a container! Huhuhu! Enough info for you! o_o Ahahaha!"


class AVLTreeModelContainer(ModelContainerBase):
    def __init__(self, lookup: str = None):
        lookup = lookup or "id"
        self.key_getter = lambda x: getattr(x, lookup)
        self.tree = AVLTree(
            key_getter=self.key_getter
        )

    def _get_key(self, instance) -> Union[int, str]:
        return self.key_getter(instance)

    def insert(self, value):
        self.tree.insert(value)

    def search(self, instance):
        return self.tree.search(self.get_key(instance))

    def delete(self, instance):
        self.tree.delete(self.get_key(instance))

    def __str__(self):
        return str(self.tree)
