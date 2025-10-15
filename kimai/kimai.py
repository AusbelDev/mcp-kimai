import logging
import dotenv
import sys

from requests.exceptions import HTTPError
from datetime import datetime, timedelta
from kimai.models.timesheet import KimaiTimesheet, KimaiTimesheetEntity
from kimai.services.kimai.kimai import KimaiService
from fastmcp import FastMCP

# # Configure logging to stderr
# logging.basicConfig(
#     level=logging.INFO,
#     format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
#     stream=sys.stderr,
# )
# logger = logging.getLogger("kimai-server")
# 
# # Initialize MCP server - NO PROMPT PARAMETER!
# mcp = FastMCP("kimai")

dotenv.load_dotenv()

if(__name__ == "__main__"):
  now = datetime.now()
  dotenv.load_dotenv()

  kimai_service = KimaiService.get_instance()
  my_timesheet = KimaiTimesheet(**{
    "begin": now.isoformat(),
    "end": now + timedelta(minutes = 30),
    "customer": 3,
    "project": 109,
    "activity": 338,
    "description": "Actividad creada desde Python",
  })

  try:
    # created_timesheet = kimai_service.create_timesheet(my_timesheet)
    # print(created_timesheet.model_dump_json(indent = 2))

    # updated_timesheet_body = KimaiTimesheet(**{
    #   "begin": now - timedelta(minutes = 90),
    #   "end": now - timedelta(minutes = 60),
    #   "project": 109,
    #   "activity": 338,
    #   "description": "Actividad actualizada desde Python",
    # })

    # updated_timesheet = kimai_service.update_timesheet(272474, updated_timesheet_body)
    # print(updated_timesheet.model_dump_json(indent = 2))

    # kimai_service.delete_timesheet(272213)
    pass

  except HTTPError as err:
    print(err.request.body)
    print(err.response.json())


