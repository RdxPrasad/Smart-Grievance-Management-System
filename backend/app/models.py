from sqlalchemy import Column, Integer, String, DateTime, BigInteger, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    role = Column(String, nullable=False)
    hashed_password = Column(String,nullable=True)
    auth_user_id = Column(UUID(as_uuid=True), nullable=True)
    department_id = Column(
    BigInteger,
    ForeignKey("departments.id"),
    nullable=True
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now())

    # ORM Relationships
    department = relationship("Department", back_populates="users")
    grievances = relationship("Grievance", back_populates="submitter")
    updates = relationship("GrievanceUpdate", back_populates="updater")


class Department(Base):
    __tablename__ = "departments"

    id = Column(BigInteger, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now())

    # ORM Relationships
    # A department has many users (staff/HODs) and many assigned grievances
    users = relationship("User", back_populates="department")
    grievances = relationship("Grievance", back_populates="department")

class Category(Base):
    __tablename__ = 'categories'

    id = Column(BigInteger , primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(Text , nullable=True)
    created_at = Column(DateTime(timezone=True),  server_default=func.now())
    updated_at = Column(DateTime(timezone=True),  server_default=func.now())

    # ORM Relationships
    # A category has many grievances
    grievances = relationship("Grievance", back_populates="category")

class Grievance(Base):
    __tablename__ = "grievances"

    id = Column(BigInteger , primary_key=True, index=True)
    submitted_by =  Column(BigInteger, ForeignKey('users.id'), nullable=False)
    complaint = Column(Text, nullable=False)
    priority = Column(String, nullable=False)
    status = Column(String, nullable=False)
    department_id = Column(
    BigInteger,
    ForeignKey("departments.id"),
    nullable=True
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now())
    category_id = Column(BigInteger, ForeignKey("categories.id"), nullable=True)

    # ORM Relationships
    submitter = relationship("User", back_populates="grievances")
    category = relationship("Category", back_populates="grievances")
    department = relationship("Department", back_populates="grievances")
    updates = relationship("GrievanceUpdate", back_populates="grievance", cascade="all, delete-orphan")

class GrievanceUpdate(Base):
    __tablename__ = "grievance_updates"

    id = Column(BigInteger , primary_key=True, index=True)
    grievance_id = Column(BigInteger, ForeignKey("grievances.id"), nullable=False)
    updated_by = Column(BigInteger, ForeignKey("users.id"), nullable=False) 
    status = Column(String, nullable=False)
    note = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # ORM Relationships
    grievance = relationship("Grievance", back_populates="updates")
    updater = relationship("User", back_populates="updates")
