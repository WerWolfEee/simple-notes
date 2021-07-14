from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from .database import SessionLocal
from . import crud, models, schemas
import jwt

oauth2schema = OAuth2PasswordBearer(tokenUrl="/token")

JWT_SECRET = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def authenticate_user(email: str, password: str, db: Session):
    user = crud.get_user_by_email(db=db, email=email)
    if not user:
        return False
    if not user.verify_password(password):
        return False
    return user


def create_token(user: models.User):
    user_obj = schemas.User.from_orm(user)
    token = jwt.encode(user_obj.dict(), JWT_SECRET)
    return dict(access_token=token, token_type="bearer")
