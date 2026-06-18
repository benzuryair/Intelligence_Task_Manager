from database.agent_db import AgentDB
from database.mission_db import MissionDB
from fastapi import APIRouter, HTTPException
import logging
from pydantic import BaseModel, Field
from typing import Literal

router = APIRouter()


@router.get("/summary")
def router_summary():
    logging.info("GET/reports/summary")
    active_agents_count = AgentDB.count_active_agents()
    total_missions = MissionDB.count_all_missions()
    open_missions = MissionDB.count_open_missions()
    completed_missions = MissionDB.count_by_status("COMPLETED")
    failed_missions = MissionDB.count_by_status("FAILED")
    critical_missions = MissionDB.count_critical_missions()
    summary_dict = {
        "active_agents_count": active_agents_count["active_agents"],
        "total_missions": total_missions["total_tasks"],
        "open_missions": open_missions["open_tasks"],
        "completed_missions": completed_missions["COUNT"],
        "failed_missions": failed_missions["COUNT"],
        "critical_missions": critical_missions["critical_tasks"],
    }
    logging.info("The system successfully returned the summary")
    return summary_dict


@router.get("/missions-by-status")
def router_count_by_status():
    logging.info("GET/reports/missions-by-status")
    list_of_status = [
        "NEW",
        "ASSIGNED",
        "IN_PROGRESS",
        "COMPLETED",
        "FAILED",
        "CANCELLED",
    ]
    results_dict = {}
    for status in list_of_status:
        result = MissionDB.count_by_status(status)
        results_dict[f"{status.lower()}"] = result["COUNT"]
    logging.info("The system successfully returned the summary by status.")
    return results_dict


@router.get("/top-agent")
def router_get_top_agent():
    logging.info("GET/reports/top-agent")
    top_agent = MissionDB.get_top_agent()
    if top_agent["completed_missions"] > 0:
        logging.info("The system successfully returned the best agent")
        return top_agent
    else:
        logging.error("No agent with completed missions found")
        raise HTTPException(
            status_code=404, detail="No agent with completed missions found"
        )
