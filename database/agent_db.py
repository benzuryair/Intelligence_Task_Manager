from database.db_connection import DBConnection
import logging


class AgentDB:

    @staticmethod
    def get_all_agents():
        with DBConnection.get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                query = """SELECT * FROM agents"""
                logging.info("SQL query to return all agents in the list")
                cursor.execute(query)
                rows = cursor.fetchall()
                return rows

    @staticmethod
    def get_agent_by_id(id: int):
        with DBConnection.get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                query = """SELECT * from agents WHERE id =%s"""
                logging.info("SQL query to return agent by ID")
                cursor.execute(query, (id,))
                row = cursor.fetchone()
                return row

    @staticmethod
    def create_agent(data: dict):
        with DBConnection.get_connection() as conn:
            with conn.cursor() as cursor:
                if "id" in data:
                    data.pop("id")
                if not data:
                    return False
                query = "INSERT INTO agents(name, specialty, is_active, agent_rank) VALUES (%s, %s, %s, %s)"
                values = [
                    data["name"],
                    data["specialty"],
                    data.get("is_active", True),
                    data["agent_rank"],
                ]
                logging.info("SQL query to create a new agent")
                cursor.execute(query, values)
                new_id = cursor.lastrowid
                conn.commit()
                agent = AgentDB.get_agent_by_id(new_id)
                return agent

    @staticmethod
    def update_agent(id: int, data: dict):
        with DBConnection.get_connection() as conn:
            with conn.cursor() as cursor:
                list_of_keys = [f"{col}=%s" for col in data]
                sorted_keys = ", ".join(list_of_keys)
                query = f"""UPDATE agents SET {sorted_keys} WHERE id = %s"""
                values = list(data.values()) + [id]
                logging.info("SQL query to update agent by ID")
                cursor.execute(query, values)
                changed = cursor.rowcount > 0
                conn.commit()
                return changed

    @staticmethod
    def deactivate_agent(id: int):
        with DBConnection.get_connection() as conn:
            with conn.cursor() as cursor:
                query = """UPDATE agents SET is_active = False WHERE id = %s"""
                logging.info("SQL query to deactivate an agent")
                cursor.execute(query, (id,))
                changed = cursor.rowcount > 0
                conn.commit()
                return changed

    @staticmethod
    def increment_completed(id: int):
        with DBConnection.get_connection() as conn:
            with conn.cursor() as cursor:
                query = """UPDATE agents SET completed_missions = completed_missions + 1 WHERE id = %s"""
                logging.info(
                    "SQL query to update the counter of tasks that the agent successfully completed"
                )
                cursor.execute(query, (id,))
                changed = cursor.rowcount > 0
                conn.commit()
                return changed

    @staticmethod
    def increment_failed(id: int):
        with DBConnection.get_connection() as conn:
            with conn.cursor() as cursor:
                query = """UPDATE agents SET failed_missions = failed_missions + 1 WHERE id = %s"""
                logging.info(
                    "SQL query to update the counter of tasks that the agent failed"
                )
                cursor.execute(query, (id,))
                changed = cursor.rowcount > 0
                conn.commit()
                return changed

    @staticmethod
    def get_agent_performance(id: int):
        agent = AgentDB.get_agent_by_id(id)
        if not agent:
            return False
        completed = agent["completed_missions"]
        failed = agent["failed_missions"]
        total = completed + failed
        all_agent_tasks = AgentDB.count_total_missions_by_id(id)
        all_inclusive = all_agent_tasks["COUNT"]
        if total > 0:
            success_rate = (completed / total) * 100
        else:
            success_rate = 0.0
        summary_dict = {
            "completed": completed,
            "failed": failed,
            "total": all_inclusive,
            "success_rate": round(success_rate, 2),
        }
        return summary_dict

    @staticmethod
    def count_active_agents():
        with DBConnection.get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                query = """SELECT COUNT(is_active) AS active_agents FROM agents WHERE is_active = True"""
                logging.info("SQL query to count how many active agents there are?")
                cursor.execute(query)
                active_agents = cursor.fetchone()
                return active_agents

    @staticmethod
    def count_total_missions_by_id(id: int):
        with DBConnection.get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                query = """SELECT COUNT(*) as COUNT
                FROM missions
                where assigned_agent_id = %s"""
                cursor.execute(query, (id,))
                row = cursor.fetchone()
                return row
