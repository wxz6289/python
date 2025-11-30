from collections.abc import Iterable
from typing import TypeVar, Protocol, Any

class SupportsLessThan:
  def __lt__(self, other: Any) -> bool:
    return self < other

LT = TypeVar('LT', bound=SupportsLessThan)

def top(series: Iterable[LT], length: int) -> list[LT]:
  ordered =  sorted(series, reverse=True)
  return ordered[:length]

result = top([4, 1, 5, 2, 6, 7, 3], 3)
print(result)


class Spam:
  def __init__(self, n):
    self.n = n

  def __lt__(self, other):
    return self.n < other.n

  def __repr__(self):
    return f'Spam({self.n})'

l = [Spam(n) for n in range(5, 0, -1)]
print(l)

print(sorted(l))
