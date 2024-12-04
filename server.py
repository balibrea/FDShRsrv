from flask import Flask, render_template
from datetime import datetime, timedelta

app = Flask(__name__)

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
    
    return days

print(shift_days("2024-11-20", "2024-12-7"))

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)