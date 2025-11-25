from research_crew.src.research_crew.main import app as fastapi_app
from mangum import Mangum

handler = Mangum(fastapi_app)
