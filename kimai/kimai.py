from kimai.services.kimai.kimai import KimaiService
from fastmcp import FastMCP
import logging
import dotenv
import sys

# Configure logging to stderr
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger("kimai-server")

# Initialize MCP server - NO PROMPT PARAMETER!
mcp = FastMCP("kimai")

dotenv.load_dotenv()

if(__name__ == "__main__"):
  dotenv.load_dotenv()

  kimai_service = KimaiService.get_instance()
