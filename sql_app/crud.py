from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException
from jose import jwt
from passlib import hash

from . import models, schemas, services


def get_user_by_email(email: str, db: Session):
    return db.query(models.User).filter(models.User.email == email).first()


def create_user(user: schemas.UserCreate, db: Session):
    user_obj = models.User(
        email=user.email, hashed_password=hash.bcrypt.hash(user.password)
    )
    db.add(user_obj)
    db.commit()
    db.refresh(user_obj)
    return user_obj


def get_current_user(
        db: Session = Depends(services.get_db),
        token: str = Depends(services.oauth2schema)
):
    try:
        payload = jwt.decode(token, services.JWT_SECRET, algorithms=["HS256"])
        user = db.query(models.User).get(payload["id"])
    except:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return user


def get_notes(user: schemas.User, db: Session):
    notes = db.query(models.Note).filter_by(owner_id=user.id)
    return list(map(schemas.Note.from_orm, notes))


def _note_selector(note_id: int, user: schemas.User, db: Session):
    note = (
        db.query(models.Note)
        .filter_by(owner_id=user.id)
        .filter(models.Note.id == note_id)
        .first()
    )
    if note is None:
        raise HTTPException(status_code=404, detail="Note does not exist")
    return note


def get_note(note_id: int, user: schemas.User, db: Session):
    note = _note_selector(note_id=note_id, user=user, db=db)
    return schemas.Note.from_orm(note)


def create_user_note(user: schemas.User, db: Session, note: schemas.NoteCreate):
    db_note = models.Note(**note.dict(), owner_id=user.id)
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return schemas.Note.from_orm(db_note)


def update_user_note(note_id: int, note: schemas.NoteCreate, user: schemas.User, db: Session):
    current_note = _note_selector(note_id, user, db)
    current_note.title = note.title
    current_note.description = note.description
    current_note.completion = note.completion

    db.commit()
    db.refresh(current_note)
    return schemas.Note.from_orm(current_note)


def delete_user_note(note_id: int, user: schemas.User, db: Session):
    current_note = _note_selector(note_id, user, db)
    db.delete(current_note)
    db.commit()
    return {"message": "Note successfully deleted"}

