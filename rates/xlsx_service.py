from flask import current_app
from openpyxl import Workbook

from services.folders import make_filepath


def write_to_xlsx(output_rows):
    workbook = Workbook()
    worksheet = workbook.worksheets[0]
    for r, row in enumerate(output_rows, start=1):
        for c, col in enumerate(row, start=1):
            cell = worksheet.cell(row=r, column=c)
            cell.value = str(col)
    filepath = make_filepath(current_app.config['FILE_FOLDER'], 'output.xlsx')
    workbook.save(filepath)
    return workbook
