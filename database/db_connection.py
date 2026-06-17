import mysql.connector


class connection:

    @staticmethod
    def get_connection():
        return mysql.connector.connect(
            host="localhost",
            port=3306,
            user="root",
            password="1234",
            database="intelligence-mysql",
        )
#
    @staticmethod
    def create_database():
        with connection.get_connection() as conn:
            with conn.cursor() as cursor:
                query = """CREATE DATABASE IF NOT EXISTS intelligence-mysql"""
                cursor.execute(query)
                conn.commit()

    @staticmethod
    def create_tables():
        with connection.get_connection() as conn:
            with conn.cursor() as cursor:

                agents_query = """CREATE TABLE IF NOT EXISTS agents(
                        id INT PRIMARY KEY AUTO_INCREMENT,
                        name VARCHAR(50) NOT NULL,
                        specialty VARCHAR(50) NOT NULL,
                        is_active INT DEFAULT 0 NOT NULL,
                        completed_missions INT DEFAULT 0 NOT NULL,
                        failed_missions INT DEFAULT 0 NOT NULL,
                        agent_rank ENUM('Junior', 'Senior', 'Commander')
                    )"""

                missions_query = """CREATE TABLE IF NOT EXISTS missions(
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    title VARCHAR(50) NOT NULL,
                    description TEXT NOT NULL,
                    location VARCHAR(50) NOT NULL,
                    difficulty INT NOT NULL,
                    importance INT NOT NULL,
                    status VARCHAR(50) DEFAULT "NEW",
                    risk_level VARCHAR(50) NOT NULL,
                    assigned_agent_id INT
                )"""
                cursor.execute(agents_query)
                cursor.execute(missions_query)
                conn.commit()
