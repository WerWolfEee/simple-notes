from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

import sql_app.database as _database
import sql_app.crud as _crud
import sql_app.models as _models
import sql_app.schemas as _schemas
import jwt

oauth2schema = OAuth2PasswordBearer(tokenUrl="/token")

JWT_SECRET = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"


def get_db():
    db = _database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


def authenticate_user(email: str, password: str, db: Session):
    user = _crud.get_user_by_email(db=db, email=email)
    if not user:
        return False
    if not user.verify_password(password):
        return False
    return user


def create_token(user: _models.User):
    user_obj = _schemas.User.from_orm(user)
    token = jwt.encode(user_obj.dict(), JWT_SECRET)
    return dict(access_token=token, token_type="bearer")
