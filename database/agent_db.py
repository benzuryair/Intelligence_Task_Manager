from database.db_connection import connection


class AgentDB:

    @staticmethod
    def get_all_agents():
        with connection.get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                query = """SELECT * FROM agents"""
                cursor.execute(query)
                rows = cursor.fetchall()
                return rows

    @staticmethod
    def get_agent_by_id(id: int):
        with connection.get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                query = """SELECT * from agents WHERE id =%s"""
                cursor.execute(query, (id,))
                row = cursor.fetchone()
                return row

    @staticmethod
    def create_agent(data: dict):
        with connection.get_connection() as conn:
            with conn.cursor() as cursor:
                query = "insert into agents(name, specialty, is_active, agent_rank) values(%s, %s, %s, %s)"
                values = list(data.values())
                cursor.execute(query, values)
                new_id = cursor.lastrowid
                conn.commit()
                agent = AgentDB.get_agent_by_id(new_id)
                return agent

    @staticmethod
    def update_agent(id: int, data: dict):
        with connection.get_connection() as conn:
            with conn.cursor() as cursor:
                list_of_keys = [f"{col}=%s" for col in data]
                sorted_keys = ", ".join(list_of_keys)
                query = f"""UPDATE agents SET {sorted_keys} WHERE id = %s"""
                values = list(data.values()) + [id]
                cursor.execute(query, values)
                changed = cursor.rowcount > 0
                conn.commit()
                return changed

    @staticmethod
    def deactivate_agent(id: int):
        with connection.get_connection() as conn:
            with conn.cursor() as cursor:
                query = """UPDATE agents SET is_active = False WHERE id = %s"""
                cursor.execute(query, (id,))
                changed = cursor.rowcount > 0
                conn.commit()
                return changed

    @staticmethod
    def increment_completed(id: int):
        with connection.get_connection() as conn:
            with conn.cursor() as cursor:
                query = """UPDATE agents SET completed_missions = completed_missions + 1 WHERE id = %s"""
                cursor.execute(query, (id,))
                changed = cursor.rowcount > 0
                conn.commit()
                return changed

    @staticmethod
    def increment_failed(id: int):
        with connection.get_connection() as conn:
            with conn.cursor() as cursor:
                query = """UPDATE agents SET failed_missions = failed_missions + 1 WHERE id = %s"""
                cursor.execute(query, (id,))
                changed = cursor.rowcount > 0
                conn.commit()
                return changed

    @staticmethod
    def get_agent_performance(id: int):
        agent = AgentDB.get_agent_by_id(id)
        completed = agent["completed_missions"]
        failed = agent["failed_missions"]
        total = completed + failed
        success_rate = (completed / total) * 100
        summary_dict = {
            "completed": completed,
            "failed": failed,
            "total": total,
            "success_rate": round(success_rate, 2),
        }
        return summary_dict

    @staticmethod
    def count_active_agents():
        with connection.get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                query = """SELECT COUNT(is_active) AS active_agents FROM agents WHERE is_active = True"""
                cursor.execute(query)
                active_agents = cursor.fetchone()
                return active_agents
