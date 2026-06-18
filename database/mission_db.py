from database.db_connection import DBConnection
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
        with DBConnection.get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                query = """SELECT * FROM missions"""
                cursor.execute(query)
                rows = cursor.fetchall()
                return rows

    @staticmethod
    def get_mission_by_id(id: int):
        with DBConnection.get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                query = """SELECT * from missions WHERE id =%s"""
                cursor.execute(query, (id,))
                row = cursor.fetchone()
                return row

    @staticmethod
    def create_mission(data: dict):
        with DBConnection.get_connection() as conn:
            with conn.cursor() as cursor:
                risk_level = risk_level_check(data["difficulty"], data["importance"])
                query = """insert into missions(title, description, location, difficulty, importance, risk_level) values(%s, %s, %s, %s, %s, %s)"""
                values = list(data.values()) + [risk_level]
                cursor.execute(query, values)
                new_id = cursor.lastrowid
                conn.commit()
                mission = MissionDB.get_mission_by_id(new_id)
                return mission

    @staticmethod
    def assign_mission(m_id: int, a_id: int):
        with DBConnection.get_connection() as conn:
            with conn.cursor() as cursor:
                query = """UPDATE missions SET status = 'ASSIGNED', assigned_agent_id = %s WHERE id = %s"""
                cursor.execute(query, (a_id, m_id))
                changed = cursor.rowcount > 0
                conn.commit()
                return changed

    @staticmethod
    def update_mission_status(id: int, status: str):
        with DBConnection.get_connection() as conn:
            with conn.cursor() as cursor:
                query = """UPDATE missions SET status = %s WHERE id = %s"""
                cursor.execute(query, (status, id))
                changed = cursor.rowcount > 0
                conn.commit()
                return changed

    @staticmethod
    def get_open_missions_by_agent(id: int):
        with DBConnection.get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                query = """SELECT * FROM missions
                WHERE (status = "ASSIGNED" or status = "IN_PROGRESS") and assigned_agent_id = %s"""
                cursor.execute(query, (id,))
                rows = cursor.fetchall()
                return rows

    @staticmethod
    def count_all_missions():
        with DBConnection.get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                query = """SELECT COUNT(*) as 'total_tasks' FROM missions"""
                cursor.execute(query)
                row = cursor.fetchone()
                return row

    @staticmethod
    def count_by_status(status: str):
        with DBConnection.get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                query = """SELECT status AS Status, COUNT(*) as COUNT
                FROM missions
                where status = %s"""
                cursor.execute(query, (status,))
                row = cursor.fetchone()
                return row

    @staticmethod
    def count_open_missions():
        with DBConnection.get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                query = """SELECT COUNT(*) AS 'open_tasks' FROM missions 
                WHERE status = "NEW" or status = "ASSIGNED" or status = "IN_PROGRESS"
                """
                cursor.execute(query)
                row = cursor.fetchone()
                return row

    @staticmethod
    def count_critical_missions():
        with DBConnection.get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                query = """SELECT COUNT(*) AS 'critical_tasks' FROM missions 
                WHERE risk_level = "CRITICAL"
                """
                cursor.execute(query)
                row = cursor.fetchone()
                return row

    @staticmethod
    def get_top_agent():
        with DBConnection.get_connection() as conn:
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
