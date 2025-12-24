from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request
from starlette.responses import HTMLResponse, RedirectResponse
from starlette.templating import Jinja2Templates
from app.routers import auth, admin, owner, tenant


app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.add_middleware(SessionMiddleware,secret_key="MehmetBozkurt")



app.include_router(auth.router, prefix="/auth")
app.include_router(admin.router, prefix="/admin")
app.include_router(owner.router, prefix="/owner")
app.include_router(tenant.router, prefix="/tenant")


@app.get("/")
async def root():
    return RedirectResponse(url="/auth/redirect-login")
