from fastapi import APIRouter, HTTPException, Form, Query
from fastapi import Request
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.templating import Jinja2Templates
from app import crud


router = APIRouter()
templates = Jinja2Templates(directory="app/templates/admin")


@router.get("/dashboard",response_class=HTMLResponse)
async def show_admin_dashboard(request:Request):
    total_users = crud.get_active_user_count()
    monthly_income = crud.get_monthly_income()
    active_reservations = crud.get_active_reservations()
    recent_users = crud.get_recent_users()
    recent_payments = crud.get_recent_payments()
    upcoming_reservations = crud.get_upcoming_reservations()
    user = crud.get_user_by_id(request.session.get("user_id"))
    return templates.TemplateResponse("dashboard-admin.html", {
        "request":request,
        "admin_name": user["UserName"],
        "admin_email": user["Email"],
        "total_users":total_users,
        "monthly_income":monthly_income,
        "active_reservations":active_reservations,
        "recent_users":recent_users,
        "recent_payments":recent_payments,
        "upcoming_reservations":upcoming_reservations
    })


@router.get("/user-management",response_class=HTMLResponse)
async def user_management(request: Request, q: str = Query(default=None)):
    if q:
        users = crud.search_users(q)
    else:
        users = crud.get_all()
    return templates.TemplateResponse("admin-user-management.html", {"request": request, "users": users, "query": q})


@router.get("/user-details/{user_id}",response_class=HTMLResponse)
async def get_user_details(request: Request, user_id: int):
    user = crud.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı")

    reservations = crud.get_reservations_by_user(user_id)

    return templates.TemplateResponse("user-details.html", {
        "request": request,
        "user": user,
        "reservations": reservations
    })

@router.get("/user-management/{user_id}/edit")
async def edit_user_page(request: Request, user_id: int):
    user = crud.get_user_by_id(user_id)
    return templates.TemplateResponse("edit-user.html", {"request": request, "user": user})


@router.post("/user-management/{user_id}/edit")
async def update_user(
        request: Request,
        user_id: int,
        UserName: str = Form(...),
        Email: str = Form(...),
        PhoneNumber: str = Form(""),
        Address: str = Form(""),
        UserRoleLevel: int = Form(...),
        IsAccountActive: str = Form(...)
):
    is_active = True if IsAccountActive == "true" else False
    crud.update_user_in_db(user_id, UserName, Email, PhoneNumber, Address, UserRoleLevel, is_active)

    return RedirectResponse(url=f"/admin/user-details/{user_id}", status_code=303)

@router.post("/user-management/{user_id}/delete")
async def delete_user(user_id:int):
    deleted = crud.delete_user_by_id(user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Kullanıcı silinemedi!")
    return RedirectResponse(url="/admin/user-management",status_code=303)


@router.get("/reservations", response_class=HTMLResponse)
async def admin_reservations(request: Request, status: str = None):
    reservations = crud.get_all_reservations(status)
    return templates.TemplateResponse("admin-reservations.html", {
        "request": request,
        "reservations": reservations,
        "current_status": status or "Tümü"
    })


@router.get("/reservations/{reservation_id}", response_class=HTMLResponse)
async def admin_reservation_details(request: Request, reservation_id: int):
    reservation = crud.get_reservation_details(reservation_id)
    if not reservation:
        raise HTTPException(status_code=404, detail="Rezervasyon bulunamadı.")

    return templates.TemplateResponse("admin-reservation-details.html", {
        "request": request,
        "reservation": reservation
    })

@router.post("/reservations/{reservation_id}/delete")
async def admin_delete_reservation(reservation_id: int):
    success = crud.delete_reservation(reservation_id)
    if not success:
        raise HTTPException(status_code=404, detail="Rezervasyon silinemedi.")

    return RedirectResponse(url="/admin/reservations", status_code=303)

@router.get("/listings", response_class=HTMLResponse)
async def admin_listings(request: Request):
    listings = crud.get_all_listings()
    return templates.TemplateResponse("admin-listings.html", {
        "request": request,
        "listings": listings
    })


@router.get("/listings/{house_id}", response_class=HTMLResponse)
async def admin_listing_details(request: Request, house_id: int):
    listing = crud.get_listing_details(house_id)
    if not listing:
        raise HTTPException(status_code=404, detail="İlan bulunamadı.")

    return templates.TemplateResponse("admin-listing-details.html", {
        "request": request,
        "listing": listing
    })

@router.post("/listings/{house_id}/delete")
async def admin_delete_listing(house_id: int):
    success = crud.delete_listing(house_id)
    if not success:
        raise HTTPException(status_code=404, detail="İlan silinemedi.")

    return RedirectResponse(url="/admin/listings", status_code=303)

@router.get("/payments", response_class=HTMLResponse)
async def admin_payments(request: Request, status: str = None):
    payments = crud.get_all_payments(status)
    return templates.TemplateResponse("admin-payments.html", {
        "request": request,
        "payments": payments,
        "current_status": status or "Tümü"
    })


@router.get("/payments/{payment_id}", response_class=HTMLResponse)
async def admin_payment_details(request: Request, payment_id: int):
    payment = crud.get_payment_details(payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Ödeme bulunamadı.")

    return templates.TemplateResponse("admin-payment-details.html", {
        "request": request,
        "payment": payment
    })

@router.get("/statistics", response_class=HTMLResponse)
async def admin_statistics(request: Request):
    total_users = crud.get_total_users_count()
    active_users = crud.get_active_user_count()
    new_users = crud.get_recent_users_count()
    reservations_trend = crud.get_reservations_trend()
    payments_trend = crud.get_payments_trend()
    comments_count = crud.get_total_comments_count()

    return templates.TemplateResponse("admin-statistics.html", {
        "request": request,
        "total_users": total_users,
        "active_users": active_users,
        "new_users": new_users,
        "reservations_trend": reservations_trend,
        "payments_trend": payments_trend,
        "comments_count": comments_count
    })
