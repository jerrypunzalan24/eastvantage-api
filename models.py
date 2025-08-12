
from dataclasses import Field
from typing import Optional
from pydantic import BaseModel, Field
from sqlalchemy import DateTime, Float, ForeignKey, create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from settings import EnvSettings
from datetime import datetime,timezone
from zoneinfo import ZoneInfo

db_engine = create_engine(EnvSettings.DATABASE_URL, connect_args={"check_same_thread": False})
sessionmaker = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
Base = declarative_base()

# Define the desired timezone for datetime fields
desired_timezone = ZoneInfo(EnvSettings.TIMEZONE) if EnvSettings.TIMEZONE else timezone.utc

# Schema definitions for Person and AddressBook models
class Person(Base):
    __tablename__ = 'person'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    phone = Column(String, index=True)
    address = relationship("AddressBook", back_populates="person", uselist=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(desired_timezone))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(desired_timezone), onupdate=lambda: datetime.now(desired_timezone))

class AddressBook(Base):
    __tablename__ = 'address_book'
    id = Column(Integer, primary_key=True, index=True)
    person_id = Column(Integer, ForeignKey('person.id'))
    person = relationship("Person", back_populates="address")
    city = Column(String, index=True)
    country = Column(String, index=True)
    street = Column(String, index=True)
    postal = Column(String, index=True)
    latitude = Column(Float, index=True)
    longitude = Column(Float, index=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(desired_timezone))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(desired_timezone), onupdate=lambda: datetime.now(desired_timezone))

Base.metadata.create_all(bind=db_engine)

# Pydantic models for request and response validation that uses regular expressions minimum and maximum length constraints

class AddressBookCreate(BaseModel):
    city: str = Field(pattern=r"^(\w+[,.]?\s?)+$", min_length=1, max_length=100, default="Quezon City")
    country: str = Field(pattern=r"^[a-zA-Z\s]+$", min_length=1, max_length=100, default="Philippines")
    street: str = Field(pattern=r"^(\w+[,.]?\s?)+$", min_length=1, max_length=100, default="Narra street")
    postal: Optional[str] = Field(pattern=r"^$|\d{4,10}", min_length=0, max_length=10, default="12345")

class PersonCreate(BaseModel):
    name: str = Field(pattern=r"^[a-zA-Z\s]+$", min_length=1, max_length=100, default="John doe")
    email: str = Field(pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$", min_length=1, max_length=100, default="example@email.com")
    phone: str = Field(pattern=r"^(09|\+639)\d{9}$", min_length=1, max_length=15, default="09123456789")
    address: AddressBookCreate

class AddressBookOutput(BaseModel):
    id: int
    person_id: int
    city: str 
    country: str 
    street: str
    postal: str 
    latitude: float 
    longitude: float
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True

class PersonOutput(BaseModel):
    id: int
    name: str
    email: str
    phone: str
    address: AddressBookOutput
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class AddressBookUpdate(BaseModel):
    city: Optional[str] = Field(pattern=r"^(\w+[,.]?\s?)+$", min_length=1, max_length=100, default="Quezon City")
    country: Optional[str] = Field(pattern=r"^[a-zA-Z\s]+$", min_length=1, max_length=100, default="Philippines")
    street: Optional[str] = Field(pattern=r"^(\w+[,.]?\s?)+$", min_length=1, max_length=100, default="Narra street")
    postal: Optional[str] = Field(pattern=r"^\d{4,10}$", min_length=0, max_length=10, default="12345")

class PersonUpdate(BaseModel):
    name: Optional[str] = Field(pattern=r"^[a-zA-Z\s]+$", min_length=1, max_length=100, default="John doe")
    email: Optional[str] = Field(pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$", min_length=1, max_length=100, default="example@email.com")
    phone: Optional[str] = Field(pattern=r"^(09|\+639)\d{9}$", min_length=1, max_length=15, default="09123456789")
    address: Optional[AddressBookCreate] = None

# Dependency to get the database session
def get_db():
    db = sessionmaker()
    try:
        yield db
    finally:
        db.close()