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
                SELECT extname
                FROM pg_extension
                WHERE extname = 'vector'
            """)
        ).all()
    )