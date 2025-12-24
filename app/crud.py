from app.database import cursor, db


def get_all():
    cursor.execute("SELECT * FROM tblUser")
    columns = [column[0] for column in cursor.description]
    results = []
    for row in cursor.fetchall():
        results.append(dict(zip(columns, row)))
    return results

def get_active_user_count():
    cursor.execute("EXEC sp_GetActiveUserCount")
    return cursor.fetchone()[0]

def get_active_reservations():
    cursor.execute("SELECT COUNT(*) FROM tblReservation WHERE ReservationStatus = 'Confirmed'")
    return cursor.fetchone()[0]

def get_monthly_income():
    cursor.execute("SELECT SUM(Amount) FROM tblPayment WHERE PaymentStatus = 'Successful' AND MONTH(PaymentDate) = MONTH(GETDATE()) AND YEAR(PaymentDate) = YEAR(GETDATE())")
    result = cursor.fetchone()[0]
    return result if result is not None else 0

def check_user(email:str, password:str):
    try:
        cursor.execute("SELECT UserId,UserName,Email,UserRoleLevel FROM tblUser WHERE email = ? AND password = ?",(email.strip(),password.strip()))
        user = cursor.fetchone()

        if user:
            columns = [column[0] for column in cursor.description]
            return dict(zip(columns,user))
        return None
    except Exception as e:
        print("Giriş hatası: ",e)

def get_user_by_id(user_id:int):
    cursor.execute("SELECT * FROM tblUser WHERE UserId = ?", (user_id,))
    row = cursor.fetchone()
    if row:
        columns = [column[0] for column in cursor.description]
        return dict(zip(columns, row))
    return None

def get_reservations_by_user(user_id: int):
    cursor.execute("""
        SELECT r.ReservationId, r.StartDate, r.EndDate, h.HouseDescription, h.HouseLocation
        FROM tblReservation r
        JOIN tblHouse h ON r.HouseId = h.HouseId
        WHERE r.TenantId = ?
        ORDER BY r.StartDate DESC
    """, (user_id,))

    columns = [column[0] for column in cursor.description]
    results = [dict(zip(columns, row)) for row in cursor.fetchall()]
    return results

def new_user(name,password,email,phone,address,role):
    try:
        cursor.execute("SELECT COUNT(*) FROM tblUser WHERE Email = ?",(email,))

        if cursor.fetchone()[0]>0:
            print("Bu email zaten kayıtlı!")
            return False

        cursor.execute("INSERT INTO tblUser (UserName,Password,Email,PhoneNumber,Address ,UserRoleLevel) VALUES (?,?,?,?,?,?)",(name,password,email,phone,address,role))
        db.commit()
        print("Yeni kullanıcı kaydedildi.")
        return True
    except Exception as e:
        print("Kayıt hatası: ",e)
        return False

def search_users(query : str):
    search_query = f"%{query}%"
    cursor.execute("SELECT * FROM tblUser WHERE UserName LIKE ? OR Email LIKE ?",(search_query,search_query))
    columns = [column[0] for column in cursor.description]
    result = [dict(zip(columns,row)) for row in cursor.fetchall()]
    return result

def get_recent_users():
    cursor.execute("SELECT TOP 5 * FROM tblUser ORDER BY CreateDate DESC")
    columns = [column[0] for column in cursor.description]
    results = []
    for row in cursor.fetchall():
        user = dict(zip(columns, row))
        user["CreateDateFormatted"] = user["CreateDate"].strftime('%d.%m.%Y') if user["CreateDate"] else "Tarih yok"
        results.append(user)
    return results

def get_recent_users_count():
    cursor.execute("""
        SELECT COUNT(*) FROM tblUser
        WHERE CreateDate >= DATEADD(DAY, -30, GETDATE())
    """)
    return cursor.fetchone()[0]


