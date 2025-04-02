import random
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta
from interfaces.request import UserCreate, passchange, Email
from utils.valid import (
    decode_token,
    create_access_token,
    create_refresh_token,
    valid_dob,
    valid_email,
    valid_mobile,
    valid_username,
    valid_pass,
)
from queries.query import (
    update_password,
    update_user,
    get_temp_address,
    authenticate_email,
    store_otp,
    create_user,
    authenticate_user,
    store_refresh_token,
    check_token,
)
from functions.weather_data import get_weather_data, get_weather
from functions.otp import send_email
import redis.asyncio as aioredis
import json

redis = aioredis.from_url("redis://localhost:6379", decode_responses=True)
CACHE_EXPIRY = 86400


async def create_userdata(db, user_data: UserCreate):
    otp = random.randint(100000, 999999)
    expiry = datetime.now() + timedelta(minutes=5)

    user_name = await valid_username(user_data.username)
    if isinstance(user_name, JSONResponse) and user_name.status_code == 400:
        return user_name

        # Validate mobile
    mobile = await valid_mobile(user_data.mobile)
    if isinstance(mobile, JSONResponse) and mobile.status_code == 400:
        return mobile
        # Validate email
    email = await valid_email(user_data.email)
    if isinstance(email, JSONResponse) and email.status_code == 400:
        return email
        # Validate passwords
    pass_valid = await valid_pass(user_data.passwords)
    if isinstance(pass_valid, JSONResponse) and pass_valid.status_code == 400:
        return pass_valid
        # Validate date_of_birth
    dob = await valid_dob(user_data.date_of_birth)
    if isinstance(dob, JSONResponse) and dob.status_code == 400:
        return dob

    message = await create_user(db, user_data)
    if isinstance(message, JSONResponse) and message.status_code == 400:
        return message
    await store_otp(db, user_data.email, otp, expiry)

    message = " user verification !! "
    email_status = await send_email(user_data.email, otp, message)
    if isinstance(email_status, JSONResponse) and email_status.status_code == 400:
        return email_status

    return JSONResponse(content={"success": True, "message": "OTP Sent Successfully"})

    # return {"message": "OTP sent successfully", "email_status": email_status}


async def log_user(db, form_data):
    email = await valid_email(form_data.username)
    if isinstance(email, JSONResponse) and email.status_code == 400:
        return email

    pass_valid = await valid_pass(form_data.password)
    if isinstance(pass_valid, JSONResponse) and pass_valid.status_code == 400:
        return pass_valid

    user = await authenticate_user(db, form_data.username, form_data.password)
    if isinstance(user, JSONResponse) and user.status_code == 400:
        return user

    access_token, refresh_token = await create_refresh_token(data={"sub": str(user)})
    await store_refresh_token(db, refresh_token, user)

    return JSONResponse(
        content={
            "success": True,
            "access_token": access_token,
            "refresh_token": refresh_token,
        }
    )
    # return {"access_token":access_token,"refresh_token":refresh_token}


async def get_access_token(db, token):
    user = await decode_token(token)
    if isinstance(user, JSONResponse) and user.status_code == 400:
        return user

    token_check_response = await check_token(db, user, token)
    if (
        isinstance(token_check_response, JSONResponse)
        and token_check_response.status_code == 400
    ):
        return token_check_response

    return await create_access_token(data={"sub": str(user)})


async def change_passd(db, token, pass_data: passchange):
    user = await decode_token(token)
    if isinstance(user, JSONResponse) and user.status_code == 400:
        return user

    token_check_response = await check_token(db, user, token)
    if (
        isinstance(token_check_response, JSONResponse)
        and token_check_response.status_code == 400
    ):
        return token_check_response

    pass_valid = await valid_pass(pass_data.old_password)
    if isinstance(pass_valid, JSONResponse) and pass_valid.status_code == 400:
        return pass_valid
    pass_valid = await valid_pass(pass_data.new_password)
    if isinstance(pass_valid, JSONResponse) and pass_valid.status_code == 400:
        return pass_valid

    return await update_password(db, user, pass_data)


