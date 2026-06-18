from fastapi import FastAPI
import uvicorn
import logging
from routes import agent_routes, mission_routes, report_routes
from database.db_connection import DBConnection

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("logs/app.log", encoding="utf-8"),
    ],
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


DBConnection.create_database()
DBConnection.create_tables()

app = FastAPI()


app.include_router(agent_routes.router, prefix="/agents", tags=["agents"])
app.include_router(mission_routes.router, prefix="/missions", tags=["missions"])
app.include_router(report_routes.router, prefix="/reports", tags=["reports"])


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8080, reload=True)
