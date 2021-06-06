import numpy as np
import pandas as pd

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

    cl['Reference'] = np.where(cl['Notes'].str[-16:-13].isin(['TEA', 'TEC']),
                               cl['Notes'].str[-16:],
                               "")

    cl['Custom Notes'] = np.where(
        cl['Notes'].str.contains("(?i)depot"), 'Depot',
        np.where(
            cl['Notes'].str.contains("(?i)payment"), 'Paid',
            np.where(
                cl['Notes'].str.contains("(?i)refund"), 'Refund',
                np.where(
                    cl['Notes'].str.contains("(?i)fermeture|ouverture"), 'Account Balances',
                    np.where(
                        cl['Notes'].str.contains("(?i)alimentation"), 'Alimentation',
                        cl['Notes'])))))

    credit_log = cl.merge(ro[['status', 'remitt_pay_sett']],
                          left_on='Reference',
                          right_on=ro['trans_ref'],
                          how='left')

    remit_one = ro.merge(cl[['Custom Notes', 'Credit Added/Deducted']],
                         left_on='trans_ref',
                         right_on=cl['Reference'],
                         how='left')

    depots = credit_log[credit_log['Custom Notes'] == "Depot"]
    paid = credit_log[credit_log['Custom Notes'] == "Paid"]
    refunds = credit_log[credit_log['Custom Notes'] == "Refund"]
    refunds_included_period = credit_log[(credit_log['status'].str.contains("(?i)DELETED", na=False)) &
                                         (credit_log['Custom Notes'] == "Refund")]

    depot_credit_log = depots['Credit Added/Deducted'].sum()
    paid_credit_log = paid['Credit Added/Deducted'].sum()
    refund_credit_log = refunds['Credit Added/Deducted'].sum()
    refunds_included_period_credit_log = refunds_included_period['Credit Added/Deducted'].sum()

    remit_one = remit_one[remit_one['agent_name'] == agent_code]
    remit_one_cash = remit_one[remit_one['payment_type'] == 'CASH']
    processed = remit_one_cash[remit_one_cash['status'] == "PROCESSED"]
    deleted = remit_one_cash[remit_one_cash['status'] == "DELETED"]
    sent_for_pay = remit_one_cash[remit_one_cash['status'] == "SENT_FOR_PAY"]
    hq_ok_paid = remit_one_cash[remit_one_cash['status'] == "HQ_OK_PAID"]
    error = remit_one_cash[remit_one_cash['status'] == "ERROR"]

    processed_remit_one_cash = processed['remitt_pay_sett'].sum()
    deleted_remit_one_cash = deleted['remitt_pay_sett'].sum()
    sent_for_pay_remit_one_cash = sent_for_pay['remitt_pay_sett'].sum()
    hq_ok_paid_remit_one_cash = hq_ok_paid['remitt_pay_sett'].sum()
    error_remit_one_cash = error['remitt_pay_sett'].sum()

    s_data = [['Depot (Credit Log)', depot_credit_log],
              ['Paid (Credit Log)', paid_credit_log],
              ['Refunds (Credit Log)', refund_credit_log],
              ['Refunds for the included period (Credit Log)', refunds_included_period_credit_log],
              ['Refunds from non included period (Credit Log)', refund_credit_log - refunds_included_period_credit_log],
              ['PROCESSED (R1 paid by cash)', processed_remit_one_cash],
              ['DELETED (R1 paid by cash)', deleted_remit_one_cash],
              ['SENT_FOR_PAY (R1 paid by cash)', sent_for_pay_remit_one_cash],
              ['HQ_OK_PAID (R1 paid by cash)', hq_ok_paid_remit_one_cash],
              ['ERROR (R1 paid by cash)', error_remit_one_cash]]

    summary = pd.DataFrame(s_data, columns=['Credit Log vs R1 comparison', 'Balance'])

    filepath = make_filepath('_FOLDER_FILE', f'Safe {agent_code}.xlsx')
    writer = pd.ExcelWriter(filepath)
    summary.to_excel(writer, sheet_name='Summary', index=False)
    remit_one.to_excel(writer, sheet_name='RemitOne (R1)', index=False)
    credit_log.to_excel(writer, sheet_name='Credit Log (CL)', index=False)
    writer.save()
    return filepath, s_data
