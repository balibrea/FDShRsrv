from flask import Flask, render_template, request, jsonify, redirect, url_for
from datetime import datetime, timedelta, date

from apscheduler.schedulers.background import BackgroundScheduler

import sqlite3

import os

import subprocess

app = Flask(__name__)

START = date(2025, 8, 14)
END = date(2025, 8, 31)

MAX_COL = 9

DB_FILE = 'fd_status.db'

INPUT_BASE = "/Raid/data/Prod/v2r0/Hybrid"
OUTPUT_DIR = "/home/auger/CurrentShift"

file_statuses = []

table_cnt = 1
dates = []

shift_data = {
    'LL':[],
    'LM':[],
    'LA':[],
    'CO':[],
    'HE':[]
}

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def shift_days(init_date, end_date):
    start = datetime.strptime(init_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")

    days = []

    now = start
    while now <= end:
        # Formatear la fecha y agregarla a la lista
        days.append(now.strftime("%m-%d"))
        # Avanzar un día
        now += timedelta(days=1)

        # Populate data (text, color)
        d = list(shift_data.keys())
        t = ("", "green")
        for i in range(5):
            shift_data[d[i]].append(t)

    return days


def shift_dates(init_date, end_date):
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


def get_date_period_name(start_date, end_date):
    # Month names for formatting
    month_names = [
        "", "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]

    # Split the input dates into month and day
    start_month, start_day = map(int, start_date.split('-'))
    end_month, end_day = map(int, end_date.split('-'))

    # Get the month names
    start_month_name = month_names[start_month]
    end_month_name = month_names[end_month]

    # Format the day suffixes
    def format_day_suffix(day):
        if day in [1, 21, 31]:
            return f"{day}st"
        elif day in [2, 22]:
            return f"{day}nd"
        elif day in [3, 23]:
            return f"{day}rd"
        else:
            return f"{day}th"

    # Construct the output
    if start_month == end_month:
        return f"{start_month_name} {format_day_suffix(start_day)} to {format_day_suffix(end_day)}"
    else:
        return f"{start_month_name} {format_day_suffix(start_day)} to {end_month_name} {format_day_suffix(end_day)}"


def fetch_shifts():
    conn = sqlite3.connect(DB_FILE) # Connect to the database
    cursor = conn.cursor()
    cursor.execute('SELECT start_year, start_month, start_day, end_year, end_month, end_day FROM shifts')
    shifts = cursor.fetchall()
    conn.close()
    # Format shifts into "YYYY-MM-DD to YYYY-MM-DD"
    shift_ranges = [
        f"{start_year:04d}-{start_month:02d}-{start_day:02d} to {end_year:04d}-{end_month:02d}-{end_day:02d}"
        for start_year, start_month, start_day, end_year, end_month, end_day in shifts
    ]
    return shift_ranges


def get_shift_data(selected_shift):
    # Parse the selected_shift string
    start_date_str, end_date_str = selected_shift.split(" to ")
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
    end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
    
    # Generate a list of all dates in the range
    date_list = [(start_date + timedelta(days=i)).strftime("%m-%d")
                 for i in range((end_date - start_date).days + 1)]

    # Connect to the database
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Prepare the shift_data dictionary
    shift_data = {fd: [] for fd in ['LL', 'LM', 'LA', 'CO', 'HE']}

    # Iterate over each date and fetch data
    current_date = start_date
    while current_date <= end_date:
        year = current_date.year
        month = current_date.month
        day = current_date.day

        # Get the day_id for the current date
        cursor.execute('''
            SELECT days.id
            FROM days
            JOIN months ON days.month_id = months.id
            JOIN years ON months.year_id = years.id
            WHERE years.year = ? AND months.month = ? AND days.day = ?
        ''', (year, month, day))
        day_id_result = cursor.fetchone()

        if day_id_result:
            day_id = day_id_result[0]

            # Fetch FD statuses for the current day
            cursor.execute('''
                SELECT fd_name, status, color
                FROM fd_statuses
                WHERE day_id = ?
            ''', (day_id,))
            fd_statuses = cursor.fetchall()

            # Populate shift_data for this day
            for fd_name, status, color in fd_statuses:
                if fd_name in shift_data:
                    shift_data[fd_name].append((status, color))

        # Move to the next day
        current_date += timedelta(days=1)

    # Close the database connection
    conn.close()

    return shift_data, date_list


def get_day_id_from_index(index, table_index):
    # Calculate the day offset based on the table index and column index
    day_offset = table_index * MAX_COL + index

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Query the days table to find the matching day_id
    cursor.execute('''
        SELECT id FROM days
        ORDER BY id LIMIT 1 OFFSET ?;
    ''', (day_offset,))
    result = cursor.fetchone()
    conn.close()

    if result:
        return result[0]
    else:
        raise ValueError(f"No matching day_id found for index {index} and table {table_index}")


# Get shifts list
shifts = fetch_shifts()

# Defaulft selected shift
selected_shift = len(shifts) -1 # last shift

# Get days list
#days = shift_days(START, END)
shift_data, days = get_shift_data(shifts[selected_shift])

def calculate_tables():
    global table_cnt
    global dates

    # Calculate the number of tables
    if len(days) > MAX_COL:
        table_cnt = 2
        dates = [get_date_period_name(days[0], days[MAX_COL-1]), get_date_period_name(days[MAX_COL], days[-1])]
    else:
        dates = get_date_period_name(days[0], days[-1])

calculate_tables()

# DEBUG
#print(shift_data)

#print(fetch_shifts())


#print("Shift Data:")
#for key, value in shift_data.items():
    #print(f"{key}: {value}")

#print("\nDate List:")
#print(days)

print(shifts)

def save_fd_data_to_db(selected_shift, fd_data):
    # Parse the selected shift
    start_date_str, end_date_str = selected_shift.split(" to ")
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
    end_date = datetime.strptime(end_date_str, "%Y-%m-%d")

    # Connect to SQLite database
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Function to insert or fetch year ID
    def get_or_create_year(year):
        cursor.execute('SELECT id FROM years WHERE year = ?', (year,))
        row = cursor.fetchone()
        if row:
            return row[0]
        cursor.execute('INSERT INTO years (year) VALUES (?)', (year,))
        return cursor.lastrowid

    # Function to insert or fetch month ID
    def get_or_create_month(year_id, month):
        cursor.execute('SELECT id FROM months WHERE year_id = ? AND month = ?', (year_id, month))
        row = cursor.fetchone()
        if row:
            return row[0]
        cursor.execute('INSERT INTO months (year_id, month) VALUES (?, ?)', (year_id, month))
        return cursor.lastrowid

    # Function to insert or fetch day ID
    def get_or_create_day(month_id, day):
        cursor.execute('SELECT id FROM days WHERE month_id = ? AND day = ?', (month_id, day))
        row = cursor.fetchone()
        if row:
            return row[0]
        cursor.execute('INSERT INTO days (month_id, day) VALUES (?, ?)', (month_id, day))
        return cursor.lastrowid

    # Iterate through each date in the selected shift range
    current_date = start_date
    while current_date <= end_date:
        year = current_date.year
        month = current_date.month
        day = current_date.day

        # Get or create the year, month, and day in the database
        year_id = get_or_create_year(year)
        month_id = get_or_create_month(year_id, month)
        day_id = get_or_create_day(month_id, day)

        # Insert FD data for this day
        for fd_name, statuses in fd_data.items():
            # Match the index of the current date to the corresponding status
            index = (current_date - start_date).days
            if index < len(statuses):  # Ensure we don't go out of bounds
                status, color = statuses[index]
                cursor.execute('''
                    INSERT OR REPLACE INTO fd_statuses (day_id, fd_name, status, color)
                    VALUES (?, ?, ?, ?)
                ''', (day_id, fd_name, status, color))

        current_date += timedelta(days=1)

    # Commit and close connection
    conn.commit()
    conn.close()


def add_shift(start_date, end_date):
    conn = sqlite3.connect(DB_FILE)
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
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    add_shift(start_date, end_date)

    dates = shift_dates(start_date, end_date)

    print(dates)

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


def delete_shift(start_date, end_date):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Delete the shift entry
    cursor.execute('''
        DELETE FROM shifts
        WHERE start_year = ? AND start_month = ? AND start_day = ?
          AND end_year = ? AND end_month = ? AND end_day = ?
    ''', (*map(int, start_date.split('-')), *map(int, end_date.split('-'))))

    # Get all dates in the shift
    dates = shift_dates(start_date, end_date)

    print(dates)

    for date in dates:
        year, month, day = map(int, date.split('-'))

        # Get year_id
        cursor.execute('SELECT id FROM years WHERE year = ?', (year,))
        year_row = cursor.fetchone()
        if not year_row:
            continue
        year_id = year_row[0]

        # Get month_id
        cursor.execute('SELECT id FROM months WHERE year_id = ? AND month = ?', (year_id, month))
        month_row = cursor.fetchone()
        if not month_row:
            continue
        month_id = month_row[0]

        # Get day_id
        cursor.execute('SELECT id FROM days WHERE month_id = ? AND day = ?', (month_id, day))
        day_row = cursor.fetchone()
        if not day_row:
            continue
        day_id = day_row[0]

        # Delete FD statuses for this day
        cursor.execute('DELETE FROM fd_statuses WHERE day_id = ?', (day_id,))
        # Delete the day entry
        cursor.execute('DELETE FROM days WHERE id = ?', (day_id,))

    # Optionally, clean up months and years with no days/months left
    cursor.execute('DELETE FROM months WHERE id NOT IN (SELECT month_id FROM days)')
    cursor.execute('DELETE FROM years WHERE id NOT IN (SELECT year_id FROM months)')

    conn.commit()
    conn.close()
    print(f"Shift from {start_date} to {end_date} deleted successfully.")


def list_shifts():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT start_year, start_month, start_day, end_year, end_month, end_day
        FROM shifts
        ORDER BY start_year, start_month, start_day
    ''')
    shifts = cursor.fetchall()
    conn.close()

    result = []
    for shift in shifts:
        start = f"{shift[0]:04d}-{shift[1]:02d}-{shift[2]:02d}"
        end = f"{shift[3]:04d}-{shift[4]:02d}-{shift[5]:02d}"
        result.append({"start": start, "end": end})
        #print(f"  {start} to {end}")
    return result

def run_reconstruction(date_str: str):
    """
    Runs the offline reconstruction script if userAugerOffline is not already running.
    date_str must be in format YYYY-MM-DD

    Launch reconstruction for a given date using a detached screen session.
    """
    try:
        # Check if userAugerOffline is already running
        result = subprocess.run(
            ["pgrep", "-x", "userAugerOffline"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        if result.returncode == 0:
            print("⚠️ userAugerOffline is already running. Skipping reconstruction.")
            return False
        
        # Run the reconstruction script
        # Call the bash script with the given date
        #result = subprocess.run(
        #    ["bash", "offlinereconstr.sh", date_str],
        #    capture_output=True,
        #    text=True,
        #    check=True
        #)
        #return result.stdout
    
        session_name = f"recon_{date_str.replace('-', '')}"

        # Check if screen session already exists
        check = subprocess.run(
            ["screen", "-list"],
            capture_output=True,
            text=True
        )

        if session_name in check.stdout:
            return f"Reconstruction already running in screen session: {session_name}"
        
        # Run the bash script inside a new detached screen
        cmd = [
            "screen", "-dmS", session_name,
            "bash", "-c", "./offlineHybRec.sh {date_str}"
        ]

        subprocess.run(cmd, check=True)

        return f"Started reconstruction in detached screen session: {session_name}"
    
    
    except subprocess.CalledProcessError as e:
        print("Error during reconstruction:", e.stderr)
        return None


def check_files(start=START, end=END):
    """Check source/output files between START_DATE and END_DATE."""
    global file_statuses
    file_statuses = []   # clear before refresh

    current_date = start
    while current_date <= end:
        year, month, day = current_date.strftime("%Y"), current_date.strftime("%m"), current_date.strftime("%d")

        input_file = f"{INPUT_BASE}/{year}/{month}/hd_{year}_{month}_{day}_12h00.root"
        output_file = f"{OUTPUT_DIR}/ADST_hyb_{year}_{month}_{day}.root"


        if os.path.exists(input_file):
            print(f"File {input_file} exists.")
            if os.path.exists(output_file):
                status = "ready"
                print(f"File {output_file} exists.")
            else:
                status = "source available, not processed"

                # Run reconstruction
                run_reconstruction("{year}-{month}-{day}")
                
                status = "source available, processing..."

                print(f"File {output_file} does not exist, processing...")
        else:
            status = "source not available"
            print(f"File {input_file} does not exist.")

        file_statuses.append({
            "date": current_date.isoformat(),
            "input": input_file,
            "output": output_file,
            "status": status,
            "last_checked": datetime.now().strftime("%Y-%m-%d %H:%M")
        })

        current_date += timedelta(days=1)

# Scheduler runs job every 2 hours
scheduler = BackgroundScheduler()
scheduler.add_job(func=check_files, trigger="interval", hours=2)
scheduler.start()


################################# Web Routes ######################################

@app.route('/', methods=['GET', 'POST'])
def home():
    global selected_shift
    global shift_data
    global days

    if request.method == 'POST':
        # Handle the selected value sent via AJAX
        selected_shift = request.json.get('selected_shift')
        print(f"################ Shift period: {selected_shift} #################")  # Use the value here

        shift_data, days = get_shift_data(shifts[selected_shift])
        calculate_tables()
        
        #return jsonify({"status": "success", "selected_shift": selected_shift})
        #return redirect(url_for('home'))
        # Return updated table data and days as JSON
        return jsonify({
            "status": "success",
            "shift_data": shift_data,
            "days": days
        }) 

    
    return render_template('index.html',
        data=shift_data,
        table_cnt = table_cnt, 
        days = days, 
        dates = dates, 
        MAX_COL = MAX_COL,
        shifts = shifts,
        selected_shift = selected_shift
    )


@app.route('/save-data', methods=['POST'])
def save_data():
    data = request.json
    print(data)  # Process or save the data as needed

    # Save the data to the database
    save_fd_data_to_db(shifts[selected_shift], data)

    #return jsonify({'message': 'Data saved successfully!', 'data': data})
    return jsonify({"status": "success"})


@app.route("/shifts", methods=["GET", "POST"])
def manage_shifts():
    if request.method == "POST":
        start_date = request.form["start_date"]
        end_date = request.form["end_date"]
        create_new_shift(start_date, end_date, color="green")
        return redirect(url_for("manage_shifts"))

    shifts = list_shifts()
    return render_template("shifts.html", shifts=shifts)


@app.route("/delete_shift", methods=["POST"])
def remove_shift():
    start_date = request.form["start_date"]
    end_date = request.form["end_date"]
    delete_shift(start_date, end_date)
    return redirect(url_for("manage_shifts"))


@app.route("/offline")
def show_files():
    print("Last shift in database:")
    #print(list_shifts()[-1])
    print(shifts[-1])
    s, e = shifts[-1].split(" to ")
    s_y, s_m, s_d = s.split("-")
    e_y, e_m, e_d = e.split("-")

    START = datetime(int(s_y), int(s_m), int(s_d))
    END = datetime(int(e_y), int(e_m), int(e_d))

    # Run once at startup
    check_files(START, END)
    #print(file_statuses)
    return render_template("offline_recon.html", rows=file_statuses)


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
