from typing import Any, Callable, Union


class Node:
    def __init__(self, key, value) -> None:
        self.key = key
        self.value = value
        self.left = None
        self.right = None
        self.height = 1


class AVLTree:
    def __init__(
        self,
        key_getter: Callable[[Any], Union[int, str]] = lambda x: x
    ) -> None:
        self.root = None
        self.key_getter = key_getter

    def get_key(self, value: Any) -> Union[int, str]:
        try:
            return self.key_getter(value)
        except Exception as e:
            raise ValueError(f"Can't get key from value: {value}") from e

    def insert(self, value: Any) -> None:
        key = self.key_getter(value)
        self.root = self._insert(self.root, key, value)

    def delete(self, key: Union[str, int]) -> None:
        self.root = self._delete(self.root, key)

    def search(self, key: Union[int, str]) -> Union[None, Any]:
        return self._search(self.root, key)

    def _search(self, node: Node, key) -> Union[None, Any]:
        if not node:
            return None
        if key == node.key:
            return node.value
        if key < node.key:
            return self._search(node.left, key)
        return self._search(node.right, key)

    def _insert(self, node, key, value) -> Node:
        if not node:
            return Node(key, value)
        if key == node.key:
            node.value = value
        elif key < node.key:
            node.left = self._insert(node.left, key, value)
        else:
            node.right = self._insert(node.right, key, value)
        return self._balance(node)

    def _delete(self, node, key) -> Node:
        if not node:
            return None
        if key == node.key:
            if not node.left:
                return node.right
            if not node.right:
                return node.left
            min_node = self._find_min(node.right)
            node.key, node.value = min_node.key, min_node.value
            node.right = self._delete(node.right, min_node.key)
        elif key < node.key:
            node.left = self._delete(node.left, key)
        else:
            node.right = self._delete(node.right, key)
        return self._balance(node)

    def _find_min(self, node: Node) -> Node:
        while node.left:
            node = node.left
        return node

    def find_max(self, node: Node) -> Node:
        while node.right:
            node = node.right
        return node

    def _get_height(self, node: Node) -> int:
        return node.height if node else 0

    def _update_height(self, node: Node) -> None:
        node.height = 1 + max(self._get_height(node.left), self._get_height(node.right))

    def _balance(self, node: Node) -> Node:
        if not node:
            return None
        self._update_height(node)
        balance_factor = self._get_height(node.left) - self._get_height(node.right)
        if balance_factor > 1:
            if self._get_height(node.left.left) >= self._get_height(node.left.right):
                return self._rotate_right(node)
            else:
                return self._rotate_left_right(node)
        if balance_factor < -1:
            if self._get_height(node.right.right) >= self._get_height(node.right.left):
                return self._rotate_left(node)
            else:
                return self._rotate_right_left(node)
        return node

    def _rotate_right(self, node: Node) -> Node:
        new_root = node.left
        node.left = new_root.right
        new_root.right = node
        self._update_height(node)
        self._update_height(new_root)
        return new_root

    def _rotate_left(self, node: Node) -> Node:
        new_root = node.right
        node.right = new_root.left
        new_root.left = node
        self._update_height(node)
        self._update_height(new_root)
        return new_root

    def _rotate_left_right(self, node: Node) -> Node:
        node.left = self._rotate_left(node.left)
        return self._rotate_right(node)

    def _rotate_right_left(self, node: Node) -> Node:
        node.right = self._rotate_right(node.right)
        return self._rotate_left(node)

    def in_order(self):
        yield from self._in_order(self.root)

    def _in_order(self, node: Node):
        if node:
            yield from self._in_order(node.left)
            yield node.key, node.value
            yield from self._in_order(node.right)

    def __str__(self) -> str:
        lines = []
        self._print(self.root, lines, 0)
        return "\n".join(lines)

    def _print(self, node: Node, lines: list, level: int) -> None:
        if node:
            self._print(node.right, lines, level + 1)
            lines.append("    " * level + f"({node.key}: {node.value})")
            self._print(node.left, lines, level + 1)