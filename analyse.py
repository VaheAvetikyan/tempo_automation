import numpy as np
import pandas as pd


def main():
    agency_credit_log = '_FOLDER_UPLOAD/agencycreditlog_TEMPOFRNICE_2021-05-01_2021-06-2.csv'
    remit_one = '_FOLDER_UPLOAD/Report_June2021.csv'
    credit_log = pd.read_csv(agency_credit_log,
                             sep=',',
                             header=0,
                             parse_dates=True,
                             skip_blank_lines=True
                             )

    remit_one = pd.read_csv(remit_one,
                            sep=',',
                            header=0,
                            parse_dates=True,
                            skip_blank_lines=True
                            )

    credit_log['Reference'] = np.where(credit_log.Notes.str[-16:-13].isin(['TEA', 'TEC']), credit_log.Notes.str[-16:],
                                       "")
    print(credit_log['Reference'])

    credit_log['Custom Notes'] = np.where(
        credit_log['Notes'].str.contains("(?i)depot"), 'Depot',
        np.where(
            credit_log['Notes'].str.contains("(?i)payment"), 'Paid',
            np.where(
                credit_log['Notes'].str.contains("(?i)refund"), 'Refund',
                np.where(
                    credit_log['Notes'].str.contains("(?i)fermeture|ouverture"), 'Account Balances',
                    np.where(
                        credit_log['Notes'].str.contains("(?i)alimentation"), 'Alimentation',
                        credit_log['Notes'])))))

    depots = credit_log[credit_log['Custom Notes'].str.contains("(?i)Depot")]
    depot_credit_log = depots['Credit Added/Deducted'].sum()
    print(depot_credit_log)
    print(credit_log.head())
    print(remit_one.head())

    # cl = pd.merge(left=credit_log, right=remit_one[['status', 'remitt_pay_sett']], left_on='Referance', right_on='trans_ref')
    # print(cl)


if __name__ == "__main__":
    main()
