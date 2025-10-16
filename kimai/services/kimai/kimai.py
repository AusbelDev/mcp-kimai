import requests
import os

from typing import Any, List, Optional

from kimai.models.activity import KimaiActivity, KimaiActivityEntity, KimaiActivityForm
from kimai.models.customer import KimaiCustomer
from kimai.models.misc import KimaiVersion
from kimai.models.project import KimaiProjectCollection
from kimai.models.request import IKimaiFetchActivitiesParams, KimaiRequestHeaders
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
    """
      Singleton class instance for only one service running.
    """
    if(cls.__instance): return cls.__instance

    cls.__instance = KimaiService()
    return cls.__instance

  def version(self) -> KimaiVersion:
    """
      Fetches current Kimai compilation version.

      @return
      KimaiVersion: Object representing the current version.
    """
    url = f'{self.__api_url}/version'

    response = requests.get(url, headers = self.__request_headers.as_headers())
    response.raise_for_status()

    data = response.json()

    return KimaiVersion(**data)

  def ping(self) -> str:
    """
      Checks Kimai's API status by returning a string when is up.

      @return
      str: String "pong"
    """
    url = f'{self.__api_url}/ping'

    response = requests.get(url, headers = self.__request_headers.as_headers())
    response.raise_for_status()

    data = response.json()

    return data.get('message')

  def get_activities(self, params: Optional[IKimaiFetchActivitiesParams] = None) -> List[KimaiActivity]:
    """
      List available activities for the user.

      @param
      params[Optional[IKimaiFetchActivitiesParams]]: A set of params for deepening
      the search. By default all params are disabled.

      @return
      List[KimaiActivity]: A list of activities.
    """
    url = f'{self.__api_url}/activities'

    response = requests.get(
      url,
      headers = self.__request_headers.as_headers(),
      params = params.model_dump(exclude_none = True) if params else None
    )
    response.raise_for_status()

    data = response.json()

    return [KimaiActivity(**activity) for activity in data]

  def get_activity(self, id: int) -> KimaiActivityEntity:
    """
      Fetches a specific activity whose id matches.

      @param
      id[int]: Specific activity id.

      @return
      KimaiActivityEntity: The found activity.
    """
    url = f'{self.__api_url}/activities/{id}'

    response = requests.get(url, headers = self.__request_headers.as_headers())
    response.raise_for_status()

    data = response.json()

    return KimaiActivityEntity(**data)

  # WARNING: Doesn't work, returns 403 (forbidden)
  def create_activity(self, activity: KimaiActivityForm) -> KimaiActivityEntity:
    """
      Creates the provided activity. Special privileges are needed for this
      action.

      @param
      activity[KimaiActivityForm]: The activity to be created.

      @return
      KimaiActivityEntity: The created activity.
    """
    url = f'{self.__api_url}/activities/'

    response = requests.post(
      url,
      headers = self.__request_headers.as_headers(),
      json = activity.model_dump(exclude_none = True)
    )
    response.raise_for_status()

    data = response.json()

    return KimaiActivityEntity(**data)

  # TODO: Use models for returning type
  # WARNING: Doesn't work, returns 403 (forbidden)
  def get_users(self) -> List[KimaiUser]:
    """
      Fetches available users in the system. Special privileges are needed for this
      action.

      @return
      List[KimaiUser]: The list of available users.
    """
    url = f'{self.__api_url}/users/'

    response = requests.get(url, headers = self.__request_headers.as_headers())
    response.raise_for_status()

    print(response.raise_for_status())

    return []

  def get_customers(self) -> List[KimaiCustomer]:
    """
      Fetches available customers in the system.

      @return
      List[KimaiCustomer]: The list of available customers.
    """
    url = f'{self.__api_url}/customers/'

    response = requests.get(
      url,
      headers = self.__request_headers.as_headers()
    )
    response.raise_for_status()

    data = response.json()

    return [KimaiCustomer(**customer) for customer in data]

  def get_tags(self) -> List[str]:
    """
      Fetches available tags in the system.

      @return
      List[str]: The list of available tags.
    """
    url = f'{self.__api_url}/tags/'

    response = requests.get(url, headers = self.__request_headers.as_headers())
    response.raise_for_status()

    response_data = response.json()
    return response_data

  def get_timesheets(self) -> List[KimaiTimesheetCollection]:
    """
      Fetches available timesheets for the current user.

      @return
      List[KimaiTimesheetCollection]: The list of available timesheets of the user.
    """
    url = f'{self.__api_url}/timesheets'

    response = requests.get(url, headers = self.__request_headers.as_headers())
    response.raise_for_status()

    response_data = response.json()

    return [KimaiTimesheetCollection(**timesheet) for timesheet in response_data]

  # WARNING: Doesn't work, returns 403 (forbidden)
  def get_timesheet(self, id: int) -> KimaiTimesheetEntity:
    """
      Fetches a timesheets for the current user.

      @return
      KimaiTimesheetEntity: The timesheet whose id matches.
    """
    url = f'{self.__api_url}/timesheets/{id}'

    response = requests.get(url, headers = self.__request_headers.as_headers())
    response.raise_for_status()

    response_data = response.json()

    return KimaiTimesheetEntity(**response_data)

  def get_recent_timesheets(self) -> List[KimaiTimesheetCollectionDetails]:
    """
      Fetches the user's recent timesheets.

      @return
      List[KimaiTimesheetCollectionDetails] = A list of the recent timesheets.
    """
    url = f'{self.__api_url}/timesheets/recent'

    response = requests.get(url, headers = self.__request_headers.as_headers())
    response.raise_for_status()

    response_data = response.json()

    return [KimaiTimesheetCollectionDetails(**timesheet) for timesheet in response_data]

  def get_active_timesheets(self) -> List[KimaiTimesheetCollectionDetails]:
    """
      Fetches the active timesheets.

      @return
      List[KimaiTimesheetCollectionDetails] = A list of the active timesheets.
    """
    url = f'{self.__api_url}/timesheets/active'

    response = requests.get(url, headers = self.__request_headers.as_headers())
    response.raise_for_status()

    response_data = response.json()

    return [KimaiTimesheetCollectionDetails(**timesheet) for timesheet in response_data]

  def get_projects(self) -> List[KimaiProjectCollection]:
    """
      Fetches the available projects.

      @return
      List[KimaiProjectCollection] = A list of the available projects.
    """
    url = f'{self.__api_url}/projects'

    response = requests.get(url, headers = self.__request_headers.as_headers())
    response.raise_for_status()

    response_data = response.json()

    return [KimaiProjectCollection(**project) for project in response_data]

  def create_timesheet(self, timesheet: KimaiTimesheet) -> KimaiTimesheetEntity:
    """
      Creates the provided timesheet in the system.

      @param
      timesheet[KimaiTimesheet]: The activity to be created.

      @return
      KimaiTimesheetEntity: The created timesheet.
    """
    url = f'{self.__api_url}/timesheets'

    response = requests.post(
      url,
      headers = self.__request_headers.as_headers(),
      json = timesheet.model_dump(exclude_none = True)
    )
    response.raise_for_status()

    response_data = response.json()

    return KimaiTimesheetEntity(**response_data)

  def update_timesheet(self, id: int, timesheet: KimaiTimesheet) -> KimaiTimesheetEntity:
    """
      Edits the specified timesheet that matches the id.

      @param
      timesheet[KimaiTimesheet]: The activity to be edited.

      @return
      KimaiTimesheetEntity: The created timesheet.
    """
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
    """
      Deletes the specified timesheet that matches the id.

      @param
      id[int]: The timesheet's id to be deleted.

      @return None
    """
    url = f'{self.__api_url}/timesheets/{id}'

    response = requests.delete(
      url,
      headers = self.__request_headers.as_headers()
    )

    response.raise_for_status()

    return None

