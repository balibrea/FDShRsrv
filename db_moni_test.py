import sqlite3
from datetime import datetime, timedelta

def shift_days(init_date, end_date):
    start = datetime.strptime(init_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")

    days = []

    now = start
    while now <= end:
        # Formatear la fecha y agregarla a la lista
        days.append(now.strftime("%Y-%m-%d"))
        # Avanzar un día
        now += timedelta(days=1)

    print(days)
    return days

def create_database():
    # Connect to SQLite database (or create it if it doesn't exist)
    conn = sqlite3.connect('fd_status.db')
    cursor = conn.cursor()

    # Create table for years
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS years (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            year INTEGER NOT NULL UNIQUE
        );
    ''')

    # Create table for months
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS months (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            year_id INTEGER NOT NULL,
            month INTEGER NOT NULL,
            FOREIGN KEY (year_id) REFERENCES years (id),
            UNIQUE(year_id, month)
        );
    ''')

    # Create table for days
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS days (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            month_id INTEGER NOT NULL,
            day INTEGER NOT NULL,
            FOREIGN KEY (month_id) REFERENCES months (id),
            UNIQUE(month_id, day)
        );
    ''')

    # Create table for FD statuses
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fd_statuses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            day_id INTEGER NOT NULL,
            fd_name TEXT NOT NULL,
            status TEXT NOT NULL,
            color TEXT NOT NULL,
            FOREIGN KEY (day_id) REFERENCES days (id),
            UNIQUE(day_id, fd_name)
        );
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS shifts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            start_year INTEGER NOT NULL,
            start_month INTEGER NOT NULL,
            start_day INTEGER NOT NULL,
            end_year INTEGER NOT NULL,
            end_month INTEGER NOT NULL,
            end_day INTEGER NOT NULL
        );
    ''')

    # Commit and close connection
    conn.commit()
    conn.close()
    print("Database and tables created successfully.")

def populate_database(dates, status=" ", color="green"):
    conn = sqlite3.connect('fd_status.db')
    cursor = conn.cursor()

    # Ensure years, months, and days are in the database
    for date in dates:
        month, day = map(int, date.split('-'))
        year = 2024 if month == 12 else 2025

        # Insert year
        cursor.execute('INSERT OR IGNORE INTO years (year) VALUES (?)', (year,))
        cursor.execute('SELECT id FROM years WHERE year = ?', (year,))
        year_id = cursor.fetchone()[0]

        # Insert month
        cursor.execute('INSERT OR IGNORE INTO months (year_id, month) VALUES (?, ?)', (year_id, month))
        cursor.execute('SELECT id FROM months WHERE year_id = ? AND month = ?', (year_id, month))
        month_id = cursor.fetchone()[0]

        # Insert day
        cursor.execute('INSERT OR IGNORE INTO days (month_id, day) VALUES (?, ?)', (month_id, day))
        cursor.execute('SELECT id FROM days WHERE month_id = ? AND day = ?', (month_id, day))
        day_id = cursor.fetchone()[0]

        # Insert FD statuses for all detectors
        for fd in ["LL", "LM", "LA", "CO", "HE"]:
            cursor.execute('''
                INSERT OR IGNORE INTO fd_statuses (day_id, fd_name, status, color)
                VALUES (?, ?, ?, ?)
            ''', (day_id, fd, status, color))

    # Commit changes
    conn.commit()
    conn.close()
    print("Database populated successfully.")

def add_shift(start_date, end_date):
    conn = sqlite3.connect('fd_status.db')
    cursor = conn.cursor()

    # Parse start and end dates
    start_year, start_month, start_day = map(int, start_date.split('-'))
    end_year, end_month, end_day = map(int, end_date.split('-'))

    # Insert shift data
    cursor.execute('''
        INSERT INTO shifts (start_year, start_month, start_day, end_year, end_month, end_day)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (start_year, start_month, start_day, end_year, end_month, end_day))

    # Commit and close connection
    conn.commit()
    conn.close()
    print(f"Shift from {start_date} to {end_date} added successfully.")


def create_new_shift(start_date, end_date, status=" ", color="green"):
    conn = sqlite3.connect('fd_status.db')
    cursor = conn.cursor()

    add_shift(start_date, end_date)

    dates = shift_days(start_date, end_date)

    # Ensure years, months, and days are in the database
    for date in dates:
        year, month, day = map(int, date.split('-'))


        # Insert year
        cursor.execute('INSERT OR IGNORE INTO years (year) VALUES (?)', (year,))
        cursor.execute('SELECT id FROM years WHERE year = ?', (year,))
        year_id = cursor.fetchone()[0]

        # Insert month
        cursor.execute('INSERT OR IGNORE INTO months (year_id, month) VALUES (?, ?)', (year_id, month))
        cursor.execute('SELECT id FROM months WHERE year_id = ? AND month = ?', (year_id, month))
        month_id = cursor.fetchone()[0]

        # Insert day
        cursor.execute('INSERT OR IGNORE INTO days (month_id, day) VALUES (?, ?)', (month_id, day))
        cursor.execute('SELECT id FROM days WHERE month_id = ? AND day = ?', (month_id, day))
        day_id = cursor.fetchone()[0]

        # Insert FD statuses for all detectors
        for fd in ["LL", "LM", "LA", "CO", "HE"]:
            cursor.execute('''
                INSERT OR IGNORE INTO fd_statuses (day_id, fd_name, status, color)
                VALUES (?, ?, ?, ?)
            ''', (day_id, fd, status, color))

    # Commit changes
    conn.commit()
    conn.close()
    print("Database populated successfully.")


if __name__ == "__main__":
    create_database()

    # Example list of dates
    '''
    dates = ['12-20', '12-21', '12-22', '12-23', '12-24', '12-25', '12-26', '12-27', '12-28', '12-29', '12-30', '12-31',
             '01-01', '01-02', '01-03', '01-04', '01-05', '01-06', '01-07']
             '''

    #populate_database(dates)

    # Create shifts periods, last day not added
    # ~ create_new_shift("2024-09-22", "2024-10-08")

    # ~ create_new_shift("2024-10-22", "2024-11-06")

    # ~ create_new_shift("2024-11-20", "2024-12-06")

    # ~ create_new_shift("2024-12-22", "2025-01-07")

    create_new_shift("2025-01-23", "2025-02-05")
