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

PAGE_WAIT = 3

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
def bad_name(driver):
    rows_info = driver.find_element(By.ID, "quickSearch_info")

    if (rows_info.text == ""): return True
    print(1, rows_info)
    print(2, rows_info.text == "")
    print(3, rows_info.get_attribute("id"))
    print(4, rows_info.get_attribute("innerHTML"))

    print(rows_info.text, rows_info.text.split("of "))
    R = int(rows_info.text.split("of ")[1].split()[0].replace(",", ""))
    
    print(R, rows_info.text)
    # person inherited no properties
    print(R)
    if R == 0:
        print("RETUREND!")
        return True

    return False
    
    # bad_name = ["LLC", "INC", "CORP", "COMPANY", "AND", "TRUST", "TRUSTEE", "ASSOCIATION", "AMERICA", "BANK", "ASSOCIATES", "STUDIO", "CLUB", "ROOFING", "UNION", "DEPARTMENT", "&", "CITY"]
    # for part in self.name.split():
    #     if part in bad_name or re.match("[0-9]", part):
    #         return False
    # return True


def search_person(driver, name):
    text_box = driver.find_element(By.ID, "txtKeyWord")
    text_box.clear()
    text_box.send_keys(name)
    text_box.send_keys(Keys.ENTER)

    time.sleep(PAGE_WAIT)


def get_property_data(driver):
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

    print(site_city_state_zip)
    site_city, site_state_zip = site_city_state_zip.split(", ")

    site_state_zip = site_state_zip.split()
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
    links = [row.find_element(By.CSS_SELECTOR, "a").get_attribute("href") for row in tRows]

    # loop through each property in the table
    for link in links:
        driver.get(link)

        property = get_property_data(driver)
        properties.append(property)

        print("we back")
        time.sleep(PAGE_WAIT)

    return properties
        

def setup():
    options = webdriver.ChromeOptions()
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    driver = webdriver.Chrome()
    return driver

def main():
    # setup webdriver
    search_page = "https://www.pcpao.gov/quick-search?qu=1&input=GANTT%20CANDACE&search_option=owner"
    driver = setup()
    driver.get(search_page)

    # grab file of names
    list_of_files = glob.glob("C:/Users/06141\Downloads/*Names*.csv")
    latest_file = max(list_of_files, key=os.path.getctime)

    on, stop = 0, 18

    # loop through each name and grab their information
    df = pd.read_csv(latest_file)
    for name in df["Liens Names"]:
        on+= 1
        print(name, on)
        if on < stop:
            continue
        
        print("passed")
        search_person(driver, name)


        if bad_name(driver):
            continue

        properties = find_properties(driver)


        print(properties, properties == None)

        if properties == None:
            # go back to search page
            continue
        
        # read each property into excel

        driver.get(search_page)

    time.sleep(10)
    driver.quit()


if __name__ == "__main__":
    main()