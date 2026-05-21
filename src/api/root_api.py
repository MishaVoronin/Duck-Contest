from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from api import contest_api, task_api, user_api
import os
from fastapi.staticfiles import StaticFiles

router = APIRouter(tags=[""])
templates = Jinja2Templates(directory="templates")


@router.get("/", summary="домашняя страница страница", response_class=HTMLResponse)
async def index(req: Request):
    return templates.TemplateResponse(request=req, name="index.html")


@router.get("/favicon.ico")
async def ico():
    return {}


def reg(app):
    os.makedirs("static", exist_ok=True)
    app.mount("/static", StaticFiles(directory="static"), name="static")
    app.include_router(router)
    app.include_router(user_api.router)
    app.include_router(contest_api.router)
    app.include_router(task_api.router)
