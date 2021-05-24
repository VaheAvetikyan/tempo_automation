from flask import Flask, render_template, request, Response, send_file, redirect, url_for
from datetime import datetime
from rates.rate import get_rates

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/rates')
def rates():
    return render_template('rates.html')


@app.route('/rates/calculate', methods=['POST'])
def calculate_rates():
    start_time = datetime.now()
    rate = request.form.get('rate')
    if not rate:
        return redirect(url_for('rates'))
    rate = float(rate)
    get_rates(rate)
    filename = 'rates/output.xlsx'
    end_time = datetime.now()
    time_diff = (end_time - start_time)
    execution_time = time_diff.total_seconds() * 1000
    print("Execution took", execution_time, " ms")
    return send_file(filename, mimetype='application/vnd.ms-excel')


if __name__ == '__main__':
    app.run()
