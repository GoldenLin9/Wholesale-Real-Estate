import glob
import os
import pandas as pd

import time
from urllib.request import urlopen

import regex as re

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class Property:

    def __init__(self, first, last, mail_address, mail_city, mail_state, mail_zip, property_address, property_city, property_state, property_zip):
        self.first = first
        self.last = last
        self.mail_address = mail_address
        self.mail_city = mail_city
        self.mail_state = mail_state
        self.mail_zip = mail_zip
        self.property_address = property_address
        self.property_city = property_city
        self.property_state = property_state
        self.property_zip = property_zip


# operating under the assumption that (entries < 10)
def check_name(self):
    bad_name = ["LLC", "INC", "CORP", "COMPANY", "AND", "TRUST", "TRUSTEE", "ASSOCIATION", "AMERICA", "BANK", "ASSOCIATES", "STUDIO", "CLUB", "ROOFING", "UNION", "DEPARTMENT", "&", "CITY"]
    for part in self.name.split():
        if part in bad_name or re.match("[0-9]", part):
            return False
    return True


def search_person(driver, name):
    owner_button = driver.find_element(By.XPATH, "//input[@value = 'owner']")
    owner_button.click()

    text_box = driver.find_element(By.ID, "txtSearchProperty-selectized")
    text_box.clear()
    text_box.send_keys(name)

    search_btn = driver.find_element(By.ID, "btnHomeQuickSearch")
    search_btn.click()


def get_property_data(driver):
    time.sleep(1)
    mail_address_elem = driver.find_element(By.ID, "mailling_add")
    mail_address = mail_address_elem.text
    print(mail_address)

    mail = mail_address.split("\n")
    print(mail)

    mail_city, mail = mail[1].split(", ")
    mail_state, mail_zip = mail.split(" ")
    print(mail_city, mail_state, mail_zip)

    site_address_elem = driver.find_element(By.ID, "site_address")
    site_address = site_address_elem.text
    print(site_address)

    site_city_state_zip = site_address.split("\n")[1]

    site_city, site_state_zip = site_city_state_zip.split(" ")

    site_state = site_state_zip[0]
    site_zip = site_state_zip[1]

    print(site_state, site_zip)

    # also third owner ?
    owners = driver.find_element(By.ID, "first_second_owner")
    first_second_owner = owners.text
    print(first_second_owner)

    first_owner = first_second_owner.split("\n")[0]

    print(first_owner)

    first_owner_last_name, first_owner_first_name = first_owner.split(", ")

    print(first_owner_last_name, first_owner_first_name)

    return Property(first_owner_first_name, first_owner_last_name, mail_address, mail_city, mail_state, mail_zip, site_address, site_city, site_state, site_zip)


# return None for no properties or a list of properties
def find_properties(driver):
    properties = []
    tBody = driver.find_element(By.CSS_SELECTOR, "tBody")
    tRows = tBody.find_elements(By.CSS_SELECTOR, "tr")

    # person inherited no properties
    if len(tRows) == 0:
        return None
    

    # loop through each property in the table
    for row in tRows:
        page_link = row.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
        driver.get(page_link)

        property = get_property_data(driver)
        properties.append(property)

        driver.navigate().back()

    return properties
        

def setup():
    options = webdriver.ChromeOptions()
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    driver = webdriver.Chrome()
    return driver

def main():
    # setup webdriver
    search_page = "https://www.pcpao.gov/"
    driver = setup()
    driver.get(search_page)

    # grab file of names
    list_of_files = glob.glob("C:/Users/06141\Downloads/*Names*.csv")
    latest_file = max(list_of_files, key=os.path.getctime)

    # loop through each name and grab their information
    df = pd.read_csv(latest_file)
    for name in df["Liens Names"]:
        # if not person.check():
        #     continue

        search_person(driver, name)
        properties = find_properties(driver)

        if properties == None:
            continue

        # read each property into excel
        

    time.sleep(10)
    driver.quit()


if __name__ == "__main__":
    main()