from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse, HTMLResponse
from starlette.responses import RedirectResponse
from starlette.templating import Jinja2Templates
from app import crud

router = APIRouter()
templates = Jinja2Templates(directory="app/templates/auth")

# GET → login sayfası göster
@router.get("/redirect-login", response_class=HTMLResponse)
async def redirect_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

# POST → login → FETCH ile JSON POST için uyumlu hale getirildi
@router.post("/login")
async def login(request: Request):
    data = await request.json()
    email = data.get("email")
    password = data.get("password")

    print("Login denemesi:", email, password)
    user = crud.check_user(email, password)

    if not user:
        raise HTTPException(status_code=401, detail="Geçersiz email veya şifre!")

    role_level = user.get("UserRoleLevel")
    if role_level == 0:
        redirect_url = "/admin/dashboard"
    elif role_level == 1:
        redirect_url = "/tenant/dashboard"
    elif role_level == 2:
        redirect_url = "/owner/dashboard"
    else:
        return JSONResponse(status_code=403, content={"detail": "Tanımsız Rol!"})

    request.session["user_id"] = user["UserId"]
    request.session["role"] = role_level

    print("Giriş başarılı:", user)
    return JSONResponse(content={"redirect": redirect_url})

# GET → sign-up sayfası
@router.get("/sign-up", response_class=HTMLResponse)
async def sign_up(request: Request):
    return templates.TemplateResponse("sign-up.html", {"request": request})

# POST → register → JSON POST bekliyor
@router.post("/register")
async def register(request: Request):
    data = await request.json()
    name = data.get("name")
    password = data.get("password")
    email = data.get("email")
    phone = data.get("phone")
    address = data.get("address")
    role_level = data.get("role_level")

    if not all([name, password, email, phone, address]) or role_level is None:
        return JSONResponse(status_code=400, content={"message": "Tüm alanlar zorunludur!"})

    success = crud.new_user(name, password, email, phone, address, role_level)

    if success:
        return {"message": "Kayıt başarılı"}
    else:
        return JSONResponse(status_code=400, content={"message": "Kayıt başarısız!"})
