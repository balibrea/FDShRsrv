from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    shift_data = {
        'LL':[("OK", "red"), ("ok", "red"),("as", "yellow")],
        'LM':[("OK", "green"), ("ok", "red"),("as", "yellow")],
        'LA':[("OK", "green"), ("ok", "red"),("as", "yellow")],
        'CO':[("OK", "green"), ("ok", "red"),("as", "yellow")],
        'HE':[("OK", "green"), ("ok", "red"),("asewe", "yellow")]
    }
    
    col_names = ["10-1", "10-2", "10-3"]
    
    return render_template('index_test.html', shift_data=shift_data, col_names=col_names, x = 1)

if __name__ == '__main__':
    app.run(debug=True)