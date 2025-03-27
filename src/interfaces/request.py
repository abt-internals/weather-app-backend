from pydantic import BaseModel, field_validator
from utils.valid import valid_dob, valid_email, valid_mobile, valid_username,valid_otp
from typing import Optional


class UserCreate(BaseModel):
    first_name: str
    last_name: str
    username: str
    email: str
    date_of_birth: str
    gender: str
    mobile: str
    passwords: str
    temp_address: str
    perm_address: str


    @field_validator("username")
    @classmethod
    def validate_username(cls, value):
        valid_username(value)
        return value

    @field_validator("mobile")
    @classmethod
    def validate_mobile(cls, value):
        valid_mobile(value)
        return value

    @field_validator("email")
    @classmethod
    def validate_email(cls, value):
        valid_email(value)
        return value

    @field_validator("date_of_birth")
    @classmethod
    def validate_dob(cls, value):
        valid_dob(value)
        return value

class passchange(BaseModel):
    old_password:str
    new_password:str
    
class updateuser(BaseModel):
    first_name: str = None
    last_name: str = None 
    username: str = None
    email: str = None
    date_of_birth: str = None
    gender: str = None
    mobile: str = None
    temp_address: str = None
    perm_address: str = None  

    @field_validator("username")
    @classmethod
    def validate_username(cls, value):
        valid_username(value)
        return value

    @field_validator("mobile")
    @classmethod
    def validate_mobile(cls, value):
        valid_mobile(value)
        return value

    @field_validator("email")
    @classmethod
    def validate_email(cls, value):
        valid_email(value)
        return value

    @field_validator("date_of_birth")
    @classmethod
    def validate_dob(cls, value):
        valid_dob(value)
        return value

class dashdata(BaseModel):
    address: Optional[str] = None
    date: Optional[str] = None

    # @field_validator("date")
    # @classmethod
    # def validate_dob(cls, value):
    #     valid_dob(value)
    #     return value

class Email(BaseModel):
    email: str

    @field_validator("email")
    @classmethod
    def validate_email(cls, value):
        valid_email(value)
        return value 

class OTP(BaseModel):
    email: str
    otp: int

    @field_validator("email")
    @classmethod
    def validate_email(cls, value):
        valid_email(value)
        return value
    
    @field_validator("otp")
    @classmethod
    def validate_otp(cls, value):
        valid_otp(value)
        return value

class empass(BaseModel):
    email: str
    password: str
            


