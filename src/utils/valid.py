import re
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import HTTPException
from jwt.exceptions import PyJWTError

# Secret key for JWT
SECRET_KEY = "e2afd725508881dbb4977ee55ee2444b645406d8b552ceec65295c6ec4fa88f2"

# Algorithm for JWT
ALGORITHM = "HS256"




def valid_mobile(mobile:str):

    if not re.match(r"^91\d{10}",mobile):

        raise HTTPException(status_code=400,detail="Mobile number must be exactly 12 digits and should start with 91 ")
    
def valid_username(username:str):

    if not re.match(r"^[\w.]{1,30}$",username):

        raise HTTPException(status_code=400,detail="Username should be max 30 characters long and should contain no special characters except '_' and '.'") 

def valid_email(email:str):

    if not re.match(r"^[\w.]+@[\w]+\.\w{2,}", email) :

        raise HTTPException(status_code=400,detail="Invalid Format !!! Email should contain '@' and should contain 'gmail'or any other second-level domain should end with '.com' or any other domain ")

def valid_dob(date_of_birth:str):
    
        if not re.match(r"^(19|20)\d{2}/(0[1-9]|1[0-2])/(0[1-9]|[12][0-9]|3[01])$",date_of_birth):
            
            raise HTTPException(status_code=400,detail="Invalid Format !!! Date Should be in format YYYY/MM/DD. Month Should be below 12 and Date should be below 31")
        
def valid_pass(password:str):
    if not re.match(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@])[A-Za-z\d@]{8,}$",password):
            raise HTTPException(status_code=400,detail="Invalid Password Format!! Password should be atleast 8 character long and should contain Atleast one capital letter, small letter,digit,@")

def valid_otp(otp:int):
     
     data=str(otp)
     if not re.match(r"^\d{6}$",data):

        raise HTTPException(status_code=400,detail="Invalid OTP !!! OTP is of 6 Digits")

def create_access_token(data: dict):
    log=data.copy()
    log.update({"exp":datetime.now(timezone.utc)+timedelta(days=5)})
    return jwt.encode(log, SECRET_KEY, algorithm=ALGORITHM)


async def create_refresh_token(data: dict):
    
        log=data.copy()
        log.update({"exp":datetime.now(timezone.utc)+timedelta(days=7)})
        refresh_token=jwt.encode(log, SECRET_KEY, algorithm=ALGORITHM)
        access_token=create_access_token(data)

        return access_token,refresh_token



def decode_token(token:str):
    try:
        #   if bol is True:
        #     payload = jwt.decode(token, options={"verify_signature": False})
        #     userid=payload.get("sub")
        #     return int(userid)
          
          payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM],options={"verify_signature": False})
          userid=payload.get("sub")
          expiry=payload.get("exp")

          if not userid:
              raise HTTPException(status_code=400,detail="Invalid Token")
          
          if expiry<datetime.now(timezone.utc).timestamp():
               raise HTTPException(status_code=400,detail="Token Expired !!!! Try refreshing token or login again.")
          
          
          
          return int(userid)
          
          
    except PyJWTError:
          raise HTTPException(status_code=400,detail="Invalid access or refresh Token")


          
    
    
