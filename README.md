# Design Feature Extraction API

This project provides a FastAPI-based web service for extracting design features from web pages. It uses Redis Queue (RQ) for background task processing and Docker for containerization.

## Features

- **Crawl Web Pages**: Extract design features and metadata from web pages.
- **Background Task Processing**: Offload crawling tasks to a Redis-backed queue.
- **Dockerized Deployment**: Easily deployable using Docker and Docker Compose.
- **CI/CD Pipeline**: Automated deployment to EC2 using GitHub Actions.

## Project Structure

```
.
├── docker-compose.yaml       # Docker Compose configuration
├── Dockerfile                # Docker image definition
├── src/                      # Source code
│   ├── main.py               # FastAPI entry point
│   ├── task_queue.py         # Redis Queue setup
│   ├── api/                  # API endpoints
│   │   ├── color.py          # Color-related API
│   │   ├── crawl.py          # Crawl-related API
│   ├── services/             # Business logic
│   │   ├── color_service.py  # Color extraction logic
│   │   ├── crawler_service.py# Web crawling logic
│   ├── static/               # Static files
│       └── index.html        # Example static page
└── .github/workflows/cicd.yml# CI/CD pipeline
```

## Prerequisites

- Docker
- Docker Compose
- Redis

## Setup and Usage

### 1. Clone the Repository

```bash
git clone https://github.com/<your-repo>.git
cd <your-repo>
```

### 2. Start the Services

Use Docker Compose to build and start the services:

```bash
docker compose up --build
```

### 3. Access the API

The API will be available at `http://localhost:5000`. You can explore the API documentation at `http://localhost:5000/docs`.

### 4. Run Background Tasks

Ensure the RQ worker is running to process background tasks:

```bash
docker compose exec worker rq worker default
```

## CI/CD Pipeline

The project includes a GitHub Actions workflow for automated deployment to an EC2 instance. The deployment script:

1. Clones or pulls the latest code.
2. Builds and starts the Docker services.
3. Cleans up unused Docker images.

## Environment Variables

- `REDIS_HOST`: Hostname for the Redis server (default: `redis` in Docker Compose).

## License

This project is licensed under the MIT License. See the LICENSE file for details.
