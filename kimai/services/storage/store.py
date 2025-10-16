import json

import os
from sys import argv

from abc import ABC, abstractmethod
from typing import Any, Literal, Mapping, Sequence, TypeAlias

Store_Type: TypeAlias = Literal["disk", "s3"]

class I_Storage(ABC):
  @abstractmethod
  def write(self, path: str, content: Sequence[str] | str):
    pass

  @abstractmethod
  def reads(self, path: str) -> str:
    """
    Reads all content of file as a single string stream.
    """
    pass

  @abstractmethod
  def read(self, path: str) -> Sequence[str]:
    """
    Reads all content of a file and returns a Sequence represeting one line per
    element.
    """
    pass

# class S3Storage(I_Storage):
#   s3_client = boto3.client("s3")
#   s3_bucket: str
#
#   def __init__(self, bucket: str):
#     self.s3_bucket = bucket
#     print("Using S3 Storage")
#
#   def write(self, path: str, content: Sequence[str] | str):
#     print(f'Saving "{"".join(content)}" in "{path}"')
#     return
#
#   def reads(self, path: str) -> str:
#     print(f'Reading content in "{path}"')
#     return ""
#
#   def read(self, path: str) -> Sequence[str]:
#     print(f'Reading content in "{path}"')
#     return []

class DiskStorage(I_Storage):
  root_path: str = "."

  def __init__(self, root_path: str = "."):
    self.root_path = root_path + ("/" if not root_path.endswith("/") else "")

    if(not os.path.exists(self.root_path)):
      print(f'[DISK-STORAGE]: This path does not exist. Creating path')
      os.makedirs(self.root_path)

    print(f'Using Disk Storage. Saving fles in path "{self.root_path}"')

  def write(self, path: str, content: Sequence[str] | str):
    if(not isinstance(content, str) and isinstance(content, Sequence)): content = "\n".join(content)

    full_path = self.root_path + path
    split_path = full_path.split("/")
    filepath = "/".join(split_path[:-1])

    if(not os.path.exists(filepath)): os.makedirs(filepath)

    with open(full_path, "w") as out_file:
      out_file.write(content)

    return

  def read(self, path: str) -> Sequence[str]:
    path = self.root_path + path
    data = []

    with open(path, "r") as input:
      data = [row for row in input]

    return data

  def reads(self, path: str) -> str:
    return "\n".join(self.read(path)).strip()

class StorageService:
  store_env: Store_Type
  store: I_Storage

  def __init__(self, store_env: Store_Type):
    self.store_env = store_env

  @abstractmethod
  def create_storage(self) -> I_Storage:
    pass

  def write(self, path: str, content: Sequence[str] | str):
    self.store.write(path, content)

    return

  def reads(self, path: str) -> str:
    return self.store.reads(path)

  def read(self, path: str) -> Sequence[str]:
    return self.store.read(path)

  def read_json(self, path: str) -> Mapping[str, Any]:
    content = self.reads(path)
    data: Mapping[str, Any] = json.loads(content)

    return data

# class S3StorageService(StorageService):
#   s3_bucket: str
# 
#   def __init__(self, bucket: str):
#     self.s3_bucket = bucket
#     self.store = self.create_storage()
# 
#   def create_storage(self) -> I_Storage:
#     return S3Storage(self.s3_bucket)

class DiskStorageService(StorageService):
  root_path: str = "."

  def __init__(self, root_path: str = "."):
    super()
    self.root_path = root_path
    self.store = self.create_storage()

  def create_storage(self) -> I_Storage:
    return DiskStorage(self.root_path)

if(__name__ == "__main__"):
  argc, args = len(argv), argv

  store_type = args[1]
  store: StorageService

  match(store_type):
    case 'disk':
      store = DiskStorageService("data/in/json/")

    case _:
      raise ValueError("Unexistant storage type")

