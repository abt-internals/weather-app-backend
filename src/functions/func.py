import random

from datetime import datetime,timedelta
from utils.valid import decode_token, create_access_token,create_refresh_token
from queries.query import update_password,update_user,get_temp_address,authenticate_email,store_otp,create_user,authenticate_user,store_refresh_token,check_token
from functions.weather_data import get_weather,get_weather_data
from functions.otp import send_email
from interfaces.request import Email,UserCreate

async def create_userdata(db,user_data:UserCreate):
    otp=random.randint(100000,999999)
    expiry=datetime.now() + timedelta(minutes=5)
    await create_user(db,user_data)
    await store_otp(db,user_data.email,otp,expiry)
    message=" user verification !! "
    email_status = await send_email(user_data.email, otp,message)
    return {"message": "OTP sent successfully", "email_status": email_status}

async def log_user(db,form_data):
    user=await authenticate_user(db,form_data.username,form_data.password)
    access_token,refresh_token= await create_refresh_token(data={"sub":str(user)})
    await store_refresh_token(db,refresh_token,user)
    return {"access_token":access_token,"refresh_token":refresh_token}

async def get_access_token(db,token):

        user =  decode_token(token)
        await check_token(db,user,token)
        return create_access_token(data={"sub":str(user)})


async def change_passd(db,token,pass_data):
    user =  decode_token(token)
    await check_token(db,user,token)
    return await update_password(db,user,pass_data)



async def update_userdata(db, user_data, token):
    user =  decode_token(token)
    return await update_user(db,user_data,user)

   
   


async def get_weatherdata(token: str, db, date:str=None, city:str=None):
    user = decode_token(token)


    if date is None and city is None :
        address = await get_temp_address(db, user)
        return await get_weather(address)

    elif city is None and date:
        address = await get_temp_address(db, user)
        return await get_weather_data(address, date)
    
    elif city and date is None:
        return await get_weather(city)
    
    else:
        return await get_weather_data(city, date)

async def forgot_pass(db,user_mail:Email):
    await authenticate_email(db,user_mail.email)
    
    otp=random.randint(100000,999999)
    expiry=datetime.now() + timedelta(minutes=5)
    await store_otp(db,user_mail.email,otp,expiry)
    message=" reseting password  !! "
    email_status = await send_email(user_mail.email, otp,message)
    return {"message": "OTP sent successfully", "email_status": email_status}

    
    

async def resend(db,user_mail:Email):
    otp=random.randint(100000,999999)
    expiry=datetime.now() + timedelta(minutes=5)
    await store_otp(db,user_mail.email,otp,expiry)
    message=" user verification !! "
    email_status = await send_email(user_mail.email, otp,message)
    return {"message": "OTP sent successfully", "email_status": email_status}
