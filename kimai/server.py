from datetime import datetime
import logging

import dotenv
import sys
import os

from typing import Any, Dict, List, cast
from fastmcp import FastMCP
from requests.models import HTTPError

from starlette.responses import PlainTextResponse
from starlette.requests import Request
from models.activity import KimaiActivity, KimaiActivityEntity
from models.customer import KimaiCustomer
from models.misc import KimaiVersion, MCPContextMeta
from models.project import KimaiProject
from models.timesheet import (
    KimaiTimesheet,
    KimaiTimesheetCollection,
    KimaiTimesheetCollectionDetails,
    KimaiTimesheetEntity,
)
from services.kimai.kimai import KimaiService
from services.storage.store import DiskStorageService

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger("kimai-server")
dotenv.load_dotenv()

mcp = FastMCP(os.getenv("MCP_SERVER_NAME", "Kimai-MCP"))
kimai_service = KimaiService.get_instance()
storage_service = DiskStorageService("./mcp_context/")


def get_meta() -> Any:
    meta = None
    difference = 0

    try:
        meta = MCPContextMeta(**storage_service.read_json("mcp_context_meta.json"))
        difference = (datetime.now() - meta.last_update).days

        logger.error(
            f"MCP context already existing. It's been {difference} day{'s' if difference != 1 else ''} since last download"
        )

    except Exception as err:
        logger.error(f"{err}")

    if meta and difference <= 7:
        # Return a json if the meta exists and is less than a week old
        return {"meta": meta}
    logger.error("Automatically downloading most recent context.")

    activities = kimai_service.get_activities()
    customers = kimai_service.get_customers()
    tags = kimai_service.get_tags()
    timesheets = kimai_service.get_timesheets()
    projects = kimai_service.get_projects()

    timesheet_descs = [
        timesheet.description for timesheet in timesheets if timesheet.description
    ]

    activities_joined = ",\n".join(
        [activity.model_dump_json() for activity in activities]
    )
    customers_joined = ",\n".join(
        [customer.model_dump_json() for customer in customers]
    )
    tags_joined = ",\n".join(tags)
    timesheets_joined = ",\n".join(
        [timesheet.model_dump_json() for timesheet in timesheets]
    )
    projects_joined = ",\n".join([project.model_dump_json() for project in projects])

    storage_service.write("kimai_activities.json", f"[\n{activities_joined}\n]")
    storage_service.write("kimai_customers.json", f"[\n{customers_joined}\n]")
    storage_service.write("kimai_timesheets.json", f"[\n{timesheets_joined}\n]")
    storage_service.write("kimai_projects.json", f"[\n{projects_joined}\n]")
    storage_service.write("kimai_tags.txt", tags_joined)
    storage_service.write(
        "kimai_timesheet_descriptions.txt", ",\n".join(timesheet_descs)
    )

    storage_service.write(
        "mcp_context_meta.json", MCPContextMeta().model_dump_json(indent=2)
    )

    return meta


@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request) -> PlainTextResponse:
    return PlainTextResponse("MCP Server is up and running")


@mcp.tool()
async def kimai_ping() -> str:
    """
    Checks Kimai's API status by returning a string when is up.

    @return
    str: String "pong"
    """
    try:
        response = kimai_service.ping()

        return response
    except HTTPError as err:
        logger.error(err)
        return err.response.json()


@mcp.tool()
async def kimai_version() -> KimaiVersion:
    """
    Fetches current Kimai compilation version.

    @return
    KimaiVersion: Object representing the current version.
    """
    try:
        response = kimai_service.version()

        return response
    except HTTPError as err:
        logger.error(err)
        return err.response.json()


@mcp.tool()
async def kimai_list_activities() -> List[KimaiActivity]:
    """
    List available activities for the user.

    @param
    params[Optional[IKimaiFetchActivitiesParams]]: A set of params for deepening
    the search. By default all params are disabled.

    @return
    List[KimaiActivity]: A list of activities.
    """
    try:
        response = kimai_service.get_activities()

        return response
    except HTTPError as err:
        logger.error(err)
        return err.response.json()


