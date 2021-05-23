import schedule
import time

from rates.rate import get_rates

schedule.every().day.at("10:30").do(get_rates)

while True:
    schedule.run_pending()
    time.sleep(1)
