from fastapi import APIRouter, HTTPException
from fastapi import Request, Form
from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse
from starlette.templating import Jinja2Templates
from app import crud

router = APIRouter()
templates = Jinja2Templates(directory="app/templates/owner")


@router.get("/dashboard", response_class=HTMLResponse)
async def show_owner_dashboard(request: Request):
    owner_id = request.session.get("user_id")
    if not owner_id:
        raise HTTPException(status_code=403, detail="Giriş yapmanız gerekiyor.")

    user = crud.get_user_by_id(owner_id)
    listings = crud.get_listings_by_owner(owner_id)
    active_listings = len([l for l in listings if l["IsHouseActive"] == 1])
    passive_listings = len([l for l in listings if l["IsHouseActive"] == 0])
    total_listings = len(listings)

    monthly_income = crud.get_owner_monthly_income(owner_id)
    total_income = crud.get_owner_total_income(owner_id)
    average_star = crud.owner_average_star(owner_id)
    recent_comments = crud.get_recent_comments(owner_id)

    return templates.TemplateResponse("dashboard-owner.html", {
        "request": request,
        "owner_name": user["UserName"],
        "owner_email": user["Email"],
        "total_listings": total_listings,
        "active_listings": active_listings,
        "passive_listings": passive_listings,
        "monthly_income": monthly_income,
        "total_income": total_income,
        "average_star": average_star,
        "recent_comments": recent_comments
    })


@router.get("/listings", response_class=HTMLResponse)
async def show_owner_listings(request: Request):
    owner_id = request.session.get("user_id")
    if not owner_id:
        raise HTTPException(status_code=403, detail="Giriş yapmanız gerekiyor.")

    listings = crud.get_listings_by_owner(owner_id)

    return templates.TemplateResponse("owner-listings.html", {
        "request": request,
        "listings": listings,
        "user": {"name": "owner", "role": "owner"}
    })


@router.post("/listings/{house_id}/activate")
async def activate_listing(house_id:int):
    activate = crud.update_house_active_status(house_id,True)
    return RedirectResponse(url="/owner/listings",status_code=303)


@router.post("/listings/{house_id}/deactivate")
async def deactivate_listing(house_id:int):
    activate = crud.update_house_active_status(house_id,False)
    return RedirectResponse(url="/owner/listings",status_code=303)


@router.get("/listings/new", response_class=HTMLResponse)
async def new_listing_form(request: Request):
    session = request.session
    user_id = session.get("user_id")
    return templates.TemplateResponse("new-listing.html", {"request": request, "user": {"UserId":user_id}})


@router.post("/listings/new")
async def new_listing(
    request: Request,
    location: str = Form(...),
    price: float = Form(...),
    description: str = Form(...),
    is_available: int = Form(1),
    is_active: int = Form(1)
):
    session = request.session
    user_id = session.get("user_id")

    if not user_id:
        return RedirectResponse(url="/login", status_code=302)

    crud.create_new_listing(
        user_id=user_id,
        location=location,
        price=price,
        description=description,
        avg_star=50,
        is_available=is_available,
        is_active=is_active
    )

    return RedirectResponse(url="/owner/listings", status_code=303)


@router.get("/listings/{house_id}/edit", response_class=HTMLResponse)
async def edit_listing_form(request: Request, house_id: int):
    session = request.session
    user_id = session.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login", status_code=302)

    house = crud.get_house_by_id(house_id)
    if not house:
        raise HTTPException(status_code=404, detail="İlan bulunamadı")

    return templates.TemplateResponse("edit-listing.html", {"request": request, "house": house})


@router.post("/listings/{house_id}/edit")
async def update_listing(
    request: Request,
    house_id: int,
    location: str = Form(...),
    price: float = Form(...),
    description: str = Form(...),
    is_available: str = Form("0"),
    is_active: str = Form("0")
):
    is_available_val = 1 if is_available == "1" else 0
    is_active_val = 1 if is_active == "1" else 0

    crud.update_house(
        house_id=house_id,
        location=location,
        price=price,
        description=description,
        is_available=is_available_val,
        is_active=is_active_val
    )

    return RedirectResponse(url="/owner/listings", status_code=303)


