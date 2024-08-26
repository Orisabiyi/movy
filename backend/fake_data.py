#!/usr/bin/env python3
import random
import uuid
from datetime import datetime, timedelta

from main.database import DB, get_db
from main.util_files import hash_password
from movies.models import Movie
from sqlalchemy import create_engine, exc
from theatre.models import ShowTime, Theatre
from theatre.theatre_management.models import Screen, Seat
from faker import Faker

# Setup your database connection
db = DB()
fake = Faker()

def generate_unique_screen_name(theatre_id, existing_names):
    # Define base names and letters
    base_names = ["screen", "Atlas", "Hall", "room"]
    letters = [chr(i) for i in range(ord("A"), ord("Z") + 1)]

    while True:
        name = f"{random.choice(base_names)} {random.choice(letters)}"
        unique_name = f"{name} {theatre_id}"
        if unique_name not in existing_names:
            existing_names.add(unique_name)
            return name

def create_theatres_and_associate_movies(session: DB):
    # Fetch 100 movies from the database (or however many are available)
    movies = session._session.query(Movie).limit(100).all()

    if not movies:
        print("No movies found in the database.")
        return

    # Create 50 theatres
    theatres = []
    for _ in range(50):
        theatre = Theatre(
            id=str(uuid.uuid4()),
            email=fake.company_email(),  # You can customize this
            name=fake.company(),
            password=hash_password("securepassword"),  # Replace with actual password handling
            description="Best theatre in the world",
            role="theatre",
            is_active=True,
            is_verified=True,
        )
        session._session.add(theatre)
        theatres.append(theatre)

    session._session.commit()  # Commit the theatres first to get their IDs

    # Now associate each theatre with random movies
    for theatre in theatres:
        existing_names = set()  # To keep track of existing screen names for the theatre

        # Select a random subset of movies for each theatre
        associated_movies = random.sample(movies, random.randint(1, 10))  # Associating between 1 to 10 movies

        for movie in associated_movies:
            # Create a screen for the theatre with a unique name
            screen_name = generate_unique_screen_name(theatre.id, existing_names)
            screen = Screen(
                screen_name=screen_name,
                capacity=random.randint(50, 300),
                theatre_id=theatre.id,
            )
            
            try:
                session._session.add(screen)
                session._session.commit()  # Commit to get the screen ID
            except exc.IntegrityError:
                session._session.rollback()  # Rollback in case of duplicate entry
                continue  # Skip to next iteration
            
            # Create a showtime for each movie
            showtime = ShowTime(
                start_movie_time=datetime.now().time(),
                expires_at=datetime.now() + timedelta(hours=3),
                date=datetime.now().date(),
                price=random.uniform(1000, 5000),  # Price range in Naira (₦1,000 to ₦5,000)
                movie_id=movie.id,
                screen_id=screen.id,
            )
            session._session.add(showtime)
            session._session.commit()  # Commit to get the showtime ID

            # Generate seats with rows labeled A-Z and random seat numbers
            rows = [chr(i) for i in range(ord("A"), ord("Z") + 1)]  # Generate row labels A-Z
            for row in random.sample(rows, min(len(rows), random.randint(5, 10))):  # Pick a random number of rows
                for seat_number in range(1, screen.capacity // len(rows) + 1):  # Distribute seats evenly across rows
                    seat = Seat(
                        screen_id=screen.id,
                        row=row,
                        seat_number=seat_number,
                        is_available=True,
                    )
                    session._session.add(seat)

    # Final commit to save everything
    session._session.commit()

if __name__ == "__main__":
    # Create a new session
    session = db
    try:
        create_theatres_and_associate_movies(session)
    finally:
        session._close