@mcp.tool()
async def kimai_get_activity(id: int) -> KimaiActivityEntity:
    """
    Fetches a specific activity whose id matches.

    @param
    id[int]: Specific activity id.

    @return
    KimaiActivityEntity: The found activity.
    """
    try:
        response = kimai_service.get_activity(id)

        return response
    except HTTPError as err:
        logger.error(err)
        return err.response.json()


@mcp.tool()
async def kimai_list_customers() -> List[KimaiCustomer]:
    """
    Fetches available customers in the system.

    @return
    List[KimaiCustomer]: The list of available customers.
    """
    try:
        response = kimai_service.get_customers()

        return response
    except HTTPError as err:
        logger.error(err)
        return err.response.json()


@mcp.tool()
async def kimai_create_timesheet(timesheet: KimaiTimesheet) -> KimaiTimesheetEntity:
    """
    Creates the provided timesheet in the system.

    @param
    timesheet[KimaiTimesheet]: The activity to be created.
        begin: datetime
        end: Optional[datetime] = None
        project: int
        activity: int
        description: Optional[str] = None
        fixedRate: Optional[str] = None
        hourlyRate: Optional[str] = None
        user: Optional[int] = None
        exported: Optional[bool] = None
        billable: Optional[bool] = None
        tags: List[str] = []

    @return
    KimaiTimesheetEntity: The created timesheet.
    """
    try:
        response = kimai_service.create_timesheet(timesheet)

        return response
    except HTTPError as err:
        logger.error(err)
        return err.response.json()


@mcp.tool()
async def kimai_update_timesheet(
    id: int, timesheet: KimaiTimesheet
) -> KimaiTimesheetEntity:
    """
    Edits the specified timesheet that matches the id.

    @param
    timesheet[KimaiTimesheet]: The activity to be edited.

    @return
    KimaiTimesheetEntity: The created timesheet.
    """
    try:
        response = kimai_service.update_timesheet(id, timesheet)

        return response
    except HTTPError as err:
        logger.error(err)
        return err.response.json()


@mcp.tool()
async def kimai_list_recent_timesheets() -> List[KimaiTimesheetCollectionDetails]:
    """
    Fetches the user's recent timesheets.

    @return
    List[KimaiTimesheetCollectionDetails] = A list of the recent timesheets.
    """
    try:
        response = kimai_service.get_recent_timesheets()

        return response
    except HTTPError as err:
        logger.error(err)

        return err.response.json()


@mcp.tool()
async def kimai_list_projects() -> List[Any]:
    """
    Fetches the available projects.

    @return
    List[KimaiProjectCollection] = A list of the available projects.
    """
    try:
        response = kimai_service.get_projects()

        return response
    except HTTPError as err:
        logger.error(err)
        return err.response.json()


@mcp.tool()
async def kimai_list_timesheets() -> List[KimaiTimesheetCollection]:
    """
    Fetches the available timesheets.

    @return
    List[KimaiProjectCollection] = A list of the available projects.
    """
    try:
        response = kimai_service.get_timesheets()

        return response
    except HTTPError as err:
        logger.error(err)
        return err.response.json()


@mcp.tool()
async def kimai_get_timesheet(id: int) -> KimaiTimesheetEntity:
    """
    Fetches a specific timesheet whose id matches.

    @param
    id[int]: Specific timesheet id.

    @return
    KimaiTimesheetEntity: The found timesheet.
    """
    try:
        response = kimai_service.get_timesheet(id)

        return response
    except HTTPError as err:
        logger.error(err)
        return err.response.json()


@mcp.tool()
def kimai_context_download():
    """
    Downloads latest metafile info such as activities, customers, projects, user
    timesheets, tags and descriptions.
    """
    response = get_meta()

    return response


