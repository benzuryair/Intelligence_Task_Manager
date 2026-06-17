# Project Intelligence Task_Manager  


## System description
This system will manage tasks and agents with the options to add agents and add tasks and associate tasks to agents and update tasks on their status.  

## Folder structure

intelligence-task-manager/ 
│  
├── database/  
│   ├── db_connection.py  
│   ├── agent_db.py  
│   │── mission_db.py     
├── README.md  
├── requirements.txt  
└── .gitignore


## Table structure

### Agents table  

|field | type| Notes| 
| :----- | ----------| -------| 
id | INT PRIMARY KEY AUTO_INCOMANT  | Unique identifier
name | VARCHAR(50) | Agent name NOT NULL
specialty | VARCHAR(50)  | Field of specialization NOT NULL
is_active | BOOLEAN | DEFAULT TRUE NOT NULL
completed_missions | INT | DEFAULT 0 NOT NULL
agent_rank |  ENUM/ VARCHAR | Junior / Senior / Commander only NOT NULL


### Mission table

|field | type| Notes| 
| :----- | ----------| -------| 
id | INT PRIMARY KEY AUTO_INCOMANT  | Unique identifier
title | VARCHAR(50) | Mission title NOT NULL
description | TEXT | Detailed description  NOT NULL
location | VARCHAR(50) | Mission location NOT NULL
difficulty | INT | 1–10 only NOT NULL
importance | INT | 1–10 only NOT NULL
status | VARCHAR(50) | DEFAULT NEW NOT NULL
risk_level | VARCHAR(50) | Automatically calculated — not coming from the user  
assigned_agent_id | INT | NULL until association


## Department structure

### db_connection class

This class holds 3 methods that connect to the image we created, create a database, and create tables.  

|method| role|
| :----- | ----------|
|get_connection() | connect to the image we created
|create_database() | create a database
|create_tables() | create tables

### AgentDB class

This department is responsible for all information and actions on agents.

|method| role|
| :----- | ----------|
|create_agent(data) | Creates a new agent and returns the agent object.
|get_all_agents() | Returns a list of all agents  
|get_agent_by_id(id) | Returns one agent by ID, or None  
update_agent(id, data) | UPDATE for the entire row (cannot change id)  
|deactivate_agent(id) | Sets agent inactive status  
|increment_completed(id) | Updates the number of tasks completed.  
|increment_failed(id) | Updates the number of failed tasks  
|get_agent_performance(id) | Returns a dictionary with these keys completed, failed, total, success_rate 
|count_active_agents()| Returns the number of active agents

### MissionDB class  
This department is responsible for the information and operations of the tasks.  
|method| role|
| :----- | ----------|
| create_mission(data) | Creates a new task and returns the entire object  
| get_all_missions() | Returns one task by ID, or None  
| assign_mission(m_id, a_id) | Assigning a task to an agent  
| update_mission_status(id, status) | Used for any status change  
|get_open_missions_by_agent(id) | Returns agent ASSIGNED/IN_PROGRESS tasks  
| count_all_missions() | Total tasks  
| count_by_status(status) | Counting by a certain status  
| count_open_missions() | Open task counter  
| count_critical_missions() | CRITICAL task counter  
| get_top_agent() | The agent with the highest completed_missions  

## System rules  
|num| law|
| :----- | ----------|
|1 | rank must be Junior / Senior / Commander — any other value throws an error.  
|2 | Difficulty and importance must be between 1 and 10 — otherwise an error.  
|3| risk_level is calculated automatically when a task is created—the user does not submit it.  
|4| An agent with is_active=False cannot accept tasks.  
|5| An agent cannot have more than 3 open tasks (ASSIGNED / IN_PROGRESS) at the same time.  
|6| If risk_level=CRITICAL — only an agent with the rank of Commander can accept the task.  
|7| If risk_level=CRITICAL — only an agent with the rank of Commander can accept the task.  
|8| Only a task with the status ASSIGNED can be started. After: status=IN_PROGRESS.  
|9| Only a task can be completed. IN_PROGRESS and changed to failed or completed status.  
|10| Only a task with a status of NEW or ASSIGNED can be canceled — otherwise an error. 


## Running instructions
Run this line in a command prompt  
```docker run -d --name intelligence-mysql -e MYSQL_ROOT_PASSWORD=1234 -e MYSQL_DATABASE=Intelligence_db -p 3306:3306 mysql:8.0```  

Run the following commands in the terminal inside the folder
 

- Python 3.13.14
- Docker
- python -m venv venv
- venv\Scripts\activate
- Fast API
- uvicorn
- mysql.connector
- pip install -r requirements.txt

And run the main.py file to initialize the database and its tables.
```py main.py```


