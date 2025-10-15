# Project Overview

This project is a Python-based web service for downloading YouTube videos. It is built with FastAPI and uses MongoDB to store download requests and `yt-dlp` to handle the video downloads. The application is designed to be run in a Docker environment and includes a main web server, a download worker, a MinIO S3-compatible object storage, and a MongoDB database.

The application exposes a RESTful API for creating, reading, and deleting download requests. When a new download request is created, it is saved to the MongoDB database with a `REGISTERED` status. A separate download worker process listens for new download requests using MongoDB change streams. When a new request is detected, the worker downloads the video, updates the status of the request in the database, and stores the video in a local `downloads` directory, which is intended to be mounted to a MinIO S3-compatible object storage.

## Key Technologies

*   **Backend:** Python, FastAPI, Uvicorn
*   **Database:** MongoDB with Beanie ODM
*   **Video Downloading:** yt-dlp
*   **Object Storage:** MinIO (S3-compatible)
*   **Containerization:** Docker

## Architecture

The application is composed of four main components:

1.  **FastAPI Web Server:** Exposes a RESTful API for managing download requests.
2.  **Download Worker:** A separate process that listens for new download requests and handles the video downloading.
3.  **MongoDB:** A NoSQL database used to store download requests and video metadata.
4.  **MinIO:** An S3-compatible object storage used to store the downloaded videos.

The web server and the download worker are decoupled through the MongoDB database. The web server simply creates a new download request in the database, and the download worker picks it up asynchronously. This allows for a scalable and resilient architecture.

# Building and Running

The project is designed to be run with Docker and Docker Compose.

1.  **Environment Variables:**
    *   Create a `.env` file from the `.env.example` file and fill in the required environment variables.

2.  **Build and Run:**
    *   To build and run the application, use the following command:
        ```bash
        docker-compose up --build
        ```

3.  **API Access:**
    *   The API will be available at `http://localhost:8000`.

4.  **MinIO Console:**
    *   The MinIO console will be available at `http://localhost:9001`.

# Development Conventions

*   **Code Style:** The project follows the PEP 8 style guide for Python code.
*   **Typing:** The project uses type hints for all function signatures and variables.
*   **API Documentation:** The API is documented using the OpenAPI standard, and the documentation is available at `http://localhost:8000/docs`.
*   **Testing:** Tests are written using the `pytest` framework and are located in the same folder as the file being tested.