from sqlalchemy.orm import Session
from models import Contact, User
from schemas import ContactCreate, ContactUpdate
from passlib.context import CryptContext

from fastapi import HTTPException


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_contact(db: Session, contact: ContactCreate, user_id: int):
    db_contact = Contact(**contact.dict(), user_id=user_id)
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact

def create_user(db: Session, email: str, password: str):
    hashed_password = pwd_context.hash(password)
    db_user = db.query(User).filter(User.email == email).first()
    if db_user:
        raise HTTPException(status_code=409, detail="Email already registered")
    new_user = User(email=email, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_contact(db: Session, contact_id: int, user_id: int):
    return db.query(Contact).filter(Contact.id == contact_id, Contact.user_id == user_id).first()

def get_contacts(db: Session, user_id: int, skip: int = 0, limit: int = 10):
    return db.query(Contact).filter(Contact.user_id == user_id).offset(skip).limit(limit).all()

def update_contact(db: Session, contact_id: int, contact: ContactUpdate, user_id: int):
    db_contact = get_contact(db, contact_id, user_id)
    if db_contact is None:
        return None
    for key, value in contact.dict(exclude_unset=True).items():
        setattr(db_contact, key, value)
    db.commit()
    db.refresh(db_contact)
    return db_contact

def delete_contact(db: Session, contact_id: int, user_id: int):
    db_contact = get_contact(db, contact_id, user_id)
    if db_contact:
        db.delete(db_contact)
        db.commit()
    return db_contact
