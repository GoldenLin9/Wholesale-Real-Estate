from public_records.get_CSV import *
import time

driver = setup()
change_date(driver, selection = "Last Month")
change_doc_type(driver, selection = "PROBATE DOCUMENT")
download_CSV(driver)

time.sleep(10)
driver.quit()