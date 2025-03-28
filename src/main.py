from fastapi import FastAPI
from routes.root import router as root_router
from configs.postgres import engine
from models.databasemodel import Base
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],  
    allow_headers=["*"],  
    allow_credentials=True, 
)

Base.metadata.create_all(bind=engine)
# Include the routers defined in your route files
app.include_router(root_router)
