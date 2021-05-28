from openpyxl import Workbook


def write_to_xlsx(output_rows):
    workbook = Workbook()
    worksheet = workbook.worksheets[0]
    for r, row in enumerate(output_rows, start=1):
        for c, col in enumerate(row, start=1):
            cell = worksheet.cell(row=r, column=c)
            cell.value = str(col)
    workbook.save('output.xlsx')
    return workbook
