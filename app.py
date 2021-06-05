import os
import zipfile
import logging

from flask import Flask, render_template, request, send_file, redirect, url_for, flash
from datetime import datetime

from werkzeug.utils import secure_filename

from files.file import get_mail_folders, download_file
from rates.rate import get_rates_xlsx
from services.folders import make_filepath

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY')
app.logger.setLevel(logging.INFO)
app.config['FILE_FOLDER'] = '_FOLDER_FILE'
app.config['UPLOAD_FOLDER'] = '_FOLDER_UPLOAD'
app.config['UPLOAD_EXTENSIONS'] = ['csv', 'xlsx']


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
    get_rates_xlsx(rate, mailbox, subject)
    filepath = make_filepath(app.config['FILE_FOLDER'], 'output.xlsx')
    app.logger.info("Getting Rates execution took %s s", (datetime.now() - start_time).total_seconds())
    return send_file(filepath, mimetype='application/vnd.ms-excel')


@app.route('/files')
def files():
    folders = get_mail_folders()
    file_formats = [".csv", ".xml", ".pdf"]
    return render_template('files.html', folders=folders, file_formats=file_formats)


@app.route('/files/download', methods=['POST'])
def download():
    start_time = datetime.now()
    mailbox = request.form.get('mailbox')
    file_format = request.form.get('format')
    one_file = request.form.get('one') == "yes"
    quantity = int(request.form.get('quantity'))
    filenames = download_file(mailbox, file_format, one_file, quantity)
    if len(filenames) > 1:
        zipf = zipfile.ZipFile(app.config['FILE_FOLDER'] + '/out.zip', 'w', zipfile.ZIP_DEFLATED)
        for file in filenames:
            zipf.write(file)
            os.remove(file)
        zipf.close()
        app.logger.info("File download execution took %s s", (datetime.now() - start_time).total_seconds())
        return send_file(app.config['_FOLDER_FILE'] + '/out.zip',
                         mimetype='zip',
                         attachment_filename='out.zip',
                         as_attachment=True)
    else:
        app.logger.info("File download execution took %s s", (datetime.now() - start_time).total_seconds())
        return send_file(filenames[0], mimetype='application/' + file_format)


@app.route('/analyse')
def analyse():
    return render_template('analyse.html')


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        if not request.files:
            flash('No file part')
            return redirect(url_for('analyse'))
        credit_log = request.files['credit_log']
        remit_one = request.files['remit_one']
        if credit_log.filename == '' or remit_one.filename == '':
            flash('No selected file')
            return redirect(url_for('analyse'))
        if credit_log and allowed_file(credit_log.filename) and remit_one and allowed_file(remit_one.filename):
            credit_log_filename = secure_filename(credit_log.filename)
            remit_one_filename = secure_filename(remit_one.filename)
            credit_log.save(make_filepath(app.config['UPLOAD_FOLDER'], credit_log_filename))
            remit_one.save(make_filepath(app.config['UPLOAD_FOLDER'], remit_one_filename))
            flash('Files uploaded successfully')
            return redirect(url_for('analyse'))
    return redirect(url_for('analyse'))


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['UPLOAD_EXTENSIONS']


if __name__ == '__main__':
    app.run()
