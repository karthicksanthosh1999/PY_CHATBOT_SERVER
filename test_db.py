from src.database.database import engine

try:
    with engine.connect() as connection:
        print("Database connected successfully!")

except Exception as error:
    print("Database connection failed:", error)