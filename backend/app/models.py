from sqlalchemy import Column, Integer, String, DateTime, BigInteger, Text, ForeignKey
from sqlalchemy.sql import func

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    role = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now())


class Category(Base):
    __tablename__ = 'categories'

    id = Column(BigInteger , primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(Text , nullable=True)
    created_at = Column(DateTime(timezone=True),  server_default=func.now())
    updated_at = Column(DateTime(timezone=True),  server_default=func.now())


class Grievance(Base):
    __tablename__ = "grievances"

    id = Column(BigInteger , primary_key=True, index=True)
    submitted_by =  Column(BigInteger, ForeignKey('users.id'), nullable=False)
    complaint = Column(Text, nullable=False)
    priority = Column(String, nullable=False)
    status = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now())
    category_id = Column(BigInteger, ForeignKey("categories.id"), nullable=False)


class GrievanceUpdate(Base):
    __tablename__ = "grievance_updates"

    id = Column(BigInteger , primary_key=True, index=True)
    grievance_id = Column(BigInteger, ForeignKey("grievances.id"), nullable=False)
    updated_by = Column(BigInteger, ForeignKey("users.id"), nullable=False) 
    status = Column(String, nullable=False)
    note = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
