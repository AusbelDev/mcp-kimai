import logging
import dotenv
import sys
import os

from typing import Any, List
from fastmcp import FastMCP
from requests.models import HTTPError

from kimai.models.activity import KimaiActivity, KimaiActivityEntity
from kimai.models.customer import KimaiCustomer
from kimai.models.misc import KimaiVersion
from kimai.models.timesheet import KimaiTimesheet, KimaiTimesheetEntity
from kimai.services.kimai.kimai import KimaiService

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger("kimai-server")

dotenv.load_dotenv()

mcp = FastMCP(os.getenv("MCP_SERVER_NAME", "Kimai-MCP"))
kimai_service = KimaiService.get_instance()

@mcp.tool()
async def kimai_ping() -> str:
  try:
    response = kimai_service.ping()

    return response
  except HTTPError as err:
    print(err)
    return err.response.json()

@mcp.tool()
async def kimai_version() -> KimaiVersion:
  try:
    response = kimai_service.version()

    return response
  except HTTPError as err:
    print(err)
    return err.response.json()

@mcp.tool()
async def kimai_list_activities() -> List[KimaiActivity]:
  try:
    response = kimai_service.get_activities()

    return response
  except HTTPError as err:
    print(err)
    return err.response.json()

@mcp.tool()
async def kimai_get_activity(id: int) -> KimaiActivityEntity:
  try:
    response = kimai_service.get_activity(id)

    return response
  except HTTPError as err:
    print(err)
    return err.response.json()

@mcp.tool()
async def kimai_list_customers() -> List[KimaiCustomer]:
  try:
    response = kimai_service.get_customers()

    return response
  except HTTPError as err:
    print(err)
    return err.response.json()

@mcp.tool()
async def kimai_create_timesheet(timesheet: KimaiTimesheet) -> KimaiTimesheetEntity:
  try:
    response = kimai_service.create_timesheet(timesheet)

    return response
  except HTTPError as err:
    print(err)
    return err.response.json()

@mcp.tool()
async def kimai_update_timesheet(id: int, timesheet: KimaiTimesheet) -> KimaiTimesheetEntity:
  try:
    response = kimai_service.update_timesheet(id, timesheet)

    return response
  except HTTPError as err:
    print(err)
    return err.response.json()

@mcp.tool()
async def kimai_list_projects() -> List[Any]:
  try:
    response = kimai_service.get_projects()

    return response
  except HTTPError as err:
    print(err)
    return err.response.json()

# TODO
@mcp.tool()
async def kimai_list_timesheets() -> List[Any]:
  try:
    response = kimai_service.version()

    return response
  except HTTPError as err:
    print(err)
    return err.response.json()

if(__name__ == "__main__"):
  HTTP_TRANSPORT = os.getenv("HTTP_TRANSPORT", "http")
  PORT = os.getenv("PORT", 8000)
  logger.warning(f'{HTTP_TRANSPORT}, {PORT}')

  try:
    mcp.run(transport = 'http', port = PORT)
  except Exception:
    sys.exit(1)