@router.post("/listings/{house_id}/delete")
async def delete_listing(house_id: int, request: Request):
    session = request.session
    user_id = session.get("user_id")

    if not user_id:
        return RedirectResponse(url="/login", status_code=302)

    crud.delete_house_by_id(house_id, user_id)
    return RedirectResponse(url="/owner/listings", status_code=303)


@router.get("/comments", response_class=HTMLResponse)
async def owner_comments(request: Request):
    owner_id = request.session.get("user_id")
    if not owner_id:
        raise HTTPException(status_code=403, detail="Giriş yapmanız gerekiyor.")

    comments = crud.get_all_comments_by_owner(owner_id)

    return templates.TemplateResponse("owner-comments.html", {
        "request": request,
        "comments": comments
    })


@router.post("/comments/{comment_id}/delete")
async def delete_comment(comment_id: int):
    deleted = crud.delete_comment_by_id(comment_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Yorum silinemedi")
    return RedirectResponse(url="/owner/comments", status_code=303)


@router.get("/income-report", response_class=HTMLResponse)
async def income_report(request: Request):
    owner_id = request.session.get("user_id")
    if not owner_id:
        raise HTTPException(status_code=403, detail="Giriş yapmanız gerekiyor.")

    summary = crud.get_income_summary(owner_id)
    history = crud.get_monthly_income_history(owner_id)

    return templates.TemplateResponse("owner-income-report.html", {
        "request": request,
        "summary": summary,
        "history": history
    })


@router.get("/reservations", response_class=HTMLResponse)
async def owner_reservations(request: Request):
    owner_id = request.session.get("user_id")
    if not owner_id:
        raise HTTPException(status_code=403, detail="Giriş yapmanız gerekiyor.")

    reservations = crud.get_owner_reservations(owner_id)

    return templates.TemplateResponse("owner-reservations.html", {
        "request": request,
        "reservations": reservations
    })


@router.get("/reservation-requests", response_class=HTMLResponse)
async def owner_reservation_requests(request: Request):
    owner_id = request.session.get("user_id")
    if not owner_id:
        raise HTTPException(status_code=403, detail="Giriş yapmanız gerekiyor.")

    reservations = crud.get_pending_reservations_by_owner(owner_id)

    return templates.TemplateResponse("owner-reservation-requests.html", {
        "request": request,
        "reservations": reservations
    })


@router.post("/reservations/{reservation_id}/approve")
async def approve_reservation(reservation_id: int):
    # 1️⃣ Confirm yap
    cursor = crud.cursor
    cursor.execute("""
        UPDATE tblReservation
        SET ReservationStatus = 'Confirmed'
        WHERE ReservationId = ?
    """, (reservation_id,))
    crud.db.commit()

    # 2️⃣ Payment oluştur
    cursor.execute("""
        SELECT h.Price, r.StartDate, r.EndDate
        FROM tblReservation r
        JOIN tblHouse h ON r.HouseId = h.HouseId
        WHERE r.ReservationId = ?
    """, (reservation_id,))
    row = cursor.fetchone()
    price = row.Price
    nights = (row.EndDate - row.StartDate).days
    nights = max(nights, 1)
    amount = price * nights

    crud.add_payment(reservation_id, amount)

    return RedirectResponse(url="/owner/reservations", status_code=303)


@router.post("/reservations/{reservation_id}/reject")
async def reject_reservation(reservation_id: int):
    cursor = crud.cursor
    cursor.execute("""
        UPDATE tblReservation
        SET ReservationStatus = 'Rejected'
        WHERE ReservationId = ?
    """, (reservation_id,))
    crud.db.commit()

    return RedirectResponse(url="/owner/reservations", status_code=303)




