from flask import Flask, render_template
from datetime import datetime, timedelta


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


# Get days list
days = shift_days(START, END)

# Calculate the number of tables
if len(days) > MAX_COL:
    table_cnt = 2
    dates = [get_date_period_name(days[0], days[MAX_COL-1]), get_date_period_name(days[MAX_COL], days[-1])]
else:
    dates = get_date_period_name(days[0], days[-1])

# DEBUG
#print(days)
#print(shift_data)

@app.route('/')
def home():
    return render_template('index.html', data=shift_data, table_cnt = table_cnt, days = days, dates = dates, MAX_COL = MAX_COL)

if __name__ == '__main__':
    app.run(debug=True)
