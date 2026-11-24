from sqlalchemy import text
from src.database.database import engine

with engine.connect() as connection:
    print(
        connection.execute(
            text("SELECT current_database()")
        ).scalar()
    )

    print(
        connection.execute(
            text("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
            """)
        ).scalars().all()
    )