from typing import List

from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from . import crud, models, schemas, services
from .database import engine


def create_database():
    return models.Base.metadata.create_all(bind=engine)


app = FastAPI()


@app.post("/users")
def create_user(user: schemas.UserCreate, db: Session = Depends(services.get_db)):
    db_user = crud.get_user_by_email(user.email, db)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    new_user = crud.create_user(user, db)
    return services.create_token(new_user)


@app.post("/token")
def generate_token(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: Session = Depends(services.get_db),
):
    user = services.authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid login or password")
    return services.create_token(user)


@app.get("/users/me", response_model=schemas.User)
def read_user(user: schemas.User = Depends(crud.get_current_user)):
    return user


@app.post("/notes", response_model=schemas.Note)
def create_note_for_user(
    note: schemas.NoteCreate,
    user: schemas.User = Depends(crud.get_current_user),
    db: Session = Depends(services.get_db)
):
    return crud.create_user_note(user=user, db=db, note=note)


@app.get("/notes", response_model=List[schemas.Note])
def read_notes(
        user: schemas.User = Depends(crud.get_current_user),
        db: Session = Depends(services.get_db)):
    return crud.get_notes(user=user, db=db)


@app.get("/notes/{note_id}", status_code=200)
def read_note(
        note_id: int,
        user: schemas.User = Depends(crud.get_current_user),
        db: Session = Depends(services.get_db)
):
    return crud.get_note(note_id, user, db)


@app.put("/notes/{note_id}", status_code=200)
def update_note_for_user(
    note_id: int,
    note: schemas.NoteCreate,
    user: schemas.User = Depends(crud.get_current_user),
    db: Session = Depends(services.get_db)
):
    crud.update_user_note(note_id, note, user, db)
    return {"message": "Successfully updated"}


@app.delete("/notes/{note_id}")
def delete_note_for_user(
    note_id: int,
    user: schemas.User = Depends(crud.get_current_user),
    db: Session = Depends(services.get_db)
):

    return crud.delete_user_note(note_id, user, db)
