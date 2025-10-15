import os

from typing import Any

class KimaiRequestHeaders:
  user_token: str
  user_password: str
  cookies: str

  def __init__(self):
    KIMAI_USER = os.getenv("KIMAI_USER")
    KIMAI_TOKEN = os.getenv("KIMAI_TOKEN")

    if(not(KIMAI_USER and KIMAI_TOKEN)):
      raise Exception("Cannot instantiate headers without crucial data")

    self.user_token = KIMAI_USER
    self.user_password = KIMAI_TOKEN

  def as_headers(self) -> Any:
    return {
      'accept': 'application/json',
      'Content-Type': 'application/json',
      'X-AUTH-USER': self.user_token,
      'X-AUTH-TOKEN': self.user_password
    }

