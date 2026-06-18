import mysql.connector


class DBConnection:

    @staticmethod
    def get_connection():
        return mysql.connector.connect(
            host="localhost",
            port=3306,
            user="root",
            password="1234",
            database="Intelligence_db",
        )

    #
    @staticmethod
    def create_database():
        conn = mysql.connector.connect(
            host="localhost",
            port=3306,
            user="root",
            password="1234"
        )
        with conn.cursor() as cursor:
            query = """CREATE DATABASE IF NOT EXISTS Intelligence_db"""
            cursor.execute(query)
        conn.commit()
        conn.close()

    @staticmethod
    def create_tables():
        with DBConnection.get_connection() as conn:
            with conn.cursor() as cursor:

                agents_query = """CREATE TABLE IF NOT EXISTS agents(
                        id INT PRIMARY KEY AUTO_INCREMENT,
                        name VARCHAR(50) NOT NULL,
                        specialty VARCHAR(50) NOT NULL,
                        is_active BOOLEAN DEFAULT True NOT NULL,
                        completed_missions INT DEFAULT 0 NOT NULL,
                        failed_missions INT DEFAULT 0 NOT NULL,
                        agent_rank ENUM('Junior', 'Senior', 'Commander')
                    )"""

                missions_query = """CREATE TABLE IF NOT EXISTS missions(
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    title VARCHAR(50) NOT NULL,
                    description TEXT NOT NULL,
                    location VARCHAR(50) NOT NULL,
                    difficulty INT NOT NULL CHECK(difficulty >= 1 and difficulty <= 10),
                    importance INT NOT NULL CHECK(importance >= 1 and importance <= 10),
                    status VARCHAR(50) DEFAULT "NEW" NOT NULL,
                    risk_level VARCHAR(50) NOT NULL,
                    assigned_agent_id INT
                )"""
                cursor.execute(agents_query)
                cursor.execute(missions_query)
                conn.commit()