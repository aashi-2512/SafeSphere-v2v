from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=True)
    phone = Column(String, unique=True, index=True, nullable=True)
    
    contacts = relationship("EmergencyContact", back_populates="user")
    alerts = relationship("SOSAlert", back_populates="user")

class EmergencyContact(Base):
    __tablename__ = "emergency_contacts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"))
    name = Column(String)
    phone = Column(String)

    user = relationship("User", back_populates="contacts")

class SOSAlert(Base):
    __tablename__ = "sos_alerts"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"))
    lat = Column(Float)
    lng = Column(Float)
    status = Column(String, default="active") # active, resolved
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    
    user = relationship("User", back_populates="alerts")