async def update_userdata(db, user_data, token):
    user = await decode_token(token)
    if isinstance(user, JSONResponse) and user.status_code == 400:
        return user

    if user_data.username:
        user_name = await valid_username(user_data.username)
        if isinstance(user_name, JSONResponse) and user_name.status_code == 400:
            return user_name

    if user_data.mobile:  # Validate mobile
        mobile = await valid_mobile(user_data.mobile)
        if isinstance(mobile, JSONResponse) and mobile.status_code == 400:
            return mobile

    if user_data.email:  # Validate email
        email = await valid_email(user_data.email)
        if isinstance(email, JSONResponse) and email.status_code == 400:
            return email

    if user_data.date_of_birth:  # Validate date_of_birth
        dob = await valid_dob(user_data.date_of_birth)
        if isinstance(dob, JSONResponse) and dob.status_code == 400:
            return dob

    data = await update_user(db, user_data, user)
    if isinstance(data, JSONResponse) and data.status_code == 400:
        return data
    return data


async def get_weatherdata(token: str, db, date: str = None, city: str = None):
    user = await decode_token(token)
    if isinstance(user, JSONResponse) and user.status_code == 400:
        return user

    if date:
        dob = await valid_dob(date)
        if isinstance(dob, JSONResponse) and dob.status_code == 400:
            return dob

    if date is None and city is None:
        address = await get_temp_address(db, user)
        date = datetime.today().date()

        redis_key = f"{address}:{date}"

        data = await redis.get(redis_key)

        if data:
            return json.loads(data)

        data = await get_weather(address)
        if isinstance(data, JSONResponse) and data.status_code == 500:
            return data

        await redis.setex(redis_key, CACHE_EXPIRY, json.dumps(data))

        return data

    elif city is None and date:
        address = await get_temp_address(db, user)

        redis_key = f"{address}:{date}"

        data = await redis.get(redis_key)

        if data:
            return json.loads(data)

        data = await get_weather_data(address, date)
        if isinstance(data, JSONResponse) and data.status_code == 500:
            return data

        await redis.setex(redis_key, CACHE_EXPIRY, json.dumps(data))

        return data

        # return await get_weather_data(address, date)

    elif city and date is None:
        date = datetime.today().date()
        redis_key = f"{city}:{date}"

        data = await redis.get(redis_key)

        if data:
            return json.loads(data)

        data = await get_weather(city)
        if isinstance(data, JSONResponse) and data.status_code == 500:
            return data

        await redis.setex(redis_key, CACHE_EXPIRY, json.dumps(data))

        return data

        # return await fetch_weather(city)

    else:
        redis_key = f"{city}:{date}"

        data = await redis.get(redis_key)

        if data:
            return json.loads(data)

        data = await get_weather_data(city, date)
        if isinstance(data, JSONResponse) and data.status_code == 500:
            return data

        await redis.setex(redis_key, CACHE_EXPIRY, json.dumps(data))

        return data

        # return await get_weather_data(city, date)


async def forgot_pass(db, user_mail: Email):
    email = await valid_email(user_mail.email)
    if isinstance(email, JSONResponse) and email.status_code == 400:
        return email

    valid = await authenticate_email(db, user_mail.email)
    if isinstance(valid, JSONResponse) and valid.status_code == 400:
        return valid

    otp = random.randint(100000, 999999)
    expiry = datetime.now() + timedelta(minutes=5)
    await store_otp(db, user_mail.email, otp, expiry)
    message = " reseting password  !! "
    email_status = await send_email(user_mail.email, otp, message)
    if isinstance(email_status, JSONResponse) and email_status.status_code == 400:
        return email_status

    return JSONResponse(content={"success": True, "message": "OTP Sent Successfully"})


async def resend(db, user_mail: Email):
    email = await valid_email(user_mail.email)
    if isinstance(email, JSONResponse) and email.status_code == 400:
        return email

    valid = await authenticate_email(db, user_mail.email)
    if isinstance(valid, JSONResponse) and valid.status_code == 400:
        return valid

    otp = random.randint(100000, 999999)
    expiry = datetime.now() + timedelta(minutes=5)
    await store_otp(db, user_mail.email, otp, expiry)
    message = " user verification !! "

    email_status = await send_email(user_mail.email, otp, message)
    if isinstance(email_status, JSONResponse) and email_status.status_code == 400:
        return email_status

    return JSONResponse(content={"success": True, "message": "OTP Sent Successfully"})
