from fastapi import FastAPI
from api import root

app = FastAPI()
root.reg(app)