def get_recent_payments():
    cursor.execute("SELECT TOP 5 * FROM tblPayment WHERE PaymentStatus = 'Successful' ORDER BY PaymentDate DESC")
    columns = [column[0] for column in cursor.description]
    results = []
    for row in cursor.fetchall():
        payment = dict(zip(columns, row))
        payment["PaymentDateFormatted"] = payment["PaymentDate"].strftime('%d.%m.%Y') if payment["PaymentDate"] else "Tarih yok"
        results.append(payment)
    return results

def get_upcoming_reservations():
    cursor.execute("""
        SELECT TOP 5 r.StartDate, u.UserName, h.HouseDescription
        FROM tblReservation r
        JOIN tblUser u ON r.TenantId = u.UserId
        JOIN tblHouse h ON r.HouseId = h.HouseId
        WHERE r.StartDate >= GETDATE() AND r.ReservationStatus = 'Confirmed'
        ORDER BY r.StartDate ASC
    """)
    columns = [col[0] for col in cursor.description]
    results = []
    for row in cursor.fetchall():
        reservation = dict(zip(columns, row))
        reservation["StartDateFormatted"] = reservation["StartDate"].strftime('%d.%m.%Y') if reservation["StartDate"] else "Tarih yok"
        results.append(reservation)
    return results

def update_user_in_db(user_id: int, user_name: str, email: str, phone: str, address: str, role_level: int, is_active: bool):
    try:
        cursor.execute("""
            UPDATE tblUser
            SET UserName = ?, Email = ?, PhoneNumber = ?, Address = ?, UserRoleLevel = ?, IsAccountActive = ?
            WHERE UserId = ?
        """, (user_name, email, phone, address, role_level, int(is_active), user_id))
        db.commit()
        return True
    except Exception as e:
        print("Kullanıcı güncelleme hatası:", e)
        return False

def delete_user_by_id(user_id: int):
    try:
        cursor.execute("DELETE FROM tblUser WHERE UserId = ?",(user_id,))
        db.commit()
        return True
    except Exception as e:
        print("Silme hatası: ", e)
        return False

def get_listings_by_owner(owner_id: int):
    query = ("""
        SELECT HouseId, HouseDescription, Price, IsHouseActive
        FROM tblHouse
        WHERE UserId = ?
    """)
    with db.cursor() as cursor:
        cursor.execute(query, (owner_id,))
        rows = cursor.fetchall()
        listings = []
        for row in rows:
            listings.append({
                "HouseId": row.HouseId,
                "HouseDescription": row.HouseDescription,
                "Price": row.Price,
                "IsHouseActive": row.IsHouseActive
            })
        return listings

def update_house_active_status(house_id:int, is_active:bool):
    result = cursor.execute("UPDATE tblHouse SET IsHouseActive = ? WHERE HouseId = ?",(1 if is_active else 0,house_id))


def owner_average_star(owner_id:int):
    cursor.execute("""
            SELECT AVG(dbo.fn_GetHouseAverageStar(HouseId))
            FROM tblHouse
            WHERE UserId = ?
        """, (owner_id,))
    result = cursor.fetchone()[0]
    return round(result, 2) if result is not None else 0

