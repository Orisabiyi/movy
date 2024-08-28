# Movy Booking Application

Movy is an online movie booking platform that allows users to browse movies, book tickets, and reserve seats at their favorite theaters. The application integrates various technologies and services to provide a seamless booking experience.

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Frontend](#frontend)
- [Backend](#backend)
- [Database](#database)
- [Third-Party Integrations](#third-party-integrations)
- [Endpoints](#endpoints)
- [Setup](#setup)
- [Challenges and Learnings](#challenges-and-learnings)
- [Contributing](#contributing)
- [License](#license)

## Features

- **User Authentication**: Secure user registration and login using Google OAuth for social login.
- **Movie Browsing**: Theaters can add movies they want to stream using data from The Movie DB (TMDb).
- **Booking and Reservation**: Users can book and cancel tickets, and reserve specific seats in theaters.
- **Payment Integration**: Secure payment processing through Paystack.
- **Real-time Data**: Utilizes Redis for caching and real-time data processing.
- **Theater Management**: Theaters can manage their movie listings and available showtimes.

## Architecture

The Movy application is designed with a microservices architecture, splitting responsibilities between the frontend and backend services.

- **Frontend**: Developed with HTML, CSS, JavaScript, and ReactJS. The frontend application is hosted on [Vercel](https://vercel.com).
- **Backend**: Built using Python with the FastAPI framework. It manages business logic, database interactions, and third-party integrations. The backend services are hosted on [Koyeb](https://koyeb.com).
- **Database**: The application uses MySQL for relational data storage and Redis for caching.
- **Third-Party Services**: Paystack for payment processing and Google OAuth for social authentication.

## Frontend

The frontend of Movy is responsible for providing an intuitive and responsive user interface. Key technologies and features include:

- **ReactJS**: A JavaScript library for building user interfaces.
- **CSS and HTML**: For styling and structuring the web pages.
- **JavaScript**: For adding interactivity and handling frontend logic.
- **Vercel Hosting**: The frontend is deployed on Vercel, ensuring high availability and scalability.

## Backend

The backend of Movy handles the core business logic, API management, and third-party service integrations. Key technologies and components include:

- **FastAPI**: A modern Python web framework for building APIs.
- **MySQL**: A relational database for storing user, booking, and movie data.
- **Redis**: Used for caching and real-time data processing.
- **Koyeb Hosting**: The backend services are deployed on Koyeb, providing a reliable and scalable infrastructure.

### Key Backend Endpoints

- **User Management**: 
  - `/auth/user/signup` - Register a new user
  - `/auth/user/login` - User login
  - `/auth/google` - Google OAuth for social login

- **Movie Management**: 
  - `/theatre/{theatre_id}/add-movie` - Theatres can add movies they want to stream
  - `/movies` - List all available movies

- **Booking and Reservation**:
  - `/booking/{showtime_id}` - Book a ticket for a movie
  - `/cancel-booking/{booking_id}` - Cancel a booking
  - `/booking` - Reserve a specific seat

- **Payment Processing**:
  - `/booking/pay` - Process payment via Paystack
  - `/verify-payment` - Verify user payment after transaction

## Database

Movy utilizes MySQL for its primary relational database, storing user information, booking details, movie data, and theater configurations. Redis is used for caching and handling real-time data updates.

### Key Database Tables

- **Users**: Stores user information and authentication details.
- **Movies**: Stores movie data, including titles, descriptions, and showtimes.
- **Theatres**: Stores information about theaters, including available screens and seating arrangements.
- **Bookings**: Stores booking details, including user reservations and payment status.
- **Seats**: Manages seat reservations, ensuring that users can reserve specific seats in a theater.
- **ShowTime**: Manages movie show time for the theatre
- **Seat**: Stores theatre seating arrangement
- **Screen**: Manages how theatre stream movies

## Third-Party Integrations

- **Paystack**: Used for processing secure payments. The integration allows users to pay for their bookings directly through the application.
- **Google OAuth**: Enables users to log in with their Google accounts, simplifying the authentication process.
- **The Movie DB (TMDb)**: Provides movie data that theaters can use to add movies to their streaming list.

