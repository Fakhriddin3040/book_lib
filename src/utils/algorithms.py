from typing import Any, Callable, Dict, List


def bin_search(arr: List[int], target: int) -> int:
    left = 0
    right = len(arr) - 1
    while (left <= right):
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        if arr[mid] > target:
            right = mid - 1
        else:
            left = mid + 1


def qsort(arr: List[Any], key: Callable[[Any], Any] = lambda x: x) -> List[Any]:
    if len(arr) <= 1:
        return arr

    pivot = key(arr[len(arr) // 2])
    left = [item for item in arr if key(item) < pivot]
    middle = [item for item in arr if key(item) == pivot]
    right = [item for item in arr if key(item) > pivot]

    return qsort(left, key) + middle + qsort(right, key)