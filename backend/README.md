## MOVY Ticket Booking API setup

```markdown
# Movy Ticket Booking App

## Overview
Movy Ticket Booking App is a backend service for booking movie tickets. It is built with FastAPI and uses MySQL for the database and Redis for caching. The app is hosted on Koyeb cloud hosting platform.

## Prerequisites
- Python 3.8+
- MySQL
- Redis

## Setup

### Clone the Repository
```sh
git clone https://github.com/your-username/movy-ticket-booking-app.git
cd movy-ticket-booking-app
```

### Create and Activate Virtual Environment
```sh
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

### Install Dependencies
```sh
pip install -r requirements.txt
```

### Environment Variables
Create a `.env` file in the project root directory and add the following environment variables:

```env
# Test Environment Variables
TEST_USERNAME=your_test_username
TEST_DATABASE=your_test_database
TEST_PASSWORD=your_test_password
TEST_HOST=your_test_host
PORT=3306

# Production Database Variables
USERNAME=sql8721521
DATABASE=your_production_database
DATABASE_PASSWORD=your_database_password
DATABASE_HOST=your_database_host
TEST_DB=1

# TMDB API Key
TMDB_API_KEY=your_tmdb_api_key

# Redis Variables
REDIS_PASSWORD=your_redis_password
REDIS_HOST=your_redis_host
REDIS_PORT=your_redis_port
```

### Database Setup
Make sure your MySQL server is running and create the necessary databases for testing and production. You can use tools like `mysql` or any MySQL client.

### Run Migrations
Apply the database migrations to create the necessary tables:
```sh
alembic upgrade head
```

### Start the Application
```sh
uvicorn main:app --reload
```

The app should now be running on `http://127.0.0.1:8000`.

## Technologies Used
- FastAPI
- Python
- MySQL
- Redis
- Hosted on Koyeb cloud hosting platform

## Contributing
Feel free to open issues or submit pull requests for any enhancements or bug fixes.

Make sure to replace placeholders like `your_test_username`, `your_test_database`, etc., with actual values relevant to your setup. Also, update the repository URL and any other specific details to match your project.