import os
import zipfile

from flask import Flask, render_template, request, Response, send_file, redirect, url_for, flash
import logging
from datetime import datetime

from files.file import get_mail_folders, download_file
from rates.rate import get_rates

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY')
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
    mailbox = request.form.get('mailbox')
    subject = request.form.get('subject')
    if not rate:
        flash('No rate is provided. Please provide a rate')
        return redirect(url_for('rates'))
    rate = float(rate)
    get_rates(rate, mailbox, subject)
    filename = 'rates/output.xlsx'
    app.logger.info("Getting Rates execution took %s s", (datetime.now() - start_time).total_seconds())
    return send_file(filename, mimetype='application/vnd.ms-excel')


@app.route('/files')
def files():
    folders = get_mail_folders()
    file_formats = [".csv", ".xml", ".pdf"]
    return render_template('files.html', folders=folders, file_formats=file_formats)


@app.route('/files/download', methods=['POST'])
def download():
    mailbox = request.form.get('mailbox')
    file_format = request.form.get('format')
    one_file = request.form.get('one') == "yes"
    quantity = int(request.form.get('quantity'))
    filenames = download_file(mailbox, file_format, one_file, quantity)
    if len(filenames) > 1:
        zipf = zipfile.ZipFile('tempo/out.zip', 'w', zipfile.ZIP_DEFLATED)
        for file in filenames:
            zipf.write(file)
        zipf.close()
        return send_file('out.zip',
                         mimetype='zip',
                         attachment_filename='out.zip',
                         as_attachment=True)
    else:
        return send_file(filenames[0], mimetype='application/file_format')


if __name__ == '__main__':
    app.run()
