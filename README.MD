# E-Commerce Auth API (FastAPI + PostgreSQL + JWT + MiddleWare)

A secure authentication system for an E-Commerce platform built with **FastAPI**, **PostgreSQL**, and **JWT**, **middleware**.

# Features

-  JWT Authentication (Login/Register)
-  Rate Limiting Middleware (60 req/min per IP)
-  PostgreSQL with SQLAlchemy ORM
-  Alembic for Database Migrations
-  CORS Configuration
-  .env Support for Secrets
-   Security Headers
-   Streamlit UI integration (Frontend)

# Tools & Tech Stack

- FastAPI
- SQLAlchemy
- PostgreSQL
- Pydantic
- JWT (python-jose)
- Passlib (bcrypt)
- Streamlit (optional UI)
- alembic
- python-dotenv

# security

- Passwords are hashed using bcrypt
- JWT is used for sessionless authentication
- All secret keys and DB URLs are stored in .env
