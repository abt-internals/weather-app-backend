from pydantic import BaseModel

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


class passchange(BaseModel):
    old_password: str
    new_password: str

    # @field_validator("new_password")
    # @classmethod
    # async def validate_newpassword(cls,value):
    #     await valid_pass(value)
    #     return value


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


class dashdata(BaseModel):
    address: Optional[str] = None
    date: Optional[str] = None


class Email(BaseModel):
    email: str


class OTP(BaseModel):
    email: str
    otp: int


class empass(BaseModel):
    email: str
    password: str
