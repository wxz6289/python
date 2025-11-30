from collections.abc import Iterable
from typing import TYPE_CHECKING
import pytest

from mypy_04 import top

def test_top_tuple() -> None:
  fruit = 'mango pear apple kiwi banana'.split()
  series: Iterable[tuple[int, str]] = ((len(s),s) for s in fruit)
  length = 3
  expected = [(6, 'banana'), (5, 'mango'), (5, 'apple')]
  result = top(series, length)
  if TYPE_CHECKING:
    reveal_type(series)
    reveal_type(expected)
    reveal_type(result)
  assert result == expected

def test_object_error() -> None:
  series = [object() for _ in range(4)]
  if TYPE_CHECKING:
    reveal_type(series)
  with pytest.raises(TypeError) as excinfo:
    top(series, 3)
  assert "'<' not supported" in str(excinfo.value)
