from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    # Example shift data for detectors with consistent lengths  
    shift_data = {
        'LL': [("OK", "green"), ("OK", "green"), ("OK", "green"), ("OK", "green")],
        'LM': [("OK", "green"), ("ok", "red"), ("as", "yellow"), ("ok", "green")],
        'LA': [("OK", "green"), ("OK", "green"), ("OK", "green"), ("ok", "red")],
        'CO': [("OK", "green"), ("ok", "red"), ("as", "yellow"), ("ok", "green")],
        'HE': [("OK", "green"), ("OK", "green"), ("OK", "green"), ("as", "yellow")],
    }

    col_names = [f"10-{i+1}" for i in range(len(shift_data['LL']))]  # Create column names dynamically  
    x = 3  # Maximum number of columns per table  
    c = (len(col_names) + x - 1) // x  # Calculate number of tables needed

    return render_template('index_test.html', shift_data=shift_data, col_names=col_names, num_tables=c, x=x)

if __name__ == '__main__':
    app.run(debug=True)