from typing import List

from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

import sql_app.crud as _crud
import sql_app.schemas as _schemas
import sql_app.services as _services
import sql_app.database as _database


def create_database():
    return _database.Base.metadata.create_all(bind=_database.engine)


app = FastAPI()


@app.post("/users")
def create_user(user: _schemas.UserCreate, db: Session = Depends(_services.get_db)):
    db_user = _crud.get_user_by_email(user.email, db)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    new_user = _crud.create_user(user, db)
    return _services.create_token(new_user)


@app.post("/token")
def generate_token(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: Session = Depends(_services.get_db),
):
    user = _services.authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid login or password")
    return _services.create_token(user)


@app.get("/users/me", response_model=_schemas.User)
def read_user(user: _schemas.User = Depends(_crud.get_current_user)):
    return user


@app.post("/notes", response_model=_schemas.Note)
def create_note_for_user(
    note: _schemas.NoteCreate,
    user: _schemas.User = Depends(_crud.get_current_user),
    db: Session = Depends(_services.get_db)
):
    return _crud.create_user_note(user=user, db=db, note=note)


@app.get("/notes", response_model=List[_schemas.Note])
def read_notes(
        user: _schemas.User = Depends(_crud.get_current_user),
        db: Session = Depends(_services.get_db)):
    return _crud.get_notes(user=user, db=db)


@app.get("/notes/{note_id}", status_code=200)
def read_note(
        note_id: int,
        user: _schemas.User = Depends(_crud.get_current_user),
        db: Session = Depends(_services.get_db)
):
    return _crud.get_note(note_id, user, db)


@app.put("/notes/{note_id}", status_code=200)
def update_note_for_user(
    note_id: int,
    note: _schemas.NoteCreate,
    user: _schemas.User = Depends(_crud.get_current_user),
    db: Session = Depends(_services.get_db)
):
    _crud.update_user_note(note_id, note, user, db)
    return {"message": "Successfully updated"}


@app.delete("/notes/{note_id}")
def delete_note_for_user(
    note_id: int,
    user: _schemas.User = Depends(_crud.get_current_user),
    db: Session = Depends(_services.get_db)
):

    return _crud.delete_user_note(note_id, user, db)
