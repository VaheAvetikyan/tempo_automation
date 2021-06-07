import re

import numpy as np
import pandas as pd
from flask import current_app

from services.folders import make_filepath


def data_processor(agent_code, agency_credit_log, remit_one):
    cl = pd.read_csv(agency_credit_log,
                     sep=',',
                     header=0,
                     parse_dates=True,
                     skip_blank_lines=True
                     )

    ro = pd.read_csv(remit_one,
                     sep=',',
                     header=0,
                     parse_dates=True,
                     skip_blank_lines=True
                     )

    reference = re.compile('(TE[a-zA-Z0-9]{14})')
    cl['Reference'] = cl['Notes'].str.extract(reference)

    notes = cl['Notes'].str
    cl['Custom Notes'] = np.where(
        notes.contains("(?i)depot"), 'Depot',
        np.where(
            notes.contains("(?i)payment"), 'Paid',
            np.where(
                notes.contains("(?i)refund"), 'Refund',
                np.where(
                    notes.contains("(?i)fermeture|ouverture|ouvereture|Rapport caisse"), 'Account Balances',
                    np.where(
                        notes.contains("(?i)alimentation"), 'Alimentation',
                        np.where(
                            notes.contains("(?i)Correction"), 'Correction',
                            cl['Notes']))))))

    credit_log = cl.merge(ro[['status', 'remitt_pay_sett']],
                          left_on='Reference',
                          right_on=ro['trans_ref'],
                          how='left')

    credit_log['Balance check'] = abs(credit_log['Credit Added/Deducted']) - abs(credit_log['remitt_pay_sett'])

    remit_one = ro.merge(cl[['Custom Notes', 'Credit Added/Deducted']],
                         left_on='trans_ref',
                         right_on=cl['Reference'],
                         how='left')

    depot = credit_log[credit_log['Custom Notes'] == "Depot"].sum()['Credit Added/Deducted']
    paid = credit_log[credit_log['Custom Notes'] == "Paid"].sum()['Credit Added/Deducted']
    refund = credit_log[credit_log['Custom Notes'] == "Refund"].sum()['Credit Added/Deducted']
    refunds_included_period = credit_log[(credit_log['status'].str.contains("(?i)DELETED", na=False)) &
                                         (credit_log['Custom Notes'] == "Refund")
                                         ].sum()['Credit Added/Deducted']

    # Parse Dates
    credit_log['Date'] = pd.to_datetime(credit_log['Date'], format='%Y-%m-%d %H:%M:%S')
    remit_one['creation_date'] = remit_one['creation_date'].str[:-6]
    remit_one['creation_date'] = pd.to_datetime(remit_one['creation_date'], format='%Y-%m-%d %H:%M:%S')
    remit_one['processed_date'] = remit_one['processed_date'].str[:-6]
    remit_one['processed_date'] = pd.to_datetime(remit_one['processed_date'], format='%Y-%m-%d %H:%M:%S')
    remit_one['deleted_date'] = remit_one['deleted_date'].str[:-6]
    remit_one['deleted_date'] = pd.to_datetime(remit_one['deleted_date'], format='%Y-%m-%d %H:%M:%S')

    remit_one = remit_one[remit_one['agent_name'] == agent_code]
    remit_one_cash = remit_one[remit_one['payment_type'] == 'CASH']

    processed = remit_one_cash[remit_one_cash['status'] == "PROCESSED"].sum()['remitt_pay_sett']
    deleted = remit_one_cash[remit_one_cash['status'] == "DELETED"].sum()['remitt_pay_sett']
    sent_for_pay = remit_one_cash[remit_one_cash['status'] == "SENT_FOR_PAY"].sum()['remitt_pay_sett']
    hq_ok_paid = remit_one_cash[remit_one_cash['status'] == "HQ_OK_PAID"].sum()['remitt_pay_sett']
    error = remit_one_cash[remit_one_cash['status'] == "ERROR"].sum()['remitt_pay_sett']

    s_data = [['Depot (Credit Log)', depot],
              ['Paid (Credit Log)', paid],
              ['Refunds (Credit Log)', refund],
              ['Refunds for the included period (Credit Log)', refunds_included_period],
              ['Refunds from non included period (Credit Log)', refund - refunds_included_period],
              ['PROCESSED (R1 paid by cash)', processed],
              ['DELETED (R1 paid by cash)', deleted],
              ['SENT_FOR_PAY (R1 paid by cash)', sent_for_pay],
              ['HQ_OK_PAID (R1 paid by cash)', hq_ok_paid],
              ['ERROR (R1 paid by cash)', error]]

    summary = pd.DataFrame(s_data, columns=['Credit Log vs R1 comparison', 'Balance'])

    filepath = make_filepath(current_app.config['FILE_FOLDER'], f'Safe {agent_code}.xlsx')
    writer = pd.ExcelWriter(filepath)
    summary.to_excel(writer, sheet_name='Summary', index=False)
    remit_one.to_excel(writer, sheet_name='RemitOne (R1)', index=False)
    credit_log.to_excel(writer, sheet_name='Credit Log (CL)', index=False)
    writer.save()
    return filepath, s_data
