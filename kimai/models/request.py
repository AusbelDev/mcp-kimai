import os

from typing import Any

class KimaiRequestHeaders:
  user_token: str
  user_password: str

  def __init__(self):
    USER_TOKEN = os.getenv("USER_TOKEN")
    USER_PASSWORD = os.getenv("USER_PASSWORD")

    if(not(USER_TOKEN and USER_PASSWORD)):
      raise Exception("Cannot instantiate headers without crucial data")

    self.user_token = USER_TOKEN
    self.user_password = USER_PASSWORD

  def as_headers(self) -> Any:
    return {
      'X-AUTH-USER': self.user_token,
      'X-AUTH-TOKEN': self.user_password
    }