@mcp.tool()
def kimai_get_ids(
    customer: str = "", project: str = "", activity: str = ""
) -> Dict[str, str]:
    """
    Fetches the ids for the provided customer, project and activity names.

    @param
    customer[str]: The customer name to search for.
    project[str]: The project name to search for.
    activity[str]: The activity name to search for.

    @return
    Dict[str, str]: A dictionary containing the found ids.
    """
    fetch_ids = {
        "customer": customer,
        "project": project,
        "activity": activity,
    }

    ids = kimai_service.get_ids(fetch_ids)

    return {k: str(v) for k, v in ids.items()}


@mcp.resource("file://kimai_activities.json")
def get_activities() -> List[KimaiActivity]:
    """
    Fetches Kimai activities locally if they exist. Else, they are requested and
    saved from the API.
    """
    activities = None

    try:
        activities = [
            KimaiActivity(**cast(Dict, activity))
            for activity in storage_service.read_json("kimai_activities.json")
        ]
    except Exception as err:
        logger.error(f"{err}")
        activities = kimai_service.get_activities()
        activities_joined = ",\n".join(
            [activity.model_dump_json() for activity in activities]
        )
        storage_service.write("kimai_activities.json", f"[\n{activities_joined}\n]")

    return activities


@mcp.resource("file://kimai_customers.json")
def get_customers() -> List[KimaiCustomer]:
    """
    Fetches Kimai customers locally if they exist. Else, they are requested and
    saved from the API.
    """
    customers = None

    try:
        customers = [
            KimaiCustomer(**cast(Dict, customer))
            for customer in storage_service.read_json("kimai_customers.json")
        ]
    except Exception as err:
        logger.error(f"{err}")
        customers = kimai_service.get_customers()
        customers_joined = ",\n".join(
            [customer.model_dump_json() for customer in customers]
        )
        storage_service.write("kimai_customers.json", f"[\n{customers_joined}\n]")

    return customers


@mcp.resource("file://kimai_tags.txt")
def get_tags() -> List[str]:
    """
    Fetches Kimai tags locally if they exist. Else, they are requested and
    saved from the API.
    """
    tags = None

    try:
        tags = cast(List[str], storage_service.read("kimai_tags.txt"))
    except Exception as err:
        logger.error(f"{err}")
        tags = kimai_service.get_tags()
        storage_service.write("kimai_tags.txt", ",\n".join(tags))

    return tags


@mcp.resource("file://kimai_timesheets.json")
def get_timesheets() -> List[KimaiTimesheet]:
    """
    Fetches Kimai timesheets locally if they exist. Else, they are requested and
    saved from the API.
    """
    timesheets = None

    try:
        timesheets = [
            KimaiTimesheet(**cast(Dict, timesheet))
            for timesheet in storage_service.read_json("kimai_timesheets.json")
        ]
    except Exception as err:
        logger.error(f"{err}")
        timesheets = kimai_service.get_timesheets()
        timesheets_joined = ",\n".join(
            [timesheet.model_dump_json() for timesheet in timesheets]
        )
        storage_service.write("kimai_timesheets.json", f"[\n{timesheets_joined}\n]")

    return timesheets


@mcp.resource("file://kimai_projects.json")
def get_projects() -> List[KimaiProject]:
    """
    Fetches Kimai projects locally if they exist. Else, they are requested and
    saved from the API.
    """
    projects = None

    try:
        projects = [
            KimaiProject(**cast(Dict, project))
            for project in storage_service.read_json("kimai_projects.json")
        ]
    except Exception as err:
        logger.error(f"{err}")
        projects = kimai_service.get_projects()
        projects_joined = ",\n".join(
            [project.model_dump_json() for project in projects]
        )
        storage_service.write("kimai_projects.json", f"[\n{projects_joined}\n]")

    return projects


if __name__ == "__main__":
    HTTP_TRANSPORT = os.getenv("MCP_HTTP_TRANSPORT", "stdio")
    PORT = os.getenv("PORT", 8000)

    try:
        get_meta()
        match HTTP_TRANSPORT:
            case "http":
                mcp.run(transport=HTTP_TRANSPORT, port=int(PORT))
            case "stdio":
                mcp.run(transport=HTTP_TRANSPORT)
    except Exception as err:
        logger.error(f"Fatal error: {err}")
        sys.exit(1)
