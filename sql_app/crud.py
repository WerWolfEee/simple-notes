from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException
# from jose import jwt
from passlib import hash
import jwt

import sql_app.models as _models
import sql_app.schemas as _schemas
import sql_app.services as _services


def get_user_by_email(email: str, db: Session):
    return db.query(_models.User).filter(_models.User.email == email).first()


def create_user(user: _schemas.UserCreate, db: Session):
    user_obj = _models.User(
        email=user.email, hashed_password=hash.bcrypt.hash(user.password)
    )
    db.add(user_obj)
    db.commit()
    db.refresh(user_obj)
    return user_obj


def get_current_user(
        db: Session = Depends(_services.get_db),
        token: str = Depends(_services.oauth2schema)
):
    try:
        payload = jwt.decode(token, _services.JWT_SECRET, algorithms=["HS256"])
        user = db.query(_models.User).get(payload["id"])
    except:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return user


def get_notes(user: _schemas.User, db: Session):
    notes = db.query(_models.Note).filter_by(owner_id=user.id)
    return list(map(_schemas.Note.from_orm, notes))


def _note_selector(note_id: int, user: _schemas.User, db: Session):
    note = (
        db.query(_models.Note)
        .filter_by(owner_id=user.id)
        .filter(_models.Note.id == note_id)
        .first()
    )
    if note is None:
        raise HTTPException(status_code=404, detail="Note does not exist")
    return note


def get_note(note_id: int, user: _schemas.User, db: Session):
    note = _note_selector(note_id=note_id, user=user, db=db)
    return _schemas.Note.from_orm(note)


def create_user_note(user: _schemas.User, db: Session, note: _schemas.NoteCreate):
    db_note = _models.Note(**note.dict(), owner_id=user.id)
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return _schemas.Note.from_orm(db_note)


def update_user_note(note_id: int, note: _schemas.NoteCreate, user: _schemas.User, db: Session):
    current_note = _note_selector(note_id, user, db)
    current_note.title = note.title
    current_note.description = note.description
    current_note.completion = note.completion

    db.commit()
    db.refresh(current_note)
    return _schemas.Note.from_orm(current_note)


def delete_user_note(note_id: int, user: _schemas.User, db: Session):
    current_note = _note_selector(note_id, user, db)
    db.delete(current_note)
    db.commit()
    return {"message": "Note successfully deleted"}
