from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, replace
from typing import Optional, Self

@dataclass(frozen=True)
class UserId:
  id: int

  def __post_init__(self):
    if self.id <= 0:
      raise ValueError("User ID must be greater than 0")


@dataclass(frozen=True)
class User:
  id: Optional[UserId]
  name: str
  email: Optional[str]
  password: str

  def __post_init__(self):
    if self.name is None or self.name == "":
      raise ValueError("User name is required")
    if self.password is None or self.password == "":
      raise ValueError("User password is required")

  def __str__(self):
    return f"User(id={self.id}, name={self.name}, email={self.email})"

  def __repr__(self):
    return f"User(id={self.id}, name={self.name}, email={self.email})"

  def verify_password(self, password: str) -> bool:
    return self.password == password

  def change_password(self, new_password: str) -> Self:
    return replace(self, password=new_password)

class Repository(ABC):
  @abstractmethod
  def save(self, user: User) -> None:
    pass

  @abstractmethod
  def find_by_id(self, id: UserId) -> Optional[User]:
    pass

  @abstractmethod
  def find_all(self) -> list[User]:
    pass

if __name__ == "__main__":
  user = User(id=UserId(id=1), name="John Doe", email="john.doe@example.com", password="password")
  print(user)
  print(user.verify_password("password"))
  print(user.change_password("new_password").password)
  print(user)
