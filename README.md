
# College Management System

This project is a **College Management System** built using **FastAPI**. It includes several services and repositories integrated with technologies such as **Kafka**, **MongoDB**, **Neo4j**, **Redis**, **Solr**, **Cassandra**, and **Docker**.

## Prerequisites

Before running the project, make sure you have the following installed:

- Python 3.x
- Docker
- Docker Compose (Optional, but useful for managing the Docker containers)
- `uvicorn` (for running the FastAPI application)

### Steps to Set Up and Run the Project

### 1. Clone the repository
First, clone the repository to your local machine:
```bash
git clone https://github.com/Big-Chill/College-Management-System.git
cd College-Management-System
```

### 2. Set up the virtual environment

It is recommended to use a virtual environment to manage dependencies. Follow these steps to set it up:

#### For Windows:
```bash
python -m venv venv
.\env\Scripts\ctivate
```

#### For macOS/Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install the required dependencies

Once your virtual environment is activated, install the required dependencies by running:
```bash
pip install -r requirements.txt
```

### 4. Set up Docker containers

This project requires several Docker images to be pulled and run locally. These containers are essential for running the services like Kafka, MongoDB, Neo4j, Redis, etc.

You need to pull the Docker images and start the containers:

```bash
docker pull confluentinc/cp-kafka:latest
docker pull confluentinc/cp-zookeeper:latest
docker pull neo4j:latest
docker pull mongo:latest
docker pull cassandra:latest
docker pull redis:latest
docker pull solr:latest
```

### 5. Run Docker containers

Start the containers with the following commands (make sure Docker is running):

```bash
docker run -d --name wantednote-mongo -p 27017:27017 mongo:latest
docker run -d --name wantednote-kafka -p 9092:9092 confluentinc/cp-kafka:latest
docker run -d --name wantednote-zookeeper -p 2181:2181 -p 2888:2888 -p 3888:3888 confluentinc/cp-zookeeper:latest
docker run -d --name wantednote-neo4j -p 7474:7474 -p 7687:7687 neo4j:latest
docker run -d --name wantedmote-solr -p 8983:8983 solr:latest
docker run -d --name wantednote-redis -p 6379:6379 redis:latest
docker run -d --name wantednote-cassandra -p 9042:9042 cassandra:latest
```

### 6. Run the FastAPI application

Once the virtual environment is set up and Docker containers are running, you can start the FastAPI application using `uvicorn`. Run the following command to start the application:

```bash
uvicorn main:app --reload
```

This will start the FastAPI app in development mode with hot-reloading enabled.

### 7. Access the application

Once the server is running, you can access the application at:

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc API Docs**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

### Docker Container Overview

Here is a list of the Docker containers required to run the project:

| Container Name          | Image                              | Ports                            |
|-------------------------|------------------------------------|----------------------------------|
| `wantednote-mongo`       | `mongo:latest`                     | `0.0.0.0:27017->27017/tcp`      |
| `wantednote-kafka`       | `confluentinc/cp-kafka:latest`     | `0.0.0.0:9092->9092/tcp`        |
| `wantednote-zookeeper`   | `confluentinc/cp-zookeeper:latest` | `0.0.0.0:2181->2181/tcp`        |
| `wantednote-neo4j`       | `neo4j:latest`                     | `0.0.0.0:7474->7474/tcp`        |
| `wantedmote-solr`        | `solr:latest`                      | `0.0.0.0:8983->8983/tcp`        |
| `wantednote-redis`       | `redis:latest`                     | `0.0.0.0:6379->6379/tcp`        |
| `wantednote-cassandra`   | `cassandra:latest`                 | `0.0.0.0:9042->9042/tcp`        |

### Notes:

- If any of the Docker containers fail to start, please check the logs using `docker logs <container-name>`.
- You may need to adjust some of the configurations based on your local environment, especially for connecting to Kafka, Redis, and other services.
