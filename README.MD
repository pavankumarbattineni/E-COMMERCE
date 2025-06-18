# E-Commerce Auth API (FastAPI + PostgreSQL)

A secure authentication system for an E-Commerce platform built with **FastAPI**, **PostgreSQL**, and **JWT**.

# Features

- User Registration and Login
- JWT Authentication
- Password Hashing with `bcrypt`
- Role Support (`is_admin`)
- Secure Endpoints (`/me`)
- Modular structure with SQLAlchemy ORM
- Configurable via `.env`

# Tools & Tech Stack

- FastAPI
- SQLAlchemy
- PostgreSQL
- Pydantic
- JWT (python-jose)
- Passlib (bcrypt)
- Streamlit (optional UI)

# security

- Passwords are hashed using bcrypt
- JWT is used for sessionless authentication
- All secret keys and DB URLs are stored in .env
