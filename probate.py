import time
from urllib.request import urlopen
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def accept_condition(driver):
    button = driver.find_element(By.ID, "btnButton")
    button.submit()


# loop throught all options and click on desired text
def select(selection):
    all_options = driver.find_elements(By.CSS_SELECTOR, ".t-item")
    for option in all_options:
        if option.text == selection:
            option.click()
            break


# currently set to last month, but can also be modified to start - end date
def change_date(driver):
    dropdown_box = driver.find_element(By.ID, "DateRangeDropDown")
    dropdown = dropdown_box.find_element(By.CSS_SELECTOR, ".t-arrow-down")
    dropdown.click()

    selection = "Last Month"
    select(selection)

def change_doc_type(driver, selection):
    dropdown = driver.find_element(By.CSS_SELECTOR, ".t-select")
    dropdown.click()
    select(selection)
    dropdown.submit()
    

options = webdriver.ChromeOptions()
options.add_experimental_option("excludeSwitches", ["enable-logging"])

link = "https://officialrecords.mypinellasclerk.org/search/SearchTypeDocType"

driver = webdriver.Chrome()
driver.get(link)

accept_condition(driver)

change_date(driver)
change_doc_type(driver, selection = "PROBATE DOCUMENT")

try:
    element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "btnCsvButton"))
    ).click()
except:
    print("CSV FILE WAS NOT ABLE TO BE DOWNLOADED")

time.sleep(50000)
driver.quit()