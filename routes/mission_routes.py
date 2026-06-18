from database.agent_db import AgentDB
from database.mission_db import MissionDB
from fastapi import APIRouter, HTTPException
import logging
from pydantic import BaseModel, Field

router = APIRouter()


class Mission(BaseModel):
    title: str = Field(max_length=50)
    description: str
    location: str = Field(max_length=50)
    difficulty: int = Field(ge=1, le=10)
    importance: int = Field(ge=1, le=10)


class UpdateMission(BaseModel):
    title: str | None = Field(default=None, max_length=50)
    description: str | None = None
    location: str | None = Field(default=None, max_length=50)
    difficulty: int | None = Field(default=None, ge=1, le=10)
    importance: int | None = Field(default=None, ge=1, le=10)


@router.post("")
def router_create_mission(body: Mission):
    logging.info("POST/missions")
    body = body.model_dump(exclude_none=True)
    mission = MissionDB.create_mission(body)
    if mission:
        logging.info(f"mission created successfully: id={mission["id"]}")
        return mission
    else:
        logging.error("Something went wrong.")
        return {"Message": "Something went wrong"}


@router.get("")
def router_get_all_missions():
    logging.info("GET/missions")
    missions = MissionDB.get_all_missions()
    logging.info("The system successfully returned all missions")
    return missions


@router.get("/{id}")
def router_get_agent_by_id(id: int):
    logging.info("/GET/missions/{id} ")
    mission = MissionDB.get_mission_by_id(id)
    if mission:
        logging.info("The system successfully returned the mission")
        return mission
    else:
        logging.error(f"mission not found: {id}")
        raise HTTPException(status_code=404, detail=f"message: mission not found: {id}")


@router.put("/{id}/assign/{agent_id}")
def router_assign_mission(id: int, agent_id: int):
    logging.info("PUT/missions/{id}/assign/{agent_id}")

    mission = MissionDB.get_mission_by_id(id)

    if mission is None:
        logging.error(f"mission ID:{id} does not exist")
        raise HTTPException(status_code=404, detail="Mission not found")

    agent = AgentDB.get_agent_by_id(agent_id)
    if agent is None:
        logging.error(f"There is no agent with ID:{agent_id}")
        raise HTTPException(status_code=404, detail="Agent not found")

    if mission["status"] != "NEW":
        logging.error("Mission not available")
        raise HTTPException(status_code=400, detail="Mission not available")

    if not agent["is_active"]:
        logging.error("Agent is not active")
        raise HTTPException(status_code=400, detail="Agent is not active")

    open_missions = MissionDB.get_open_missions_by_agent(agent_id)
    if len(open_missions) >= 3:
        logging.error(f"Agent has reached maximum missions: id={agent_id}")
        raise HTTPException(
            status_code=400, detail="Agent has reached maximum missions"
        )

    if mission["risk_level"] == "CRITICAL" and agent["agent_rank"] != "Commander":
        logging.error("Only Commander can handle critical missions")
        raise HTTPException(
            status_code=400, detail="Only Commander can handle critical missions"
        )

    changed = MissionDB.assign_mission(id, agent_id)
    if changed:
        return {"Message": "mission assignment was successful."}
    else:
        logging.error("Something went wrong.")
        return {"Message": "Something went wrong"}


@router.put("/{id}/start")
def router_start_mission(id: int):
    logging.info("PUT/missions/{id}/start")
    mission = MissionDB.get_mission_by_id(id)
    if mission is None:
        logging.error(f"mission ID:{id} not found")
        raise HTTPException(status_code=404, detail=f"mission ID:{id} not found")

    if mission["status"] != "ASSIGNED":
        logging.error("you can start a mission only if the mission status is ASSIGNED")
        raise HTTPException(
            status_code=400,
            detail="you can start a mission only if the mission status is ASSIGNED",
        )
    changed = MissionDB.update_mission_status(id, "IN_PROGRESS")
    if changed:
        logging.info("Mission started successfully")
        return {"message": "Mission started successfully"}
    else:
        logging.error("Something went wrong.")
        return {"Message": "Something went wrong"}


@router.put("/{id}/complete")
def router_complete_mission(id: int):
    logging.info("PUT/missions/{id}/complete")

    mission = MissionDB.get_mission_by_id(id)
    if mission is None:
        logging.error(f"mission ID:{id} not found")
        raise HTTPException(status_code=404, detail=f"mission ID:{id} not found")

    if mission["status"] != "IN_PROGRESS":
        logging.error(
            "you can complete a mission only if the mission status is IN_PROGRESS"
        )
        raise HTTPException(
            status_code=400,
            detail="you can complete a mission only if the mission status is IN_PROGRESS",
        )

    changed = MissionDB.update_mission_status(id, "COMPLETED")
    if changed:
        agent_id = mission.get("assigned_agent_id")
        if agent_id:
            AgentDB.increment_completed(agent_id)
        logging.info("Mission COMPLETED successfully")
        return {"message": "Mission COMPLETED successfully"}
    else:
        logging.error("Something went wrong.")
        return {"Message": "Something went wrong"}


@router.put("/{id}/fail")
def router_fail_mission(id: int):
    logging.info("PUT/missions/{id}/fail")

    mission = MissionDB.get_mission_by_id(id)
    if mission is None:
        logging.error(f"mission ID:{id} not found")
        raise HTTPException(status_code=404, detail=f"mission ID:{id} not found")

    if mission["status"] != "IN_PROGRESS":
        logging.error(
            "you can fail a mission only if the mission status is IN_PROGRESS"
        )
        raise HTTPException(
            status_code=400,
            detail="you can fail a mission only if the mission status is IN_PROGRESS",
        )

    changed = MissionDB.update_mission_status(id, "FAILED")
    if changed:
        agent_id = mission.get("assigned_agent_id")
        if agent_id:
            AgentDB.increment_failed(agent_id)
        logging.info("Mission faild successfully")
        return {"message": "Mission faild successfully"}
    else:
        logging.error("Something went wrong.")
        return {"Message": "Something went wrong"}


@router.put("/{id}/cancel")
def router_cancel_mission(id: int):
    logging.info("/missions/{id}/cancel")

    mission = MissionDB.get_mission_by_id(id)
    if mission is None:
        logging.error(f"mission ID:{id} not found")
        raise HTTPException(status_code=404, detail=f"mission ID:{id} not found")

    if mission["status"] not in ["ASSIGNED", "NEW"]:
        logging.error(
            "you can cancel a mission only if the mission status is ASSIGNED or NEW"
        )
        raise HTTPException(
            status_code=400,
            detail="you can cancel a mission only if the mission status is ASSIGNED or NEW",
        )

    changed = MissionDB.update_mission_status(id, "CANCELLED")
    if changed:
        logging.info("Mission canceld successfully")
        return {"message": "Mission canceld successfully"}
    else:
        logging.error("Something went wrong.")
        return {"Message": "Something went wrong"}
