import os

from typing import Any

class KimaiRequestHeaders:
  user_token: str
  user_password: str

  def __init__(self):
    USER_USER = os.getenv("USER_USER")
    USER_TOKEN = os.getenv("USER_TOKEN")

    if(not(USER_USER and USER_TOKEN)):
      raise Exception("Cannot instantiate headers without crucial data")

    self.user_token = USER_USER
    self.user_password = USER_TOKEN

  def as_headers(self) -> Any:
    return {
      'X-AUTH-USER': self.user_token,
      'X-AUTH-USER': self.user_password
    }

