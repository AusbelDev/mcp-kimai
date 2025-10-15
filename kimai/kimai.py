from kimai.services.kimai.kimai import KimaiService
import dotenv

if(__name__ == "__main__"):
  dotenv.load_dotenv()

  kimai_service = KimaiService.get_instance()
