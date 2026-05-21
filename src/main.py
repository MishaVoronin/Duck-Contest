from fastapi import FastAPI
from api import root_api

app = FastAPI()
root_api.reg(app)
