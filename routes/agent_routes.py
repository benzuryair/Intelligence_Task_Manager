from database.agent_db import AgentDB
from fastapi import APIRouter, HTTPException
import logging
from pydantic import BaseModel, Field
from typing import Literal

router = APIRouter()


class Agent(BaseModel):
    name: str = Field(max_length=50)
    specialty: str = Field(max_length=50)
    is_active: bool = Field(default=True)
    agent_rank: Literal["Junior", "Senior", "Commander"]


class UpdateAgent(BaseModel):
    name: str | None = Field(default=None, max_length=50)
    specialty: str | None = Field(default=None, max_length=50)
    is_active: bool | None = Field(default=None)
    agent_rank: Literal["Junior", "Senior", "Commander"] | None = None


@router.post("", status_code=201)
def router_create_agent(body: Agent):
    logging.info("POST/agents")
    body = body.model_dump()

    agent = AgentDB.create_agent(body)
    if agent:
        logging.info(f"Agent created successfully: id={agent["id"]}")
        return agent
    else:
        logging.error("Something went wrong.")
        return {"Message": "Something went wrong"}


@router.get("")
def router_get_all_agents():
    logging.info("GET/agents")
    agents = AgentDB.get_all_agents()
    logging.info("The system successfully returned all agents.")
    return agents


@router.get("/{id}")
def router_get_agent_by_id(id: int):
    logging.info("/GET/agents/{id} ")
    agent = AgentDB.get_agent_by_id(id)
    if agent:
        logging.info("The system successfully returned the agent.")
        return agent
    else:
        logging.error(f"Agent not found: {id}")
        raise HTTPException(status_code=404, detail=f"message: Agent not found: {id}")


@router.put("/{id}")
def router_update_agent(id: int, body: UpdateAgent):
    logging.info("POT/agents/{id}")
    body = body.model_dump(exclude_none=True)
    changed = AgentDB.update_agent(id, body)
    if changed:
        logging.info(f"agent id:{id} details have been updated successfully")
        return {"message": f"agent id:{id} details have been updated successfully"}
    else:
        logging.error(f"No agent with such ID:{id} found.")
        raise HTTPException(
            status_code=404, detail=f"message: No agent with such ID:{id} found."
        )


@router.put("/{id}/deactivate")
def router_deactivate_agent(id: int):
    logging.info("POT/agents/{id}/deactivate")
    agent = AgentDB.get_agent_by_id(id)
    if agent is None:
        logging.info(f"Cannot deactivate. agent ID:{id} does not exist.")
        raise HTTPException(status_code=404, detail=f"No agent found with ID: {id}")

    if not agent["is_active"]:
        logging.error(
            "The agent has already been deactivated and cannot be deactivated again"
        )
        raise HTTPException(
            status_code=400,
            detail="The agent has already been deactivated and cannot be deactivated again",
        )

    AgentDB.deactivate_agent(id)
    logging.info("The system successfully deactivated the agent")
    return {"message": "The system successfully deactivated the agent"}


@router.get("/{id}/performance")
def router_get_agent_performance(id: int):
    logging.info("GET/agents/{id}/performance")
    summary_dict = AgentDB.get_agent_performance(id)
    if summary_dict:
        logging.info(
            f"The system successfully returned the performance of agent ID = {id}"
        )
        return summary_dict
    else:
        logging.error(f"No agent with such ID:{id} found.")
        return {"message": f"No agent with such ID:{id} found."}
