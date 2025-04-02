from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from fastapi.responses import JSONResponse
from sqlalchemy.future import select
from models.databasemodel import User, Usercred, Useraddress, Userrefresh
from interfaces.request import UserCreate, passchange, OTP, empass
from datetime import datetime
from utils.valid import valid_email, valid_otp
from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def create_user(db: AsyncSession, user_data: UserCreate):
    try:
        new_user = User(
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            username=user_data.username,
            date_of_birth=datetime.strptime(
                user_data.date_of_birth, r"%Y/%m/%d"
            ).date(),
            gender=user_data.gender,
        )

        new_user.credentials = Usercred(
            email=user_data.email,
            mobile=user_data.mobile,
            passwords=pwd_context.hash(user_data.passwords),
        )

        new_user.address = Useraddress(
            temp_address=user_data.temp_address, perm_address=user_data.perm_address
        )

        new_user.refresh = Userrefresh(refresh_token="")

        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        return JSONResponse(
            content={"success": True, "message": "User Created Successfully"}
        )

    except IntegrityError as e:
        await db.rollback()
        if user_data.email in str(e.orig):
            error_message = "Email is already present in database"

        elif user_data.mobile in str(e.orig):
            error_message = "Mobile no. is already present in database"

        elif user_data.username in str(e.orig):
            error_message = "Username is already present in database"

        return JSONResponse(
            content={"success": False, "message": error_message}, status_code=400
        )


async def store_refresh_token(db: AsyncSession, refresh_token: str, user_id: int):
    result = await db.execute(select(Userrefresh).filter(Userrefresh.id == user_id))
    user = result.scalars().first()

    user.refresh_token = refresh_token

    await db.commit()
    await db.refresh(user)

    return JSONResponse(
        content={"success": True, "message": "Refresh Token Stored Successfully"}
    )


async def get_refresh_token(db: AsyncSession, user_id: int):
    result = await db.execute(select(Userrefresh).filter(Userrefresh.id == user_id))
    user = result.scalars().first()

    return user.refresh_token


async def update_password(db: AsyncSession, user_id: int, pass_data: passchange):
    result = await db.execute(select(Usercred).filter(Usercred.id == user_id))
    user = result.scalars().first()

    if not pwd_context.verify(pass_data.old_password, user.passwords):
        return JSONResponse(
            content={"success": False, "message": "Incorrect Old Password"},
            status_code=400,
        )

    if pwd_context.verify(pass_data.new_password, user.passwords):
        return JSONResponse(
            content={"success": False, "message": "New and old password are same"},
            status_code=400,
        )

    user.passwords = pwd_context.hash(pass_data.new_password)

    await db.commit()
    await db.refresh(user)

    return JSONResponse(
        content={"success": True, "message": "Password Changed Successfully"}
    )


async def authenticate_user(db: AsyncSession, email: str, password: str):
    result = await db.execute(select(Usercred).filter(Usercred.email == email))
    user = result.scalars().first()

    if not user:
        return JSONResponse(
            content={"success": False, "message": "User Not Found"}, status_code=400
        )

    if user.is_verified is False:
        return JSONResponse(
            content={"success": False, "message": "User not Verified"}, status_code=400
        )

    passs = user.passwords

    if not pwd_context.verify(password, passs):
        return JSONResponse(
            content={"success": False, "message": "Incorrect Password"}, status_code=400
        )

    return user.id


async def authenticate_email(db: AsyncSession, email: str):
    result = await db.execute(select(Usercred).filter(Usercred.email == email))
    user = result.scalars().first()

    if not user:
        return JSONResponse(
            content={"success": False, "message": "User not Found"}, status_code=400
        )

    return user.id


async def update_user(db: AsyncSession, data, user):
    user_data = data.dict(exclude_unset=True)

    users_result = await db.execute(select(User).filter(User.id == user))
    users = users_result.scalars().first()

    user_cred_result = await db.execute(select(Usercred).filter(Usercred.id == user))
    user_cred = user_cred_result.scalars().first()

    user_address_result = await db.execute(
        select(Useraddress).filter(Useraddress.id == user)
    )
    user_address = user_address_result.scalars().first()

    if not users:
        return JSONResponse(
            content={"success": False, "message": "User not Found"}, status_code=400
        )

    fields = {"first_name", "last_name", "username", "gender", "date_of_birth"}
    cred_fields = {"email", "mobile"}
    address_fields = {"temp_address", "perm_address"}

    for field, value in user_data.items():
        if field in fields and value is not None:
            setattr(users, field, value)
        elif field in cred_fields and value is not None:
            setattr(user_cred, field, value)
        elif field in address_fields and value is not None:
            setattr(user_address, field, value)
        else:
            return JSONResponse(
                content={"success": False, "message": "Invalid Field"}, status_code=400
            )

    await db.commit()

    return JSONResponse(
        content={"success": True, "message": "User Data Updated Successfully"}
    )


async def get_temp_address(db: AsyncSession, user: int):
    result = await db.execute(select(Useraddress).filter(Useraddress.id == user))
    user = result.scalars().first()

    return user.temp_address


async def store_otp(db: AsyncSession, users, otp, expiry):
    result = await db.execute(select(Usercred).filter(Usercred.email == users))
    user = result.scalars().first()

    user.otp = otp
    user.expiry_time = expiry
    user.is_verified = False
    await db.commit()
    await db.refresh(user)

    return JSONResponse(content={"success": True, "message": "OTP Stored Successfully"})


async def verifyotp(db: AsyncSession, client: OTP):
    email = await valid_email(client.email)
    if isinstance(email, JSONResponse) and email.status_code == 400:
        return email

    otp = await valid_otp(client.otp)
    if isinstance(otp, JSONResponse) and otp.status_code == 400:
        return otp

    result = await db.execute(select(Usercred).filter(Usercred.email == client.email))
    user = result.scalars().first()

    if not user:
        return JSONResponse(
            content={"success": False, "message": "User not Found"}, status_code=404
        )

        # Check if OTP exists in the database

    otp = client.otp

    if otp != user.otp:
        return JSONResponse(
            content={"success": False, "message": "Invalid OTP"}, status_code=400
        )

    if datetime.now() > user.expiry_time:
        return JSONResponse(
            content={"success": False, "message": "OTP Expired"}, status_code=404
        )

    user.otp = None
    user.is_verified = True
    user.expiry_time = None

    await db.commit()
    await db.refresh(user)
    return JSONResponse(
        content={"success": True, "message": "OTP Verified Successfully"}
    )


async def change_pass(db: AsyncSession, user_pass: empass):
    result = await db.execute(
        select(Usercred).filter(Usercred.email == user_pass.email)
    )
    user = result.scalars().first()

    if not user:
        return JSONResponse(
            content={"success": False, "message": "User not Found"}, status_code=404
        )

    if user.is_verified is False:
        return JSONResponse(
            content={"success": False, "message": "User not Verified"}, status_code=400
        )

    user.passwords = pwd_context.hash(user_pass.password)

    await db.commit()
    await db.refresh(user)

    return JSONResponse(
        content={"success": True, "message": "Password Reseted Successfully"}
    )


async def check_token(db: AsyncSession, user_id, token):
    result = await db.execute(select(Userrefresh).filter(Userrefresh.id == user_id))
    user = result.scalars().first()

    if not user:
        return JSONResponse(
            content={"success": False, "message": "User not Found"}, status_code=400
        )

    if user.refresh_token != token:
        return JSONResponse(
            content={"success": False, "message": "Pass Refresh Token"}, status_code=400
        )

    return JSONResponse(content={"success": True, "message": "User Verified"})
