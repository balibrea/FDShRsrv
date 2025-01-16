from flask import Flask, render_template, request, jsonify, redirect, url_for
from datetime import datetime, timedelta

import sqlite3

app = Flask(__name__)

START = "2024-12-20"
END = "2025-01-7"
MAX_COL = 9

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
    conn = sqlite3.connect('fd_status.db')
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
    conn = sqlite3.connect('fd_status.db') # Connect to the database
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
    conn = sqlite3.connect('fd_status.db')
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

    conn = sqlite3.connect('fd_status.db')
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


@app.route('/save', methods=['POST'])
def save_data():
    try:
        # Retrieve the table data from the frontend
        table_data = request.json.get('tableData')

        print(table_data)

        # Open database connection
        conn = sqlite3.connect('fd_status.db')
        cursor = conn.cursor()

        # Process each entry in table data
        for entry in table_data:
            shift = entry['shift']
            statuses = entry['statuses']

            for i, status in enumerate(statuses):
                # Find the day_id based on the column index and shift period
                day_id = get_day_id_from_index(i, entry['tableIndex'])

                # Update or insert the fd_status record for the given day and FD name
                cursor.execute('''
                    INSERT INTO fd_statuses (day_id, fd_name, status, color)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(day_id, fd_name) DO UPDATE SET
                        status = excluded.status,
                        color = excluded.color;
                ''', (day_id, shift, status['text'], status['color']))

        # Commit the changes to the database
        conn.commit()
        conn.close()

        return jsonify({"status": "success"})
    except Exception as e:
        print("Error saving data:", e)
        return jsonify({"status": "error", "message": str(e)})



if __name__ == '__main__':
    app.run(debug=True)
