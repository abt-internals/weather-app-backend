from fastapi import FastAPI
from routes.root import router as root_router
from configs.postgres import engine
from models.databasemodel import Base

app = FastAPI()

Base.metadata.create_all(bind=engine)
# Include the routers defined in your route files
app.include_router(root_router)
