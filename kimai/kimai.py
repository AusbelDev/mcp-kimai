from datetime import datetime
import logging

from requests import Request
import dotenv
import sys
import os

from typing import Any, Dict, List, Optional, cast
from fastmcp import FastMCP
from requests.models import HTTPError

from starlette.responses import PlainTextResponse
from starlette.requests import Request
from kimai.models.activity import KimaiActivity, KimaiActivityEntity
from kimai.models.customer import KimaiCustomer
from kimai.models.misc import KimaiVersion, MCPContextMeta
from kimai.models.project import KimaiProject, KimaiProjectCollection
from kimai.models.timesheet import KimaiTimesheet, KimaiTimesheetCollection, KimaiTimesheetCollectionDetails, KimaiTimesheetEntity
from kimai.services.kimai.kimai import KimaiService
from kimai.services.storage.store import DiskStorageService

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

def get_meta() -> None:
  meta = None
  difference = 0

  try:
    meta = MCPContextMeta(**storage_service.read_json("mcp_context_meta.json"))
    difference = (datetime.now() - meta.last_update).days

    logger.error(f'MCP context already existing. It\'s been {difference} day{"s" if difference != 1 else ""} since last download')

  except Exception as err:
    logger.error(f'{err}')

  if(meta and difference <= 7): 
    return
  logger.error('Automatically downloading most recent context.')

  activities = kimai_service.get_activities()
  customers = kimai_service.get_customers()
  tags = kimai_service.get_tags()
  timesheets = kimai_service.get_timesheets()
  projects = kimai_service.get_projects()

  timesheet_descs = [timesheet.description for timesheet in timesheets if timesheet.description]

  activities_joined = ",\n".join([activity.model_dump_json() for activity in activities])
  customers_joined = ",\n".join([customer.model_dump_json() for customer in customers])
  tags_joined = ",\n".join(tags)
  timesheets_joined = ",\n".join([timesheet.model_dump_json() for timesheet in timesheets])
  projects_joined = ",\n".join([project.model_dump_json() for project in projects])

  storage_service.write("kimai_activities.json", f'[\n{activities_joined}\n]')
  storage_service.write("kimai_customers.json", f'[\n{customers_joined}\n]')
  storage_service.write("kimai_timesheets.json", f'[\n{timesheets_joined}\n]')
  storage_service.write("kimai_projects.json", f'[\n{projects_joined}\n]')
  storage_service.write("kimai_tags.txt", tags_joined)
  storage_service.write("kimai_timesheet_descriptions.txt", ",\n".join(timesheet_descs))

  storage_service.write("mcp_context_meta.json", MCPContextMeta().model_dump_json(indent = 2))

  return

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
async def kimai_list_activities(params: Optional[Dict[str, Any]]) -> List[KimaiActivity]:
  """
    List available activities for the user. It allows for a deeper search by
    several criteria like:

    project: Optional[str] = None
    projects: Optional[List[str]] = None
    visible: Optional[VisibilityOptions] = None
    globals: Optional[bool] = None
    orderBy: Optional[OrderByOptions] = "name"
    order: Optional[OrderDirectionOptions] = "ASC"
    term: Optional[str] = None

    @param
    params[Optional[IKimaiFetchActivitiesParams]]: A set of params for deepening
    the search. By default all params are disabled.

    @return
    List[KimaiActivity]: A list of activities.
  """
  activities = None

  try:
    if(params):
      logger.info("Fetching parameterized request from API")
      activities = kimai_service.get_activities(params)

      return activities

    if(storage_service.file_exists("kimai_activities.json")):
      logger.info("Fetching available activities from local store")

      activities = [KimaiActivity(**cast(Dict, activity)) for activity in storage_service.read_json("kimai_activities.json")]

      return activities

    logger.info("Fetching default activities from API")

    activities = kimai_service.get_activities()
    activities_joined = ",\n".join([activity.model_dump_json() for activity in activities])
    storage_service.write("kimai_activities.json", f'[\n{activities_joined}\n]')

    return activities

  except Exception as err:
    logger.error(f'{err}')

  return []

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
    logger.info("Fetching available recent timesheets from local store")
    if(storage_service.file_exists("kimai_customers.json")):
      customers = [KimaiCustomer(**cast(Dict, customer)) for customer in storage_service.read_json("kimai_customers.json")]

      return customers

    logger.info("Fetching default timesheets from API")
    customers = kimai_service.get_customers()

    customers_joined = ",\n".join([customer.model_dump_json() for customer in customers])
    storage_service.write("kimai_customers.json", f'[\n{customers_joined}\n]')

    return customers

  except HTTPError as err:
    logger.error(err)
    return err.response.json()

