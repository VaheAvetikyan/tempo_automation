from flask import Flask, render_template, request, Response, send_file, redirect, url_for

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
    rate = request.form.get('rate')
    if not rate:
        return redirect(url_for('rates'))
    rate = float(rate)
    get_rates(rate)
    filename = 'rates/output.xlsx'
    return send_file(filename, mimetype='application/vnd.ms-excel')


if __name__ == '__main__':
    app.run()
