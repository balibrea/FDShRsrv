import sqlite3

# Step 1: Create the SQLite database and table
def initialize_database():
    conn = sqlite3.connect("shifts.db")
    cursor = conn.cursor()

    # Create table for storing shift data
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS shifts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            detector_name TEXT NOT NULL,
            date TEXT NOT NULL,
            state TEXT NOT NULL,
            color TEXT NOT NULL
        )
    ''')

    conn.commit()
    conn.close()

# Step 2: Insert shift data into the database
def insert_shift_data(detector_shifts):
    conn = sqlite3.connect("shifts.db")
    cursor = conn.cursor()

    for detector, periods in detector_shifts.items():
        for date, (state, color) in periods:
            cursor.execute('''
                INSERT INTO shifts (detector_name, date, state, color)
                VALUES (?, ?, ?, ?)
            ''', (detector, date, state, color))

    conn.commit()
    conn.close()

# Step 3: Generate shift data based on your calendar
# Example: Define shift dates and populate the dictionary
shift_dates = ["12-20", "12-21", "12-22", "12-23", "12-24", "12-25", "12-26", "12-27", "12-28", "12-29", "12-30", "12-31", "01-01", "01-02", "01-03", "01-04", "01-05", "01-06", "01-07"]

def generate_shift_data():
    detectors = ["LL", "LM", "LA", "CO", "HE"]
    shift_data = {}

    for detector in detectors:
        shift_data[detector] = [(date, ("active", "yellow")) for date in shift_dates]

    return shift_data

# Step 4: Query data for display in the web app
def fetch_shift_data():
    conn = sqlite3.connect("shifts.db")
    cursor = conn.cursor()

    cursor.execute('''
        SELECT detector_name, date, state, color FROM shifts
        ORDER BY detector_name, date
    ''')

    rows = cursor.fetchall()
    conn.close()
    return rows

# Initialize the database and populate it
if __name__ == "__main__":
    initialize_database()
    shift_data = generate_shift_data()
    
    # Transform shift_data for insertion
    detector_shifts = {
        detector: [(date, data) for date, data in shift_data[detector]]
        for detector in shift_data
    }

    insert_shift_data(detector_shifts)

    # Fetch and print data to verify
    rows = fetch_shift_data()
    for row in rows:
        print(row)
