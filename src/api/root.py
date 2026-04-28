from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from api import user

router = APIRouter(tags=[""])
templates = Jinja2Templates(directory="templates")


@router.get("/", summary="домашняя страница страница", response_class=HTMLResponse)
async def index(req: Request):
    return templates.TemplateResponse(request=req, name="index.html")


@router.get("/favicon.ico")
async def ico():
    return {}


def reg(app):
    app.include_router(router)
    app.include_router(user.router)
