from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# for using a SQLite database uncomment the line:
# SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"

# for using a PostgreSQL database uncomment the line:
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:pOSTgRE@localhost:5432/postgre_sql_app"

# for using a SQLite database uncomment the line:
# engine = create_engine(
#     SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
# )

# for using a PostgreSQL database uncomment the line:
engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
