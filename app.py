from flask import Flask, render_template, request, Response, send_file, redirect, url_for
import logging
from datetime import datetime
from rates.rate import get_rates

app = Flask(__name__)

app.logger.setLevel(logging.INFO)


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
    app.logger.info("Execution took %s s", (datetime.now() - start_time).total_seconds())
    return send_file(filename, mimetype='application/vnd.ms-excel')


if __name__ == '__main__':
    app.run()
