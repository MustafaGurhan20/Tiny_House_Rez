import pyodbc

try:
    db = pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=MEHMET\\MSSQLSERVER01;"
        "DATABASE=tinyhousedb;"
        "Trusted_Connection=yes;"
    )
    cursor = db.cursor()
    print("Bağlantı başarılı")

except Exception as e:
    print("Bağlantı hatası:",e)

