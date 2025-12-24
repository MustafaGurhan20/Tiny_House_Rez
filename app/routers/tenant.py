from fastapi import APIRouter, HTTPException, Query
from fastapi import Request, Form
from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse
from starlette.templating import Jinja2Templates
from app import crud

router = APIRouter()
templates = Jinja2Templates(directory="app/templates/tenant")



@router.get("/dashboard", response_class=HTMLResponse)
async def show_tenant_dashboard(request: Request):
    tenant_id = request.session.get("user_id")
    if not tenant_id:
        raise HTTPException(status_code=403, detail="Giriş yapmanız gerekiyor.")

    # Kullanıcı bilgileri
    user = crud.get_user_by_id(tenant_id)

    # Popüler evler
    popular_houses = crud.get_popular_houses(limit=4)

    # Son rezervasyonlar
    recent_reservations = crud.get_recent_reservations_by_tenant(tenant_id, limit=3)

    return templates.TemplateResponse("dashboard-tenant.html", {
        "request": request,
        "tenant_name": user["UserName"],
        "tenant_email": user["Email"],
        "popular_houses": popular_houses,
        "recent_reservations": recent_reservations
    })




@router.get("/explore", response_class=HTMLResponse)
async def explore_houses(request: Request, q: str = Query(default=None)):
    houses = crud.search_houses(q)
    return templates.TemplateResponse("tenant-explore.html", {
        "request": request,
        "houses": houses,
        "query": q
    })

@router.post("/reserve", response_class=HTMLResponse)
async def create_reservation(
    request: Request,
    house_id: int = Form(...),
    start_date: str = Form(...),
    end_date: str = Form(...),

):

    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse(url="/", status_code=302)

    try:
        if crud.is_reservation_conflict(house_id=house_id, start=start_date, end=end_date):
            return templates.TemplateResponse("tenant-explore.html", {
                "request": request,
                "houses": crud.search_houses(),
                "query": "",
                "alert": "Bu tarihler arasında zaten bir rezervasyon var!"
            })

        res_id = crud.add_reservation(user_id, house_id, start_date, end_date)

        return templates.TemplateResponse("tenant-explore.html", {
            "request": request,
            "houses": crud.search_houses(),
            "query": "",
            "alert": "Rezervasyon talebiniz iletilmiştir! Ev sahibinin onaylamasını bekleyin."
        })

    except Exception as e:
        print("Rezervasyon hatası:", e)
        return templates.TemplateResponse("tenant-explore.html", {
            "request": request,
            "houses": crud.search_houses(),
            "query": "",
            "alert": "Bir hata oluştu! Lütfen tekrar deneyin."
        })


@router.get("/reservations", response_class=HTMLResponse)
async def tenant_reservations(request: Request):
    tenant_id = request.session.get("user_id")
    if not tenant_id:
        raise HTTPException(status_code=403, detail="Giriş yapmanız gerekiyor.")

    reservations = crud.get_reservations_by_tenant(tenant_id)

    return templates.TemplateResponse("tenant-reservations.html", {
        "request": request,
        "reservations": reservations
    })


@router.get("/comments", response_class=HTMLResponse)
async def tenant_comments(request: Request):
    tenant_id = request.session.get("user_id")
    if not tenant_id:
        raise HTTPException(status_code=403, detail="Giriş yapmanız gerekiyor.")

    comments = crud.get_comments_by_tenant(tenant_id)

    return templates.TemplateResponse("tenant-comments.html", {
        "request": request,
        "comments": comments
    })



@router.post("/add-comment")
async def add_comment(
    request: Request,
    house_id: int = Form(...),
    content: str = Form(...),
    star: int = Form(...)
):
    tenant_id = request.session.get("user_id")
    if not tenant_id:
        raise HTTPException(status_code=403, detail="Giriş yapmanız gerekiyor.")

    # Güvenlik: Bu tenant gerçekten bu evi Confirmed olarak kiralamış mı?
    cursor = crud.cursor
    cursor.execute("""
        SELECT COUNT(*) 
        FROM tblReservation
        WHERE TenantId = ? AND HouseId = ? AND ReservationStatus = 'Confirmed'
    """, (tenant_id, house_id))
    count = cursor.fetchone()[0]

    if count == 0:
        return JSONResponse(status_code=400, content={"message": "Bu ev için yorum ekleyemezsiniz!"})

    success = crud.add_comment(tenant_id, house_id, content, star)

    if success:
        return RedirectResponse(url="/tenant/reservations", status_code=303)
    else:
        return JSONResponse(status_code=500, content={"message": "Yorum eklenirken bir hata oluştu!"})
