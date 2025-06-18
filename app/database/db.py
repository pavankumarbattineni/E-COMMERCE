from app.database.session import SessionLocal

# dependency to get the database session

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