def create_new_listing(user_id, location, price, description, avg_star, is_available, is_active):
    query = """
        INSERT INTO tblHouse (UserId, HouseLocation, Price, HouseDescription, HouseAvgStar, IsAvailable, IsHouseActive)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    cursor.execute(query, [user_id, location, price, description, avg_star, is_available, is_active])
    db.commit()

def get_house_by_id(house_id):
    cursor.execute("SELECT * FROM tblHouse WHERE HouseId = ?", (house_id,))
    row = cursor.fetchone()
    if row:
        columns = [column[0] for column in cursor.description]
        return dict(zip(columns, row))
    return None

def update_house(house_id, location, price, description, is_available, is_active):
    query = """
        UPDATE tblHouse
        SET HouseLocation = ?, 
            Price = ?, 
            HouseDescription = ?, 
            IsAvailable = ?, 
            IsHouseActive = ?
        WHERE HouseId = ?
    """
    cursor.execute(query, (location, price, description, is_available, is_active, house_id))
    db.commit()

def delete_house_by_id(house_id, user_id):
    cursor.execute("DELETE FROM tblHouse WHERE HouseId = ? AND UserId = ?", (house_id, user_id))
    db.commit()

def get_owner_monthly_income(owner_id: int):
    cursor.execute("""
        SELECT SUM(p.Amount)
        FROM tblPayment p
        JOIN tblReservation r ON p.ReservationId = r.ReservationId
        JOIN tblHouse h ON r.HouseId = h.HouseId
        WHERE h.UserId = ? AND MONTH(p.PaymentDate) = MONTH(GETDATE()) AND YEAR(p.PaymentDate) = YEAR(GETDATE())
        AND p.PaymentStatus = 'Successful'
    """, (owner_id,))
    result = cursor.fetchone()[0]
    return result if result else 0

def get_owner_total_income(owner_id: int):
    cursor.execute("SELECT dbo.fn_GetOwnerTotalIncome(?)", (owner_id,))
    result = cursor.fetchone()[0]
    return result if result else 0

def get_recent_comments(owner_id: int):
    cursor.execute("""
        SELECT TOP 5 c.Content, c.Star, c.CreateDate
        FROM tblComment c
        JOIN tblHouse h ON c.HouseId = h.HouseId
        WHERE h.UserId = ?
        ORDER BY c.CreateDate DESC
    """, (owner_id,))
    rows = cursor.fetchall()
    columns = [column[0] for column in cursor.description]
    comments = []
    for row in rows:
        comment = dict(zip(columns, row))
        comment["Date"] = comment["CreateDate"].strftime("%d.%m.%Y") if comment["CreateDate"] else ""
        comments.append(comment)
    return comments

def get_all_comments_by_owner(owner_id:int):
    cursor.execute("""
        SELECT c.CommentId, c.Content, c.Star, c.CreateDate, h.HouseDescription
        FROM tblComment c
        JOIN tblHouse h ON c.HouseId = h.HouseId
        WHERE h.UserId = ?
        ORDER BY c.CreateDate DESC
    """,(owner_id,))

    columns = [column[0] for column in cursor.description]
    comments = []
    for row in cursor.fetchall():
        comment = dict(zip(columns, row))
        comment["Date"] = comment["CreateDate"].strftime('%d.%m.%Y') if comment["CreateDate"] else ""
        comments.append(comment)
    return comments


def delete_comment_by_id(comment_id: int):
    try:
        cursor.execute("DELETE FROM tblComment WHERE CommentId = ?", (comment_id,))
        db.commit()
        return True
    except Exception as e:
        print("Yorum silme hatası:", e)
        return False

def get_income_summary(owner_id: int):
    cursor.execute("""
        SELECT 
            SUM(CASE WHEN MONTH(PaymentDate) = MONTH(GETDATE()) AND YEAR(PaymentDate) = YEAR(GETDATE()) THEN p.Amount ELSE 0 END) AS ThisMonth,
            SUM(CASE WHEN MONTH(PaymentDate) = MONTH(DATEADD(MONTH, -1, GETDATE())) AND YEAR(PaymentDate) = YEAR(DATEADD(MONTH, -1, GETDATE())) THEN p.Amount ELSE 0 END) AS LastMonth,
            SUM(p.Amount) AS Total
        FROM tblPayment p
        JOIN tblReservation r ON p.ReservationId = r.ReservationId
        JOIN tblHouse h ON r.HouseId = h.HouseId
        WHERE h.UserId = ? AND p.PaymentStatus = 'Successful'
    """, (owner_id,))
    row = cursor.fetchone()
    return {
        "this_month": row[0] or 0,
        "last_month": row[1] or 0,
        "total": row[2] or 0
    }

def get_monthly_income_history(owner_id: int):
    cursor.execute("""
        SELECT 
            FORMAT(p.PaymentDate, 'yyyy-MM') AS Month,
            SUM(p.Amount) AS Total
        FROM tblPayment p
        JOIN tblReservation r ON p.ReservationId = r.ReservationId
        JOIN tblHouse h ON r.HouseId = h.HouseId
        WHERE h.UserId = ? AND p.PaymentStatus = 'Successful'
        GROUP BY FORMAT(p.PaymentDate, 'yyyy-MM')
        ORDER BY Month DESC
    """, (owner_id,))
    results = []
    for row in cursor.fetchall():
        results.append({"month": row[0], "total": float(row[1])})
    return results

def search_houses(query=None):
    if query:
        cursor.execute("""
            SELECT * FROM tblHouse
            WHERE IsHouseActive = 1 AND IsAvailable = 1
              AND (HouseLocation LIKE ? OR HouseDescription LIKE ?)
            ORDER BY HouseAvgStar DESC
        """, (f"%{query}%", f"%{query}%"))
    else:
        cursor.execute("""
            SELECT * FROM tblHouse
            WHERE IsHouseActive = 1 AND IsAvailable = 1
            ORDER BY HouseAvgStar DESC
        """)
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]

def add_reservation(tenant_id: int, house_id: int, start: str, end: str) -> int:
    try:
        cursor.execute("EXEC sp_AddReservation ?, ?, ?, ?", (tenant_id, house_id, start, end))
        reservation_id = cursor.fetchone()[0]
        return reservation_id
    except Exception as e:
        print("Rezervasyon ekleme hatası:", e)
        return -1

def add_payment(reservation_id: int, amount: float):
    try:
        query = """
            INSERT INTO tblPayment (ReservationId, Amount, PaymentDate, PaymentStatus, PaymentMethod)
            VALUES (?, ?, GETDATE(), 'Successful', 'Credit Card')
        """
        cursor.execute(query, (reservation_id, amount))
        db.commit()
    except Exception as e:
        print("Ödeme ekleme hatası:", e)

def is_reservation_conflict(house_id: int, start: str, end: str) -> bool:
    try:
        query = """
            SELECT COUNT(*) FROM tblReservation
            WHERE HouseId = ? AND ReservationStatus = 'Confirmed'
            AND (
                (StartDate <= ? AND EndDate >= ?) OR
                (StartDate <= ? AND EndDate >= ?) OR
                (StartDate >= ? AND EndDate <= ?)
            )
        """
        cursor.execute(query, (house_id, start, start, end, end, start, end))
        count = cursor.fetchone()[0]
        return count > 0
    except Exception as e:
        print("Çakışma kontrolü hatası:", e)
        return True

def get_reservations_by_tenant(tenant_id: int):
    cursor.execute("""
        SELECT r.ReservationId, r.StartDate, r.EndDate, r.ReservationStatus, 
               h.HouseId, h.HouseDescription, h.HouseLocation
        FROM tblReservation r
        JOIN tblHouse h ON r.HouseId = h.HouseId
        WHERE r.TenantId = ?
        ORDER BY r.StartDate DESC
    """, (tenant_id,))

    columns = [column[0] for column in cursor.description]
    results = [dict(zip(columns, row)) for row in cursor.fetchall()]
    return results

def add_comment(user_id: int, house_id: int, content: str, star: int):
    try:
        cursor.execute("""
            INSERT INTO tblComment (UserId, HouseId, Content, Star, CreateDate)
            VALUES (?, ?, ?, ?, GETDATE())
        """, (user_id, house_id, content, star))
        db.commit()
        return True
    except Exception as e:
        print("Yorum ekleme hatası:", e)
        return False

def get_pending_reservations_by_owner(owner_id: int):
    cursor.execute("""
        SELECT r.ReservationId, r.StartDate, r.EndDate, r.ReservationStatus,
               u.UserName AS TenantName, h.HouseDescription
        FROM tblReservation r
        JOIN tblHouse h ON r.HouseId = h.HouseId
        JOIN tblUser u ON r.TenantId = u.UserId
        WHERE h.UserId = ? AND r.ReservationStatus = 'Pending'
        ORDER BY r.StartDate ASC
    """, (owner_id,))

    columns = [column[0] for column in cursor.description]
    results = [dict(zip(columns, row)) for row in cursor.fetchall()]
    return results

def get_owner_reservations(owner_id: int):
    cursor.execute("""
        SELECT r.ReservationId, r.StartDate, r.EndDate, r.ReservationStatus,
               u.UserName AS TenantName, h.HouseDescription
        FROM tblReservation r
        JOIN tblHouse h ON r.HouseId = h.HouseId
        JOIN tblUser u ON r.TenantId = u.UserId
        WHERE h.UserId = ?
        ORDER BY r.StartDate DESC
    """, (owner_id,))

    columns = [column[0] for column in cursor.description]
    results = [dict(zip(columns, row)) for row in cursor.fetchall()]
    return results

def get_comments_by_tenant(tenant_id: int):
    cursor.execute("""
        SELECT c.CommentId, c.Content, c.Star, c.CreateDate, h.HouseDescription
        FROM tblComment c
        JOIN tblHouse h ON c.HouseId = h.HouseId
        WHERE c.UserId = ?
        ORDER BY c.CreateDate DESC
    """, (tenant_id,))

    columns = [column[0] for column in cursor.description]
    comments = []
    for row in cursor.fetchall():
        comment = dict(zip(columns, row))
        comment["Date"] = comment["CreateDate"].strftime('%d.%m.%Y') if comment["CreateDate"] else ""
        comments.append(comment)
    return comments

def get_popular_houses(limit=4):
    cursor.execute("""
        SELECT TOP (?) HouseId, HouseDescription, HouseLocation, Price, HouseAvgStar
        FROM tblHouse
        WHERE IsHouseActive = 1 AND IsAvailable = 1
        ORDER BY HouseAvgStar DESC
    """, (limit,))
    columns = [column[0] for column in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]

def get_recent_reservations_by_tenant(tenant_id: int, limit=3):
    cursor.execute("""
        SELECT TOP (?) r.ReservationId, r.StartDate, r.EndDate, r.ReservationStatus, 
               h.HouseDescription
        FROM tblReservation r
        JOIN tblHouse h ON r.HouseId = h.HouseId
        WHERE r.TenantId = ?
        ORDER BY r.StartDate DESC
    """, (limit, tenant_id))
    columns = [column[0] for column in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def get_all_reservations(status=None):
    query = """
        SELECT r.ReservationId, r.StartDate, r.EndDate, r.ReservationStatus,
               u.UserName AS TenantName, h.HouseDescription, o.UserName AS OwnerName
        FROM tblReservation r
        JOIN tblUser u ON r.TenantId = u.UserId
        JOIN tblHouse h ON r.HouseId = h.HouseId
        JOIN tblUser o ON h.UserId = o.UserId
    """
    params = []
    if status:
        query += " WHERE r.ReservationStatus = ?"
        params.append(status)

    query += " ORDER BY r.StartDate DESC"

    cursor.execute(query, params)
    columns = [column[0] for column in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def get_reservation_details(reservation_id: int):
    cursor.execute("""
        SELECT r.ReservationId, r.StartDate, r.EndDate, r.ReservationStatus,
               u.UserName AS TenantName, u.Email AS TenantEmail,
               h.HouseDescription, h.HouseLocation,
               o.UserName AS OwnerName, o.Email AS OwnerEmail
        FROM tblReservation r
        JOIN tblUser u ON r.TenantId = u.UserId
        JOIN tblHouse h ON r.HouseId = h.HouseId
        JOIN tblUser o ON h.UserId = o.UserId
        WHERE r.ReservationId = ?
    """, (reservation_id,))

    row = cursor.fetchone()
    if row:
        columns = [column[0] for column in cursor.description]
        return dict(zip(columns, row))
    return None

def delete_reservation(reservation_id: int):
    try:
        # Önce ödeme varsa sil
        cursor.execute("DELETE FROM tblPayment WHERE ReservationId = ?", (reservation_id,))
        # Sonra rezervasyon sil
        cursor.execute("DELETE FROM tblReservation WHERE ReservationId = ?", (reservation_id,))
        db.commit()
        return True
    except Exception as e:
        print("Rezervasyon silme hatası:", e)
        return False

def get_all_listings():
    cursor.execute("""
        SELECT h.HouseId, h.HouseDescription, h.HouseLocation, h.Price, h.IsHouseActive,
               u.UserName AS OwnerName
        FROM tblHouse h
        JOIN tblUser u ON h.UserId = u.UserId
        ORDER BY h.HouseId DESC
    """)
    columns = [column[0] for column in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]

def get_listing_details(house_id: int):
    cursor.execute("""
        SELECT h.HouseId, h.HouseDescription, h.HouseLocation, h.Price, h.IsHouseActive, h.IsAvailable, h.HouseAvgStar,
               u.UserName AS OwnerName, u.Email AS OwnerEmail
        FROM tblHouse h
        JOIN tblUser u ON h.UserId = u.UserId
        WHERE h.HouseId = ?
    """, (house_id,))

    row = cursor.fetchone()
    if row:
        columns = [column[0] for column in cursor.description]
        return dict(zip(columns, row))
    return None

def delete_listing(house_id: int):
    try:
        cursor.execute("DELETE FROM tblHouse WHERE HouseId = ?", (house_id,))
        db.commit()
        return True
    except Exception as e:
        print("İlan silme hatası:", e)
        return False

def get_all_payments(status=None):
    query = """
        SELECT p.PaymentId, p.Amount, p.PaymentDate, p.PaymentStatus, p.PaymentMethod,
               u.UserName AS TenantName, h.HouseDescription
        FROM tblPayment p
        JOIN tblReservation r ON p.ReservationId = r.ReservationId
        JOIN tblUser u ON r.TenantId = u.UserId
        JOIN tblHouse h ON r.HouseId = h.HouseId
    """
    params = []
    if status:
        query += " WHERE p.PaymentStatus = ?"
        params.append(status)

    query += " ORDER BY p.PaymentDate DESC"

    cursor.execute(query, params)
    columns = [column[0] for column in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]

def get_payment_details(payment_id: int):
    cursor.execute("""
        SELECT p.PaymentId, p.Amount, p.PaymentDate, p.PaymentStatus, p.PaymentMethod,
               u.UserName AS TenantName, u.Email AS TenantEmail,
               h.HouseDescription, h.HouseLocation
        FROM tblPayment p
        JOIN tblReservation r ON p.ReservationId = r.ReservationId
        JOIN tblUser u ON r.TenantId = u.UserId
        JOIN tblHouse h ON r.HouseId = h.HouseId
        WHERE p.PaymentId = ?
    """, (payment_id,))

    row = cursor.fetchone()
    if row:
        columns = [column[0] for column in cursor.description]
        return dict(zip(columns, row))
    return None

def get_total_users_count():
    cursor.execute("SELECT COUNT(*) FROM tblUser")
    return cursor.fetchone()[0]

def get_reservations_trend():
    cursor.execute("""
        SELECT FORMAT(StartDate, 'yyyy-MM') AS Month, COUNT(*) AS Count
        FROM tblReservation
        GROUP BY FORMAT(StartDate, 'yyyy-MM')
        ORDER BY Month ASC
    """)
    results = []
    for row in cursor.fetchall():
        results.append({"month": row[0], "count": row[1]})
    return results

def get_payments_trend():
    cursor.execute("""
        SELECT FORMAT(PaymentDate, 'yyyy-MM') AS Month, SUM(Amount) AS Total
        FROM tblPayment
        WHERE PaymentStatus = 'Successful'
        GROUP BY FORMAT(PaymentDate, 'yyyy-MM')
        ORDER BY Month ASC
    """)
    results = []
    for row in cursor.fetchall():
        results.append({"month": row[0], "total": float(row[1])})
    return results

def get_total_comments_count():
    cursor.execute("SELECT COUNT(*) FROM tblComment")
    return cursor.fetchone()[0]

