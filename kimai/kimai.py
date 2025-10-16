from datetime import datetime
import logging
import dotenv
import sys
import os

from typing import Any, Dict, List, cast
from fastmcp import FastMCP
from requests.models import HTTPError

from kimai.models.activity import KimaiActivity, KimaiActivityEntity
from kimai.models.customer import KimaiCustomer
from kimai.models.misc import KimaiVersion, MCPContextMeta
from kimai.models.project import KimaiProject
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

    logger.warning(f'MCP context already existing. It\'s been {difference} day{"s" if difference != 1 else ""} since last download')

  except Exception as err:
    logger.warning(f'{err}')

  if(meta and difference <= 7): return
  logger.warning(f'Automatically downloading most recent context.')

  activities = kimai_service.get_activities()
  customers = kimai_service.get_customers()
  tags = kimai_service.get_tags()
  timesheets = kimai_service.get_timesheets()
  projects = kimai_service.get_projects()

  timesheet_descs = [timesheet.description for timesheet in timesheets if timesheet.description]

  storage_service.write("kimai_activities.json", f'[\n{",\n".join([activity.model_dump_json() for activity in activities])}\n]')
  storage_service.write("kimai_customers.json", f'[\n{",\n".join([activity.model_dump_json() for activity in customers])}\n]')
  storage_service.write("kimai_timesheets.json", f'[\n{",\n".join([activity.model_dump_json() for activity in timesheets])}\n]')
  storage_service.write("kimai_projects.json", f'[\n{",\n".join([activity.model_dump_json() for activity in projects])}\n]')
  storage_service.write("kimai_tags.txt", ",\n".join(tags))
  storage_service.write("kimai_timesheet_descriptions.txt", ",\n".join(timesheet_descs))

  storage_service.write("mcp_context_meta.json", MCPContextMeta().model_dump_json(indent = 2))

  return

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
    print(err)
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
    print(err)
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
    print(err)
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
    print(err)
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
    print(err)
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
    print(err)
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
    print(err)
    return err.response.json()

@mcp.tool()
async def kimai_list_recent_activities() -> List[KimaiTimesheetCollectionDetails]:
  """
    Fetches the user's recent timesheets.

    @return
    List[KimaiTimesheetCollectionDetails] = A list of the recent timesheets.
  """
  try:
    response = kimai_service.get_recent_timesheets()

    return response
  except HTTPError as err:
    print(err)

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
    print(err)
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
    print(err)
    return err.response.json()

@mcp.tool()
def context_download():
  """
  Downloads latest metadata info such as activities, customers, projects, user
  timesheets, tags and descriptions.
  """
  get_meta()

@mcp.resource("data://kimai_activities")
def get_activities() -> List[KimaiActivity]:
  """
  Fetches Kimai activities locally if they exist. Else, they are requested and
  saved from the API.
  """
  activities = None

  try:
    activities = [KimaiActivity(**cast(Dict, activity)) for activity in storage_service.read_json("kimai_activities.json")]
  except:
    activities = kimai_service.get_activities()
    storage_service.write("kimai_activities.json", f'[\n{",\n".join([activity.model_dump_json() for activity in activities])}\n]')

  return activities

@mcp.resource("data://kimai_customers")
def get_customers() -> List[KimaiCustomer]:
  """
  Fetches Kimai customers locally if they exist. Else, they are requested and
  saved from the API.
  """
  customers = None

  try:
    customers = [KimaiCustomer(**cast(Dict, customer)) for customer in storage_service.read_json("kimai_customers.json")]
  except:
    customers = kimai_service.get_customers()
    storage_service.write("kimai_customers.json", f'[\n{",\n".join([customer.model_dump_json() for customer in customers])}\n]')

  return customers

@mcp.resource("data://kimai_tags")
def get_tags() -> List[str]:
  """
  Fetches Kimai tags locally if they exist. Else, they are requested and
  saved from the API.
  """
  tags = None

  try:
    tags = cast(List[str], storage_service.read("kimai_tags.json"))
  except:
    tags = kimai_service.get_tags()
    storage_service.write("kimai_tags.txt", ",\n".join(tags))

  return tags

@mcp.resource("data://kimai_timesheets")
def get_timesheets() -> List[KimaiTimesheet]:
  """
  Fetches Kimai timesheets locally if they exist. Else, they are requested and
  saved from the API.
  """
  timesheets = None

  try:
    timesheets = [KimaiTimesheet(**cast(Dict, timesheet)) for timesheet in storage_service.read_json("kimai_timesheets.json")]
  except:
    timesheets = kimai_service.get_timesheets()
    storage_service.write("kimai_timesheets.json", f'[\n{",\n".join([timesheet.model_dump_json() for timesheet in timesheets])}\n]')

  return timesheets

@mcp.resource("data://kimai_projects")
def get_projects() -> List[KimaiProject]:
  """
  Fetches Kimai projects locally if they exist. Else, they are requested and
  saved from the API.
  """
  projects = None

  try:
    projects = [KimaiProject(**cast(Dict, project)) for project in storage_service.read_json("kimai_projects.json")]
  except:
    projects = kimai_service.get_projects()
    storage_service.write("kimai_projects.json", f'[\n{",\n".join([project.model_dump_json() for project in projects])}\n]')

  return projects

if(__name__ == "__main__"):
  HTTP_TRANSPORT = os.getenv("HTTP_TRANSPORT", "http")
  PORT = os.getenv("PORT", 8000)

  try:
    get_meta()
    mcp.run(transport = "stdio")
  except Exception as err:
    sys.exit(1)
