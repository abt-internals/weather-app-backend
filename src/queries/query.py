from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from models.databasemodel import User, Usercred, Useraddress, Userrefresh
from interfaces.request import UserCreate,passchange,OTP,empass
from fastapi import HTTPException
from datetime import datetime
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def create_user(db: Session, user_data: UserCreate):
    try :
        new_user = User(first_name=user_data.first_name,
            last_name=user_data.last_name,
            username=user_data.username,
            date_of_birth=datetime.strptime(user_data.date_of_birth, r"%Y/%m/%d").date(),
            gender=user_data.gender,
            )  
        
        new_user.credentials=Usercred(
            email=user_data.email,
            mobile=user_data.mobile,
            passwords=pwd_context.hash(user_data.passwords))
        
        new_user.address=Useraddress(
            temp_address=user_data.temp_address,
            perm_address=user_data.perm_address)
        
        new_user.refresh=Userrefresh(
            refresh_token="")

        

        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except IntegrityError as e:

        db.rollback()
        if user_data.email in str(e.orig):
            raise HTTPException(status_code=400, detail="Email is already present in database")
        
        elif user_data.username in str(e.orig):
            raise HTTPException(status_code=400, detail="Username is already present in database")

        elif user_data.mobile in str(e.orig):
            raise HTTPException(status_code=400, detail="Mobile no. is already present in database")

    return {"message":"User Created Successfully"}

async def store_refresh_token(db: Session,refresh_token:str,user_id:int):
    
    user=db.query(Userrefresh).filter(Userrefresh.id==user_id).first()
    user.refresh_token=refresh_token
    
    db.commit()
    db.refresh(user)
    
    return {"message":"Refresh Token Stored Successfully"}

async def get_refresh_token(db: Session,user_id:int):

    user=db.query(Userrefresh).filter(Userrefresh.id==user_id).first()
    
    return user.refresh_token

async def update_password(db: Session,user_id:int,pass_data:passchange):

    user=db.query(Usercred).filter(Usercred.id==user_id).first()
    
    if not pwd_context.verify(pass_data.old_password, user.passwords):
        raise HTTPException(status_code=400,detail="Incorrect Old Password")

    if pwd_context.verify(pass_data.new_password, user.passwords):
        raise HTTPException(status_code=400,detail="New Password should not be same as Old Password")     
    
    user.passwords=pwd_context.hash(pass_data.new_password)
    
    db.commit()
    db.refresh(user)
    
    return {"message":"Password Changed Successfully"}




async def authenticate_user(db: Session, email: str, password: str):
    user = db.query(Usercred).filter(Usercred.email == email).first()

    if not user :
            raise HTTPException(status_code=404,detail="User not Found")
    
    if user.is_verified is False:
        raise HTTPException(status_code=400,detail="User not Verified") 
    
    passs=user.passwords
    
    if not pwd_context.verify(password, passs):   
            raise HTTPException(status_code=400,detail="Incorrect Password")
        
    return user.id   


async def authenticate_email(db: Session, email:str):

    user = db.query(Usercred).filter(Usercred.email == email).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user.id

async def update_user(db,data,user):

    user_data=data.dict(exclude_unset=True) 

    users=db.query(User).filter(User.id==user).first()
    user_cred=db.query(Usercred).filter(Usercred.id==user).first()
    user_address=db.query(Useraddress).filter(Useraddress.id==user).first()
    if not users:
        raise HTTPException(status_code=404,detail="User not Found")
     
    fields = {"first_name", "last_name", "username", "gender", "date_of_birth"}
    cred_fields = {"email", "mobile"}
    address_fields = {"temp_address", "perm_address"}

    for field,value in user_data.items():
        if field in fields and value is not None:
            setattr(users,field,value)
        elif field in cred_fields and value is not None:
            setattr(user_cred,field,value)
        elif field in address_fields and value is not None:
            setattr(user_address,field,value)
        else:
            raise HTTPException(status_code=400,detail="Invalid Field")

    db.commit()

    return {"message":"User Data Updated Successfully"}    
        
async def get_temp_address(db: Session,user:int):
     user=db.query(Useraddress).filter(Useraddress.id==user).first()
     return user.temp_address        
        
async def store_otp(db,users,otp,expiry):

    user=db.query(Usercred).filter(Usercred.email==users).first()
    user.otp=otp
    user.expiry_time=expiry
    user.is_verified=False
    db.commit()
    db.refresh(user)

    return {"message":"OTP Stored Successfully"}

async def verifyotp(db,client:OTP):

     user=db.query(Usercred).filter(Usercred.email==client.email).first()
     if not user:
        raise HTTPException(status_code=404, detail="User not found")
     
         # Check if OTP exists in the database
     

     otp=client.otp

     if otp!=user.otp:
         raise HTTPException(status_code=400,detail="Invalid OTP")
     
     if datetime.now()>user.expiry_time:
         raise HTTPException(status_code=404, detail="Otp Expired !!! ")
     
     user.otp = None
     user.is_verified=True
     user.expiry_time=None
     db.commit()
     db.refresh(user)
     return {"message":"OTP Verified Successfully"} 

async def change_pass(db,user_pass:empass):
    
    user=db.query(Usercred).filter(Usercred.email==user_pass.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.is_verified is False:
        raise HTTPException(status_code=400,detail="User not Verified")
    
    user.passwords=pwd_context.hash(user_pass.password)
    db.commit()
    db.refresh(user)
    return {"message":"Password Reset Successfully"}     

async def check_token(db,user_id,token):
    user=db.query(Userrefresh).filter(Userrefresh.id==user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.refresh_token!=token:
        raise HTTPException(status_code=404, detail="Pass refresh token")
    
    return {"message":"User Verified"}