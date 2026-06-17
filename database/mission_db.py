from database.db_connection import connection
from database.agent_db import AgentDB


def risk_level_check(difficulty: int, importance: int):
    risk_level = (difficulty * 2) + importance
    if 0 <= risk_level <= 9:
        return "LOW"
    elif 10 <= risk_level <= 17:
        return "MEDIUM"
    elif 18 <= risk_level <= 24:
        return "HIGH"
    elif risk_level >= 25:
        return "CRITICAL"


class MissionDB:

    @staticmethod
    def get_all_missions():
        with connection.get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                query = """SELECT * FROM missions"""
                cursor.execute(query)
                rows = cursor.fetchall()
                return rows

    @staticmethod
    def get_mission_by_id(id: int):
        with connection.get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                query = """SELECT * from missions WHERE id =%s"""
                cursor.execute(query, (id,))
                row = cursor.fetchone()
                return row

    @staticmethod
    def create_mission(data: dict):
        with connection.get_connection() as conn:
            with conn.cursor() as cursor:
                risk_level = risk_level_check(data["difficulty"], data["importance"])
                query = """insert into missions(title, description, location, difficulty, importance, risk_level, status) values(%s, %s, %s, %s, %s, %s, True)"""
                values = list(data.values()) + [risk_level]
                cursor.execute(query, values)
                new_id = cursor.lastrowid
                conn.commit()
                mission = MissionDB.get_mission_by_id(new_id)
                return mission

    @staticmethod
    def assign_mission(m_id: int, a_id: int):
        with connection.get_connection() as conn:
            with conn.cursor() as cursor:
                agent = AgentDB.get_agent_by_id(a_id)
                if agent is None:
                    return {"message": f"There is no agent with ID:{a_id}"}

                if not agent["is_active"]:
                    return {
                        "message": f"Agent ID:{a_id} cannot accept a mission because it is inactive"
                    }

                open_missions = MissionDB.get_open_missions_by_agent(a_id)
                if len(open_missions) >= 3:
                    return {
                        "message": f"Agent ID: {a_id} holds 3 tasks and cannot add more"
                    }

                mission = MissionDB.get_mission_by_id(m_id)
                if mission is None:
                    return {"message": f"Task ID:{m_id} does not exist"}

                if (
                    mission["status"] == "CRITICAL"
                    and agent["agent_rank"] != "Commander"
                ):
                    return {"message": "Only a Commander can take on such a mission."}

                query = """UPDATE missions SET status = 'ASSIGNED', assigned_agent_id = %s WHERE id = %s"""
                cursor.execute(query, (a_id, m_id))
                changed = cursor.rowcount > 0
                conn.commit()
                return changed

    @staticmethod
    def update_mission_status(id: int, status: str):
        with connection.get_connection() as conn:
            with conn.cursor() as cursor:

                mission = MissionDB.get_mission_by_id(id)
                if mission is None:
                    return {"message": f"Task ID:{id} does not exist"}

                if status == "ASSIGNED" and mission["status"] != "NEW":
                    return {
                        "message": "You can only update a task to ASSIGNED when its current status is NEW"
                    }

                if status == "IN_PROGRESS" and mission["status"] != "ASSIGNED":
                    return {
                        "message": "You can only update a task to IN_PROGRESS when its current status is ASSIGNED"
                    }

                if (
                    status in ["completed", "failed"]
                    and mission["status"] != "IN_PROGRESS"
                ):
                    return {
                        "message": "You can only update a task to completed or failed when its current status is IN_PROGRESS"
                    }

                if status == "CANCELLED" and mission["status"] not in [
                    "NEW",
                    "ASSIGNED",
                ]:
                    return {
                        "message": "You can only update a task to CANCELLED when its current status is NEW or ASSIGNED"
                    }

                query = """UPDATE missions SET status = %s WHERE id = %s"""
                cursor.execute(query, (status, id))
                changed = cursor.rowcount > 0
                conn.commit()
                return changed

    @staticmethod
    def get_open_missions_by_agent(id: int):
        with connection.get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                query = """SELECT * FROM missions
                WHERE (status = "ASSIGNED" or status = "IN_PROGRESS") and assigned_agent_id = %s"""
                cursor.execute(query, (id,))
                rows = cursor.fetchall()
                return rows

    @staticmethod
    def count_all_missions():
        with connection.get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                query = """SELECT COUNT(*) as 'total_tasks' FROM missions"""
                cursor.execute(query)
                row = cursor.fetchone()
                return row

    @staticmethod
    def count_by_status(status: str):
        with connection.get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                query = """SELECT status AS Status, COUNT(*) as COUNT
                FROM missions
                where status = %s"""
                cursor.execute(query, (status,))
                row = cursor.fetchone()
                return row

    @staticmethod
    def count_open_missions():
        with connection.get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                query = """SELECT COUNT(*) AS 'open_tasks' FROM missions 
                WHERE status = "NEW" or status = "ASSIGNED" or status = "IN_PROGRESS"
                """
                cursor.execute(query)
                row = cursor.fetchone()
                return row

    @staticmethod
    def count_critical_missions():
        with connection.get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                query = """SELECT COUNT(*) AS 'critical_tasks' FROM missions 
                WHERE risk_level = "CRITICAL"
                """
                cursor.execute(query)
                row = cursor.fetchone()
                return row

    @staticmethod
    def get_top_agent():
        with connection.get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                query = """
                SELECT * FROM agents ORDER BY completed_missions DESC LIMIT 1 """
                cursor.execute(query)
                top_agent = cursor.fetchone()
                if not top_agent:
                    return None
                return {
                    "agent_id": top_agent["id"],
                    "completed_missions": top_agent["completed_missions"],
                }
