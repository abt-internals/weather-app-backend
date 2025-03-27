from fastapi import APIRouter, Depends
from interfaces.request import UserCreate,passchange,updateuser,Email,OTP,empass      #request.py
from sqlalchemy.orm import Session
from configs.postgres import get_db
from queries.query import verifyotp,change_pass                      #query.py
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
#from utils.valid import                                                         #valid.py
from functions.func import get_access_token,change_passd,update_userdata,get_weatherdata,forgot_pass,create_userdata,log_user,resend #func.py

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@router.post("/register")
async def add_user(user_data: UserCreate, db: Session = Depends(get_db)):
    return await create_userdata(db, user_data)
    
@router.post("/login")
async def check_user(form_data: OAuth2PasswordRequestForm = Depends(),db: Session = Depends(get_db)):
    return await log_user(db,form_data)
    

@router.get("/refresh")
async def refresh_token(token:str = Depends(oauth2_scheme),db: Session = Depends(get_db)):
    return await get_access_token(db,token)

@router.put("/changepass")
async def change_password(pass_data:passchange, token: str = Depends(oauth2_scheme) , db: Session = Depends(get_db)):

    return await change_passd(db,token,pass_data)

    
@router.put("/update")
async def update_user(user_data: updateuser, token:str = Depends(oauth2_scheme),  db: Session = Depends(get_db)):
    return await update_userdata(db, user_data, token)  

@router.get("/dashboard")
async def none_info(token:str=Depends(oauth2_scheme),db:Session=Depends(get_db)):
    return await get_weatherdata(token,db)


@router.put("/search/")
async def dashboard(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db),d:str=None,city:str=None):
    return await get_weatherdata(token, db, d,city) 


@router.post("/forgotpassword")
async def forgot_password(user_mail:Email,db: Session = Depends(get_db)):
    return await forgot_pass(db,user_mail)

@router.post("/verifyotp")
async def verify_otp(user:OTP,db: Session = Depends(get_db)):
    return await verifyotp(db,user)

@router.post("/resendotp")
async def resend_otp(user_mail:Email,db:Session=Depends(get_db)):
    return await resend(db,user_mail) 


@router.post("/resetpass")
async def reset_password(user_pass:empass,db: Session = Depends(get_db)):
    return await change_pass(db,user_pass)


    
    
