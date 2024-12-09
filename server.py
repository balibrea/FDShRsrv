from flask import Flask, render_template
from datetime import datetime, timedelta

app = Flask(__name__)

START = "2024-11-20"
END = "2024-11-25"
MAX_COL = 9

table_cnt = 1

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

# Get days list
days = shift_days(START, END)

# Calculate the number of tables
if len(days) > MAX_COL:
    table_cnt = 2

# DEBUG
print(days)
print(shift_data)

@app.route('/')
def home():
    return render_template('index.html', data=shift_data, table_cnt = table_cnt, days = days)

if __name__ == '__main__':
    app.run(debug=True)