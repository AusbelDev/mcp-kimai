import json
import logging
import os
from typing import Any, Dict, List, Optional

import dotenv
import requests
from models.activity import KimaiActivity, KimaiActivityEntity, KimaiActivityForm
from models.customer import KimaiCustomer
from models.misc import KimaiVersion
from models.project import KimaiProjectCollection
from models.request import (
    IKimaiFetchActivitiesParams,
    IKimaiFetchRecentTimesheetsParams,
    IKimaiFetchTimesheetsParams,
    KimaiRequestHeaders,
)
from models.timesheet import (
    KimaiTimesheet,
    KimaiTimesheetCollection,
    KimaiTimesheetCollectionDetails,
    KimaiTimesheetEntity,
    KimaiTimesheetNonUTC,
)
from models.user import KimaiUser

logger = logging.getLogger(__name__)

CONTEXT_PATH = "./mcp_context/"
dotenv.load_dotenv()


class KimaiService:
    __api_url: str
    __request_headers: KimaiRequestHeaders

    __instance: Optional[Any] = None

    def __init__(self):
        KIMAI_BASE_URL = os.getenv("KIMAI_BASE_URL")

        if not KIMAI_BASE_URL:
            raise Exception("Cannot instantiate service without crucial data")

        self.__api_url = KIMAI_BASE_URL
        self.__request_headers = KimaiRequestHeaders()

    @classmethod
    def get_instance(cls):
        """
        Singleton class instance for only one service running.
        """
        if cls.__instance:
            return cls.__instance

        cls.__instance = KimaiService()
        return cls.__instance

    def version(self) -> KimaiVersion:
        """
        Fetches current Kimai compilation version.

        @return
        KimaiVersion: Object representing the current version.
        """
        url = f"{self.__api_url}/version"

        response = requests.get(url, headers=self.__request_headers.as_headers())
        response.raise_for_status()

        data = response.json()

        return KimaiVersion(**data)

    def ping(self) -> str:
        """
        Checks Kimai's API status by returning a string when is up.

        @return
        str: String "pong"
        """
        url = f"{self.__api_url}/ping"

        response = requests.get(url, headers=self.__request_headers.as_headers())
        response.raise_for_status()

        data = response.json()

        return data.get("message")

    def user_server_config(self) -> Dict[str, Any]:
        """
        Fetches current Kimai user server configuration.

        @return
        Dict[str, Any]: Object representing the current user server config.
        """
        url = f"{self.__api_url}/config/i18n"

        response = requests.get(url, headers=self.__request_headers.as_headers())
        response.raise_for_status()

        data = response.json()

        return data

    def get_activities(
        self, params: Optional[Dict[str, Any]] = None
    ) -> List[KimaiActivity]:
        """
        List available activities for the user.

        @param
        params[Optional[IKimaiFetchActivitiesParams]]: A set of params for deepening
        the search. By default all params are disabled.

        @return
        List[KimaiActivity]: A list of activities.
        """
        url = f"{self.__api_url}/activities"
        valid_params = None

        if os.path.exists(f"{CONTEXT_PATH}/kimai_activities.json") and not params:
            try:
                with open(
                    f"{CONTEXT_PATH}/kimai_activities.json", "r", encoding="utf-8"
                ) as f:
                    data = json.load(f)
                logger.info("Loaded activities from local context file.")
                return [KimaiActivity(**activity) for activity in data]
            except Exception as e:
                logger.error(
                    f"Failed to load activities from local context file. Error: {e}"
                )
        else:
            try:
                if params:
                    valid_params = IKimaiFetchActivitiesParams(**params)
                response = requests.get(
                    url,
                    headers=self.__request_headers.as_headers(),
                    params=valid_params.model_dump(exclude_none=True)
                    if valid_params
                    else None,
                )
                response.raise_for_status()

                data = response.json()

                return [KimaiActivity(**activity) for activity in data]
            except Exception as e:
                logger.error(f"Failed to fetch activities from Kimai API. Error: {e}")
        return []

    def get_activity(self, id: int) -> KimaiActivityEntity:
        """
        Fetches a specific activity whose id matches.

        @param
        id[int]: Specific activity id.

        @return
        KimaiActivityEntity: The found activity.
        """
        url = f"{self.__api_url}/activities/{id}"

        response = requests.get(url, headers=self.__request_headers.as_headers())
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
        url = f"{self.__api_url}/activities/"

        response = requests.post(
            url,
            headers=self.__request_headers.as_headers(),
            json=activity.model_dump(exclude_none=True),
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
        url = f"{self.__api_url}/users/"

        response = requests.get(url, headers=self.__request_headers.as_headers())
        response.raise_for_status()

        return []

    def get_customers(self) -> List[KimaiCustomer]:
        """
        Fetches available customers in the system.

        @return
        List[KimaiCustomer]: The list of available customers.
        """
        url = f"{self.__api_url}/customers/"

        response = requests.get(url, headers=self.__request_headers.as_headers())
        response.raise_for_status()

        data = response.json()

        return [KimaiCustomer(**customer) for customer in data]

    def get_tags(self) -> List[str]:
        """
        Fetches available tags in the system.

        @return
        List[str]: The list of available tags.
        """
        url = f"{self.__api_url}/tags/"

        response = requests.get(url, headers=self.__request_headers.as_headers())
        response.raise_for_status()

        response_data = response.json()
        return response_data

    def get_timesheets(
        self, params: Optional[Dict[str, Any]] = None
    ) -> List[KimaiTimesheetCollection]:
        """
        Fetches available timesheets for the current user.

        @return
        List[KimaiTimesheetCollection]: The list of available timesheets of the user.
        """
        url = f"{self.__api_url}/timesheets"
        valid_params = None

        local_context_file = f"{CONTEXT_PATH}/kimai_timesheets.json"
        if os.path.exists(local_context_file) and not params:
            logger.info("Attempting to load timesheets from local context file.")
            try:
                if os.path.exists(local_context_file):
                    with open(local_context_file, "r", encoding="utf-8") as f:
                        response_data = json.load(f)
                    logger.info("Loaded timesheets from local context file.")
            except Exception as e:
                logger.error(
                    f"Failed to load timesheets from local context file. Error: {e}"
                )
        else:
            logger.info("Fetching timesheets from Kimai API.")
            try:
                if params:
                    valid_params = IKimaiFetchTimesheetsParams(**params)
                response = requests.get(
                    url,
                    headers=self.__request_headers.as_headers(),
                    params=valid_params.model_dump(exclude_none=True)
                    if valid_params
                    else None,
                )
                response.raise_for_status()
                response_data = response.json()
            except Exception as e:
                logger.error(f"Failed to fetch timesheets from Kimai API. Error: {e}")

        return [KimaiTimesheetCollection(**timesheet) for timesheet in response_data]

    def get_timesheet(self, id: int) -> KimaiTimesheetEntity:
        """
        Fetches a timesheets for the current user.

        @return
        KimaiTimesheetEntity: The timesheet whose id matches.
        """
        url = f"{self.__api_url}/timesheets/{id}"

        local_context_file = f"{CONTEXT_PATH}/kimai_timesheets.json"
        logger.info("Attempting to load timesheet from local context file.")
        if os.path.exists(local_context_file):
            try:
                if os.path.exists(local_context_file):
                    with open(local_context_file, "r", encoding="utf-8") as f:
                        response_data = json.load(f)
                    for timesheet in response_data:
                        if timesheet.get("id") == id:
                            logger.info("Loaded timesheet from local context file.")
                            return KimaiTimesheetEntity(**timesheet)
            except Exception as e:
                logger.error(
                    f"Failed to load timesheet from local context file. Error: {e}"
                )
        else:
            try:
                url = f"{self.__api_url}/timesheets/{id}"

                response = requests.get(
                    url, headers=self.__request_headers.as_headers()
                )
                response.raise_for_status()
                response_data = response.json()
            except Exception as e:
                logger.error(f"Failed to fetch timesheet from Kimai API. Error: {e}")

        return KimaiTimesheetEntity(**response_data)

    def get_recent_timesheets(
        self, params: Optional[Dict[str, Any]]
    ) -> List[KimaiTimesheetCollectionDetails]:
        """
        Fetches the user's recent timesheets.

        @return
        List[KimaiTimesheetCollectionDetails] = A list of the recent timesheets.
        """
        url = f"{self.__api_url}/timesheets/recent"
        valid_params = None
        if params:
            valid_params = IKimaiFetchRecentTimesheetsParams(**params)

        response = requests.get(
            url,
            headers=self.__request_headers.as_headers(),
            params=valid_params.model_dump(exclude_none=True) if valid_params else None,
        )
        response.raise_for_status()

        response_data = response.json()

        return [
            KimaiTimesheetCollectionDetails(**timesheet) for timesheet in response_data
        ]

    def get_active_timesheets(self) -> List[KimaiTimesheetCollectionDetails]:
        """
        Fetches the active timesheets.

        @return
        List[KimaiTimesheetCollectionDetails] = A list of the active timesheets.
        """
        url = f"{self.__api_url}/timesheets/active"

        response = requests.get(url, headers=self.__request_headers.as_headers())
        response.raise_for_status()

        response_data = response.json()

        return [
            KimaiTimesheetCollectionDetails(**timesheet) for timesheet in response_data
        ]

    def get_projects(self) -> List[KimaiProjectCollection]:
        """
        Fetches the available projects.

        @return
        List[KimaiProjectCollection] = A list of the available projects.
        """
        url = f"{self.__api_url}/projects"

        response = requests.get(url, headers=self.__request_headers.as_headers())
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
        if isinstance(timesheet.project, str):
            timesheet.project = int(
                self.get_ids({"project": timesheet.project})["project"]
            )
        if isinstance(timesheet.activity, str):
            timesheet.activity = int(
                self.get_ids({"activity": timesheet.activity})["activity"]
            )

        url = f"{self.__api_url}/timesheets"

        try:
            response = requests.post(
                url,
                headers=self.__request_headers.as_headers(),
                json=timesheet.model_dump(exclude_none=True),
            )
            response.raise_for_status()

            response_data = response.json()

        except Exception as e:
            logger.error(f"Failed to create timesheet in Kimai API. Error: {e}")
            logger.error(f"{response.text}")
            raise e

        return KimaiTimesheetEntity(**response_data)

    def create_outlook_timesheet(
        self, timesheet: KimaiTimesheetNonUTC
    ) -> KimaiTimesheetEntity:
        """
        Creates the provided timesheet in the system. This is specifically for Outlook events.

        @param
        timesheet[KimaiTimesheet]: The activity to be created.

        @return
        KimaiTimesheetEntity: The created timesheet.
        """
        if isinstance(timesheet.project, str):
            timesheet.project = int(
                self.get_ids({"project": timesheet.project})["project"]
            )
        if isinstance(timesheet.activity, str):
            timesheet.activity = int(
                self.get_ids({"activity": timesheet.activity})["activity"]
            )

        url = f"{self.__api_url}/timesheets"

        try:
            response = requests.post(
                url,
                headers=self.__request_headers.as_headers(),
                json=timesheet.model_dump(exclude_none=True),
            )
            response.raise_for_status()

            response_data = response.json()

        except Exception as e:
            logger.error(f"Failed to create timesheet in Kimai API. Error: {e}")
            logger.error(f"{response.text}")
            raise e

        return KimaiTimesheetEntity(**response_data)

    def update_timesheet(
        self, id: int, timesheet: KimaiTimesheet
    ) -> KimaiTimesheetEntity:
        """
        Edits the specified timesheet that matches the id.

        @param
        timesheet[KimaiTimesheet]: The activity to be edited.

        @return
        KimaiTimesheetEntity: The created timesheet.
        """
        url = f"{self.__api_url}/timesheets/{id}"

        response = requests.patch(
            url,
            headers=self.__request_headers.as_headers(),
            json=timesheet.model_dump(exclude_none=True),
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
        url = f"{self.__api_url}/timesheets/{id}"

        response = requests.delete(url, headers=self.__request_headers.as_headers())
        response.raise_for_status()

        return None

    def get_ids(self, fetch: Dict[str, str]) -> Dict[str, str]:
        """
        Fetches IDs for various entities based on provided names.

        @param
        fetch[Dict[str, str]]: A dictionary with entity types as keys and names as values.

        @return
        Dict[str, int]: A dictionary with entity types as keys and their corresponding IDs as values.
        """

        for entity_type, name in fetch.items():
            if entity_type == "":
                del fetch[entity_type]
                continue
            if entity_type == "project":
                if os.path.exists(f"{CONTEXT_PATH}/kimai_projects.json"):
                    with open(
                        f"{CONTEXT_PATH}/kimai_projects.json", "r", encoding="utf-8"
                    ) as f:
                        projects_data = json.load(f)
                    for project in projects_data:
                        if project.get("name").lower() == name.lower():
                            fetch["project"] = project.get("id")
                            break
            if entity_type == "activity":
                if os.path.exists(f"{CONTEXT_PATH}/kimai_activities.json"):
                    with open(
                        f"{CONTEXT_PATH}/kimai_activities.json", "r", encoding="utf-8"
                    ) as f:
                        activities_data = json.load(f)
                    for activity in activities_data:
                        if activity.get("name").lower() == name.lower() and fetch.get(
                            "project"
                        ) == activity.get("project"):
                            fetch["activity"] = activity.get("id")
                            break
            if entity_type == "customer":
                if os.path.exists(f"{CONTEXT_PATH}/kimai_customers.json"):
                    with open(
                        f"{CONTEXT_PATH}/kimai_customers.json", "r", encoding="utf-8"
                    ) as f:
                        customers_data = json.load(f)
                    for customer in customers_data:
                        if customer.get("name").lower() == name.lower():
                            fetch["customer"] = customer.get("id")
                            break

        return fetch
