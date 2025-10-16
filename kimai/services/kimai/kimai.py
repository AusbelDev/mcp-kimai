import requests
import os

from typing import Any, List, Optional

from kimai.models.activity import KimaiActivity, KimaiActivityEntity, KimaiActivityForm
from kimai.models.customer import KimaiCustomer
from kimai.models.misc import KimaiVersion
from kimai.models.project import KimaiProjectCollection
from kimai.models.request import KimaiRequestHeaders
from kimai.models.timesheet import KimaiTimesheet, KimaiTimesheetCollection, KimaiTimesheetCollectionDetails, KimaiTimesheetEntity
from kimai.models.user import KimaiUser

class KimaiService:
  __api_url: str
  __request_headers: KimaiRequestHeaders

  __instance: Optional[Any] = None

  def __init__(self):
    KIMAI_BASE_URL = os.getenv("KIMAI_BASE_URL")

    if(not KIMAI_BASE_URL):
      raise Exception("Cannot instantiate service without crucial data")

    self.__api_url = KIMAI_BASE_URL
    self.__request_headers = KimaiRequestHeaders()

  @classmethod
  def get_instance(cls):
    if(cls.__instance): return cls.__instance

    cls.__instance = KimaiService()
    return cls.__instance

  def version(self) -> KimaiVersion:
    url = f'{self.__api_url}/version'

    response = requests.get(url, headers = self.__request_headers.as_headers())
    response.raise_for_status()

    data = response.json()

    return KimaiVersion(**data)

  def ping(self) -> str:
    url = f'{self.__api_url}/ping'

    response = requests.get(url, headers = self.__request_headers.as_headers())
    response.raise_for_status()

    data = response.json()

    return data.get('message')

  def get_activities(self) -> List[KimaiActivity]:
    url = f'{self.__api_url}/activities'

    response = requests.get(url, headers = self.__request_headers.as_headers())
    data = response.json()

    return [KimaiActivity(**activity) for activity in data]

  def get_activity(self, id: int) -> KimaiActivityEntity:
    url = f'{self.__api_url}/activities/{id}'

    response = requests.get(url, headers = self.__request_headers.as_headers())
    data = response.json()

    return KimaiActivityEntity(**data)

  # WARNING: Doesn't work, returns 403 (forbidden)
  def create_activity(self, activity: KimaiActivityForm) -> KimaiActivityEntity:
    url = f'{self.__api_url}/activities/'

    response = requests.post(
      url,
      headers = self.__request_headers.as_headers(),
      json = activity.model_dump(exclude_none = True)
    )
    data = response.json()

    return KimaiActivityEntity(**data)

  # TODO: Use models for returning type
  # WARNING: Doesn't work, returns 403 (forbidden)
  def get_users(self) -> List[KimaiUser]:
    url = f'{self.__api_url}/users/'
    response = requests.get(url, headers = self.__request_headers.as_headers())

    print(response.raise_for_status())

    return []

  def get_customers(self) -> List[KimaiCustomer]:
    url = f'{self.__api_url}/customers/'

    response = requests.get(
      url,
      headers = self.__request_headers.as_headers()
    )
    data = response.json()

    return [KimaiCustomer(**customer) for customer in data]

  def get_tags(self) -> List[str]:
    url = f'{self.__api_url}/tags/'

    response = requests.get(url, headers = self.__request_headers.as_headers())
    response.raise_for_status()

    response_data = response.json()
    return response_data

  def get_timesheets(self) -> List[KimaiTimesheetCollection]:
    url = f'{self.__api_url}/timesheets'

    response = requests.get(url, headers = self.__request_headers.as_headers())
    response.raise_for_status()

    response_data = response.json()

    return [KimaiTimesheetCollection(**timesheet) for timesheet in response_data]

  # WARNING: Doesn't work, returns 403 (forbidden)
  def get_timesheet(self, id: int) -> KimaiTimesheetEntity:
    url = f'{self.__api_url}/timesheets/{id}'

    response = requests.get(url, headers = self.__request_headers.as_headers())
    response.raise_for_status()

    response_data = response.json()

    return KimaiTimesheetEntity(**response_data)

  def get_recent_timesheets(self) -> List[KimaiTimesheetCollectionDetails]:
    url = f'{self.__api_url}/timesheets/recent'

    response = requests.get(url, headers = self.__request_headers.as_headers())
    response.raise_for_status()

    response_data = response.json()

    return [KimaiTimesheetCollectionDetails(**timesheet) for timesheet in response_data]

  def get_active_timesheets(self) -> List[KimaiTimesheetCollectionDetails]:
    url = f'{self.__api_url}/timesheets/active'

    response = requests.get(url, headers = self.__request_headers.as_headers())
    response.raise_for_status()

    response_data = response.json()

    return [KimaiTimesheetCollectionDetails(**timesheet) for timesheet in response_data]

  def get_projects(self) -> List[KimaiProjectCollection]:
    url = f'{self.__api_url}/projects'

    response = requests.get(url, headers = self.__request_headers.as_headers())
    response.raise_for_status()

    response_data = response.json()

    return [KimaiProjectCollection(**project) for project in response_data]

  def create_timesheet(self, timesheet: KimaiTimesheet) -> KimaiTimesheetEntity:
    url = f'{self.__api_url}/timesheets'

    response = requests.post(
      url,
      headers = self.__request_headers.as_headers(),
      json = timesheet.model_dump(exclude_none = True)
    )
    # print(timesheet.model_dump(exclude_none = True))
    # print(response.request.headers)
    # print(response.request.body)

    response.raise_for_status()
    response_data = response.json()

    return KimaiTimesheetEntity(**response_data)

  def update_timesheet(self, id: int, timesheet: KimaiTimesheet) -> KimaiTimesheetEntity:
    url = f'{self.__api_url}/timesheets/{id}'

    response = requests.patch(
      url,
      headers = self.__request_headers.as_headers(),
      json = timesheet.model_dump(exclude_none = True)
    )

    response.raise_for_status()
    response_data = response.json()

    return KimaiTimesheetEntity(**response_data)

  def delete_timesheet(self, id: int) -> None:
    url = f'{self.__api_url}/timesheets/{id}'

    response = requests.delete(
      url,
      headers = self.__request_headers.as_headers()
    )

    response.raise_for_status()

    return None

