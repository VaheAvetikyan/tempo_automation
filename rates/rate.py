import re
from datetime import date

from services.email_service import text_parser
from rates.xlsx_service import write_to_xlsx

RATE_CONVENTION = {
    "MMTBRAUSD": ["BRASIL REALES MORE BRASIL", "BRL"],
    "MMTCHL": ["CHILE PESO CHILENO MORE CHILE", "CLP"],
    "MMTCOLPI": ["COLOMBIA PESO COLOMBIANO BANCO W", "COP"],
    "MMTHNDBR": ["HONDURAS LEMPIRA BANRURAL", "HNL"],
    "MMTMEXDT": ["MEXICO PESO MEXICANO DELGADO MEXICO", "MXN"],
    "MMTPRY": ["PARAGUAY GUARANI MORE PARAGUAY", "PYG"],
    "MMTPERIBE": ["PERU NUEVO SOL INTERBANK", "PEN"],
    "MMTDOMRD": ["REPUBLICA DOMINICANA PESO REP. DOMINICANA BHD", "DOP"],
    "MMTDOMBU": ["REPUBLICA DOMINICANA PESO REP. DOMINICANA BANCO UNION", "DOP"],
}


def get_rates_xlsx(xe_rate, mailbox, subject):
    output_rows = get_rates(xe_rate, mailbox, subject)
    return write_to_xlsx(output_rows)


def get_rates(xe_rate, mailbox, subject):
    today = date.today()
    input_data = text_parser(mailbox, subject, 5)
    input_dict = rates_to_dict(input_data)

    today = today.strftime("%Y-%m-%d")

    output_rows = []
    for k, v in RATE_CONVENTION.items():
        if v[0] in input_dict.keys():
            rate = float(input_dict[v[0]])
            output_rows.append([today, rate, k, "usd", "avahe", "", xe_rate, rate * xe_rate, v[1]])

    output_rows.append([today, "", "BTCBRA", "usd", "avahe", "", xe_rate, "", "BRL"])
    output_rows.append([today, "", "dexmar", "", "avahe", "", "", "", "MAD"])
    output_rows.append([today, "", "EARNGN", "", "", "", "", "", "NGN"])
    output_rows.append([today, "", "MTBPHL", "", "avahe", "", "", "", "PHP"])

    return output_rows


def rates_to_dict(input_data):
    input_data = input_data.splitlines()
    input_dict = {}
    for line in input_data:
        items = re.split(r'\s+(?=\d)|(?<=\d)\s+', line)
        if len(items) > 1:
            input_dict[items[0]] = items[1]
    return input_dict
