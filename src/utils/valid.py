import re
from datetime import datetime, timedelta, timezone
from fastapi.responses import JSONResponse
import jwt
from jwt.exceptions import PyJWTError
import os
from dotenv import load_dotenv

load_dotenv


# Secret key for JWT
SECRET_KEY = os.getenv("SECRET_KEY")

# Algorithm for JWT

ALGORITHM = os.getenv("ALGORITHM")


async def valid_mobile(mobile: str):
    if not re.match(r"^91\d{10}", mobile):
        return JSONResponse(
            content={
                "success": False,
                "message": "Mobile number must be exactly 12 digits and should start with 91",
            },
            status_code=400,
        )
        # raise HTTPException(status_code=400,detail="Mobile number must be exactly 12 digits and should start with 91 ")


async def valid_username(username: str):
    if not re.match(r"^[\w.]{1,30}$", username):
        return JSONResponse(
            content={
                "success": False,
                "message": "Username should be max 30 characters long and should contain no special characters except '_' and '.'",
            },
            status_code=400,
        )
        # raise HTTPException(status_code=400,detail="Username should be max 30 characters long and should contain no special characters except '_' and '.'")


async def valid_email(email: str):
    if not re.match(r"^[\w.]+@[\w]+\.\w{2,}", email):
        return JSONResponse(
            content={
                "success": False,
                "message": "Invalid Format !!! Email should contain '@' and should contain 'gmail'or any other second-level domain should end with '.com' or any other domain",
            },
            status_code=400,
        )
        # raise HTTPException(status_code=400,detail="Invalid Format !!! Email should contain '@' and should contain 'gmail'or any other second-level domain should end with '.com' or any other domain ")


async def valid_dob(date_of_birth: str):
    if not re.match(
        r"^(19|20)\d{2}/(0[1-9]|1[0-2])/(0[1-9]|[12][0-9]|3[01])$", date_of_birth
    ):
        return JSONResponse(
            content={
                "success": False,
                "message": "Invalid Format !!! Date Should be in format YYYY/MM/DD. Month Should be below 12 and Date should be below 31",
            },
            status_code=400,
        )
        # raise HTTPException(status_code=400,detail="Invalid Format !!! Date Should be in format YYYY/MM/DD. Month Should be below 12 and Date should be below 31")


async def valid_pass(password: str):
    if not re.match(
        r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@])[A-Za-z\d@]{8,}$", password
    ):
        return JSONResponse(
            content={
                "success": False,
                "message": "Invalid Password Format!! Password should be atleast 8 character long and should contain Atleast one capital letter, small letter,digit,@",
            },
            status_code=400,
        )
        # raise HTTPException(status_code=400,detail="Invalid Password Format!! Password should be atleast 8 character long and should contain Atleast one capital letter, small letter,digit,@")


async def valid_otp(otp: int):
    data = str(otp)
    if not re.match(r"^\d{6}$", data):
        return JSONResponse(
            content={"success": False, "message": "Invalid OTP !!! OTP is of 6 Digits"},
            status_code=400,
        )
        # raise HTTPException(status_code=400,detail="Invalid OTP !!! OTP is of 6 Digits")


async def create_access_token(data: dict):
    log = data.copy()
    log.update(
        {"exp": datetime.now(timezone.utc) + timedelta(days=5), "token_type": "bearer"}
    )
    return jwt.encode(log, SECRET_KEY, algorithm=ALGORITHM)


async def create_refresh_token(data: dict):
    log = data.copy()
    log.update(
        {"exp": datetime.now(timezone.utc) + timedelta(days=7), "token_type": "bearer"}
    )

    refresh_token = jwt.encode(log, SECRET_KEY, algorithm=ALGORITHM)
    access_token = await create_access_token(data)

    return access_token, refresh_token


async def decode_token(token: str):
    try:
        #   if bol is True:
        #     payload = jwt.decode(token, options={"verify_signature": False})
        #     userid=payload.get("sub")
        #     return int(userid)

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
            options={"verify_signature": False},
        )
        userid = payload.get("sub")
        expiry = payload.get("exp")
        token_type = payload.get("token_type")

        if token_type != "bearer":
            return JSONResponse(
                content={"success": False, "message": "Invalid Token !!!"},
                status_code=400,
            )
            # raise HTTPException(status_code=400,detail="Invalid Token !!! ")

        if not userid:
            return JSONResponse(
                content={"success": False, "message": "Invalid Token !!!"},
                status_code=400,
            )
        #   raise HTTPException(status_code=400,detail="Invalid Token")

        if expiry < datetime.now(timezone.utc).timestamp():
            return JSONResponse(
                content={
                    "success": False,
                    "message": "Token Expired !!!! Try refreshing token or login again.",
                },
                status_code=400,
            )
        #    raise HTTPException(status_code=400,detail="Token Expired !!!! Try refreshing token or login again.")

        return int(userid)

    except PyJWTError:
        return JSONResponse(
            content={"success": False, "message": "Invalid access or refresh Token."},
            status_code=400,
        )
    #   raise HTTPException(status_code=400,detail="Invalid access or refresh Token")
