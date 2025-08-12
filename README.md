# EastVantage Address Book API

A FastAPI-based address book application with geolocation and robust validation, designed for concurrency safety and clean code structure.

## Table of Contents
- [Features](#features)
- [Setup Instructions](#setup-instructions)
- [Project Structure & Python File Roles](#project-structure--python-file-roles)
- [API Endpoints](#api-endpoints)
- [Notes](#notes)

## Features
- Create, update, delete, and fetch address book entries
- Geolocation-based nearby search using the Haversine formula
- Input validation with Pydantic (regex, min/max length, required fields)
- Concurrency-safe create, update, and delete operations
- Logging and error handling

## Setup Instructions

1. **Clone the Repository**
   ```sh
   git clone https://github.com/jerrypunzalan24/eastvantage-api
   cd eastvantage-api
   ```

2. **Create and Activate a Virtual Environment (Windows)**
   ```sh
   py -m venv eastvantage_venv
   ./eastvantage_venv/Scripts/activate
   ```
- or you can use 
  ```sh
    cd eastvantage_venv/Scripts/
    activate.bat
  ```

3. **Install Dependencies**
   ```sh
   pip install -r requirements.txt
   ```

4 **Configure with .env file**
- You can access this page https://developers.google.com/maps/get-started#api-key on how to get your api key to be able to use geolocation services
- Create and edit `.env` with the following configuration
```
    HOST=0.0.0.0
    PORT=8000
    DATABASE_URL=sqlite:///./test123.db
    TIMEZONE=Asia/Manila
    GOOGLE_MAPS_API_KEY=<YOUR_API_KEY>
```

5. **Run the Application**
   ```sh
    py main.py 
   ```
   The API will be available at `http://localhost:<PORT>`.
   Swagger API docs can be found here: `http://localhost:<PORT>/docs` 
## Project Structure & Python File Roles

- **main.py**
  - Entry point for the FastAPI app
  - Defines all API endpoints (CRUD, nearby search)
  - Handles request validation, logging, and error responses
  - Ensures concurrency safety for create, update, and delete operations

- **models.py**
  - SQLAlchemy ORM models: `Person`, `AddressBook`
  - Pydantic models for request/response validation
  - Database engine and session setup
  - `get_db` dependency for database access

- **services.py**
  - Business logic, e.g., `GeolocationService` for geocoding and distance calculations
  - Implements the Haversine formula for nearby search

- **settings.py**
  - Application and environment configuration (e.g., database URL, host, port)
  - `EnvSettings` and `AppSettings` classes

- **logger.py**
  - Configures and provides a logger for the application
  - Used throughout the app for info and error logging

## API Endpoints
- `GET /` — Welcome route
- `GET /all_address` — List all address book entries (paginated)
- `GET /get_address/{person_id}` — Get address by person ID
- `GET /nearby` — Find addresses near a given location
- `POST /create_address` — Create a new address/person
- `PUT /update_address/{person_id}` — Update an existing address/person
- `DELETE /delete_address/{person_id}` — Delete an address/person

## Notes
- You can modify the request time out and toggle refresh of the application in `settings.py`.
- All input is validated using Pydantic models.
- Logging is enabled for all major operations and errors.


