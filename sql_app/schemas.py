from typing import List, Optional
from pydantic import BaseModel


class NoteBase(BaseModel):
    title: str
    description: Optional[str] = None
    completion: Optional[bool] = False


class NoteCreate(NoteBase):
    pass


class Note(NoteBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    password: str

    class Config:
        orm_mode = True


class User(UserBase):
    id: int
    notes: List[Note] = []

    class Config:
        orm_mode = True
