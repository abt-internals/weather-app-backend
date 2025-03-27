from sqlalchemy import Column, Integer, String,Date,ForeignKey,Boolean,TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import expression
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "userInfo"
    
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    username = Column(String, unique=True, nullable=False)
    date_of_birth = Column(Date, nullable=False)
    gender = Column(String, nullable=False)

    # Relationships
    credentials = relationship("Usercred", back_populates="user", uselist=False)
    address = relationship("Useraddress", back_populates="user", uselist=False)
    refresh = relationship("Userrefresh", back_populates="user", uselist=False)


class Usercred(Base):
    __tablename__ = "userCred"
    
    id = Column(Integer, ForeignKey("userInfo.id"), primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False)
    mobile = Column(String, unique=True, nullable=False)
    passwords = Column(String, nullable=False)
    otp = Column(Integer, nullable=True, default=None)
    is_verified = Column(Boolean, nullable=True, server_default=expression.false())
    expiry_time = Column(TIMESTAMP, nullable=True)

    # Relationship
    user = relationship("User", back_populates="credentials", uselist=False)


class Useraddress(Base):
    __tablename__ = "userAddress"

    id = Column(Integer, ForeignKey("userInfo.id"), primary_key=True, index=True)
    temp_address = Column(String, nullable=False)
    perm_address = Column(String, nullable=False)   

    # Relationship
    user = relationship("User", back_populates="address", uselist=False)


class Userrefresh(Base):
    __tablename__ = "userRefresh"
    
    id = Column(Integer, ForeignKey("userInfo.id"), primary_key=True, index=True)
    refresh_token = Column(String, nullable=True, default=None)
    
    # Relationship
    user = relationship("User", back_populates="refresh", uselist=False)


    