@mcp.tool()
async def kimai_create_timesheet(timesheet: KimaiTimesheet) -> KimaiTimesheetEntity:
  """
    Creates the provided timesheet in the system.

    @param
    timesheet[KimaiTimesheet]: The activity to be created.

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
async def kimai_update_timesheet(id: int, timesheet: KimaiTimesheet) -> KimaiTimesheetEntity:
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
async def kimai_list_recent_timesheets(
  params: Optional[Dict[str, Any]]
) -> List[KimaiTimesheetCollectionDetails]:
  """
    Fetches the user's recent timesheets. It also allows to search by different
    criteria like:

    user: Optional[str] = None
    begin: Optional[datetime] = None
    size: Optional[int] = None

    @return
    List[KimaiTimesheetCollectionDetails] = A list of the recent timesheets.
  """
  try:
    if(params):
      logger.info("Fetching parameterized request from API")
      timesheets = kimai_service.get_recent_timesheets(params)

      return timesheets

    if(storage_service.file_exists("kimai_timesheets.json")):
      logger.info("Fetching available recent timesheets from local store")

      timesheets = [KimaiTimesheetCollectionDetails(**cast(Dict, activity)) for activity in storage_service.read_json("kimai_timesheets.json")]

      return timesheets

    logger.info("Fetching default timesheets from API")

    timesheets = kimai_service.get_recent_timesheets()
    timesheets_joined = ",\n".join([activity.model_dump_json() for activity in timesheets])
    storage_service.write("kimai_timesheets.json", f'[\n{timesheets_joined}\n]')

    return timesheets

  except Exception as err:
    logger.error(f'{err}')

  return []

@mcp.tool()
async def kimai_list_projects() -> List[KimaiProjectCollection]:
  """
    Fetches the available projects.

    @return
    List[KimaiProjectCollection] = A list of the available projects.
  """
  try:
    if(storage_service.file_exists("kimai_projects.json")):
      logger.info("Fetching available recent projects from local store")

      projects = [KimaiProjectCollection(**cast(Dict, activity)) for activity in storage_service.read_json("kimai_projects.json")]

      return projects

    logger.info("Fetching default projects from API")

    projects = kimai_service.get_projects()
    projects_joined = ",\n".join([activity.model_dump_json() for activity in projects])
    storage_service.write("kimai_projects.json", f'[\n{projects_joined}\n]')

    return projects

  except Exception as err:
    logger.error(f'{err}')

  return []

@mcp.tool()
async def kimai_list_timesheets(params: Optional[Dict[str, Any]]) -> List[KimaiTimesheetCollection]:
  """
    Fetches the available timesheets. It has several search parameterization by:

    user: Optional[str] = None
    customers: Optional[List[str]] = None
    projects: Optional[List[str]] = None
    activities: Optional[List[str]] = None
    page: Optional[int] = 1
    size: Optional[int] = 50
    tags: Optional[str] = None
    orderBy: Optional[OrderByOptions] = "name"
    order: Optional[OrderDirectionOptions] = "ASC"
    begin: Optional[datetime] = None
    end: Optional[datetime] = None
    active: Optional[bool] = None
    billable: Optional[bool] = None
    full: Optional[bool] = False
    term: Optional[str] = None
    modified_after: Optional[datetime] = None

    @return
    List[KimaiProjectCollection] = A list of the available projects.
  """
  try:
    if(params):
      logger.info("Fetching parameterized request from API")
      timesheets = kimai_service.get_timesheets(params)

      return timesheets

    if(storage_service.file_exists("kimai_timesheets.json")):
      logger.info("Fetching available timesheets from local store")

      timesheets = [KimaiTimesheetCollection(**cast(Dict, activity)) for activity in storage_service.read_json("kimai_timesheets.json")]

      return timesheets

    logger.info("Fetching default timesheets from API")

    timesheets = kimai_service.get_timesheets()
    timesheets_joined = ",\n".join([activity.model_dump_json() for activity in timesheets])
    storage_service.write("kimai_timesheets.json", f'[\n{timesheets_joined}\n]')

    return timesheets

  except Exception as err:
    logger.error(f'{err}')

  return []

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
  get_meta()

@mcp.resource("file://kimai_activities.json")
def get_activities() -> List[KimaiActivity]:
  """
  Fetches Kimai activities locally if they exist. Else, they are requested and
  saved from the API. It allows for a deeper search considering the following
  criteria:

  project: Optional[str] = None
  projects: Optional[List[str]] = None
  visible: Optional[VisibilityOptions] = None
  globals: Optional[bool] = None
  orderBy: Optional[OrderByOptions] = "name"
  order: Optional[OrderDirectionOptions] = "ASC"
  term: Optional[str] = None

  """
  activities = None

  try:
    activities = [KimaiActivity(**cast(Dict, customer)) for customer in storage_service.read_json("kimai_activities.json")]

  except Exception as err:
    logger.error(f'{err}')
    activities = kimai_service.get_activities()
    activities_joined = ",\n".join([customer.model_dump_json() for customer in activities])
    storage_service.write("kimai_activities.json", f'[\n{activities_joined}\n]')

  return activities

@mcp.resource("file://kimai_customers.json")
def get_customers() -> List[KimaiCustomer]:
  """
  Fetches Kimai customers locally if they exist. Else, they are requested and
  saved from the API.
  """
  customers = None

  try:
    customers = [KimaiCustomer(**cast(Dict, customer)) for customer in storage_service.read_json("kimai_customers.json")]
  except Exception as err:
    logger.error(f'{err}')
    customers = kimai_service.get_customers()
    customers_joined = ",\n".join([customer.model_dump_json() for customer in customers])
    storage_service.write("kimai_customers.json", f'[\n{customers_joined}\n]')

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
    logger.error(f'{err}')
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
    timesheets = [KimaiTimesheet(**cast(Dict, timesheet)) for timesheet in storage_service.read_json("kimai_timesheets.json")]
  except Exception as err:
    logger.error(f'{err}')
    timesheets = kimai_service.get_timesheets()
    timesheets_joined = ",\n".join([timesheet.model_dump_json() for timesheet in timesheets])
    storage_service.write("kimai_timesheets.json", f'[\n{timesheets_joined}\n]')

  return timesheets

@mcp.resource("file://kimai_projects.json")
def get_projects() -> List[KimaiProject]:
  """
  Fetches Kimai projects locally if they exist. Else, they are requested and
  saved from the API.
  """
  projects = None

  try:
    projects = [KimaiProject(**cast(Dict, project)) for project in storage_service.read_json("kimai_projects.json")]
  except Exception as err:
    logger.error(f'{err}')
    projects = kimai_service.get_projects()
    projects_joined = ",\n".join([project.model_dump_json() for project in projects])
    storage_service.write("kimai_projects.json", f'[\n{projects_joined}\n]')

  return projects

if(__name__ == "__main__"):
  # timesheets = kimai_service.get_timesheets({"begin": "2025-10-01T00:00:00", "end": "2025-10-01T23:59:59"})

  # for timesheet in timesheets:
  #   print(timesheet.model_dump_json(indent = 2))
  HTTP_TRANSPORT = os.getenv("MCP_HTTP_TRANSPORT", "stdio")
  PORT = os.getenv("PORT", 8000)

  try:
    get_meta()
    match(HTTP_TRANSPORT):
      case "http":
        mcp.run(transport = HTTP_TRANSPORT, host = "0.0.0.0", port = PORT)
      case "stdio":
        mcp.run(transport = HTTP_TRANSPORT)
  except Exception as err:
    logger.error(f'Fatal error: {err}')
    sys.exit(1)
