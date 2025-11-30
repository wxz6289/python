from typing import Any, Optional, Union, NamedTuple

def double(x: Any) -> Any:
    return x * 2

print(double(2))

# def double2(x: object) -> object:
#     return x * 2

# print(double2(3))

def show_count(count: int, singular: str, plural: Optional[str] = None) -> str:
  return f"{count} {singular}"


def parse_token(token: str) -> Union[str, float]:
  try:
    return float(token)
  except ValueError:
    return token

from geolib import geohash as gh # type: ignore

PRECISION = 9

def geohash(lat_lon: tuple[float, float]) -> str:
  return gh.encode(*lat_lon, PRECISION)

class Coordinate(NamedTuple):
  lat: float
  lon: float

def geohash2(lat_lon: Coordinate) -> str:
  return gh.encode(*lat_lon, PRECISION)


from collections.abc import Sequence

def columnize(sequence: Sequence[str], num_columns: int = 0) -> list[tuple[str, ...]]:
  if num_columns == 0:
    num_columns = round(len(sequence)*0.5)
  num_rows, reminder = divmod(len(sequence), num_columns)
  num_rows += bool(reminder)
  return [tuple(sequence[i::num_rows]) for i in range(num_rows)]

animals = 'drake fawn heron ibex koala lynx tahr xerus yak zapus'.split()
table = columnize(animals)
for row in table:
  print(f'{word:10}' for word in row)


