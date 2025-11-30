from collections.abc import Iterable
from typing import TypeAlias

FromTo: TypeAlias = tuple[str, str]

def zip_replace(text: str, changes: Iterable[FromTo]) -> str:
  for from_, to in changes:
    text = text.replace(from_, to)
  return text


l33t = [('a', '4'), ('e', '3'), ('i', '1'), ('o', '0')]
text = 'mad skilled noob powned leet'

result =  zip_replace(text, l33t)
print(result)
