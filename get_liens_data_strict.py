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

PAGE_WAIT = 2.5

class Property:

    def __init__(self, first, last, mail_address, mail_city, mail_state, mail_zip, property_address, property_city, property_state, property_zip, second_owner, third_owner):
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
        self.second_owner = second_owner
        self.third_owner = third_owner

def corp(name):

    # we don't know if corp or not
    if name == None:
        return False
    
    bad_name = ["LLC", "TRE", "INC", "CORP", "COMPANY", "AND", "TRUST", "TRUSTEE", "ASSOCIATION", "AMERICA", "BANK", "ASSOCIATES", "STUDIO", "CLUB", "ROOFING", "UNION", "DEPARTMENT", "&", "CITY"]
    for part in name.split():
        fixed_part = part.replace(",", "")
        if fixed_part in bad_name or re.match("[0-9]", part):
            return True
        
    return False

# operating under the assumption that (entries < 10)
def bad_name(driver, name):
    rows_info = driver.find_element(By.ID, "quickSearch_info")

    if (rows_info.text == ""): return True

    R = int(rows_info.text.split("of ")[1].split()[0].replace(",", ""))
    
    # person inherited no properties
    if R == 0:
        return True

    if corp(name): return True
        
    return False


def search_person(driver, name):
    text_box = driver.find_element(By.ID, "txtKeyWord")

    last, first_middle = name.split(" ", 1)
    text_box.clear()
    text_box.send_keys(f"{last}, {first_middle}")
    text_box.send_keys(Keys.ENTER)

    time.sleep(PAGE_WAIT)


def get_property_data(driver):
    

    try:
        # check owner names
        first_second_owner = driver.find_element(By.ID, "first_second_owner").text
        third_owner = driver.find_element(By.ID, "third_owner").text

        third_owner = None if third_owner == "" else third_owner

        if "\n" in first_second_owner:
            first_owner, second_owner = first_second_owner.split("\n")
        else:
            first_owner, second_owner = first_second_owner, None

        first_second_owner.replace("\n", " ")
        print("owners: ", first_owner, "|", second_owner, "|", third_owner, "| res: ", (corp(first_owner) or corp(second_owner) or corp(third_owner)))
        if corp(first_owner) or corp(second_owner) or corp(third_owner):
            return None


        mail_address_elem = driver.find_element(By.ID, "mailling_add")
        mail_address = mail_address_elem.text

        
        mail = mail_address.split("\n")

        mail_city, mail = mail[1].split(", ")
        mail_state, mail_zip = mail.split(" ")

        site_address_elem = driver.find_element(By.ID, "site_address")
        site_address = site_address_elem.text

        site_city_state_zip = site_address.split("\n")[1]

        site_city, site_state_zip = site_city_state_zip.split(", ")

        site_state_zip = site_state_zip.split()
        site_state = site_state_zip[0]
        site_zip = site_state_zip[1]


        first_owner_last_name, first_owner_first_name = first_owner.split(", ")
    except:
        return None

    print("returned property")
    return Property(first_owner_first_name, first_owner_last_name, mail_address, mail_city, mail_state, mail_zip, site_address, site_city, site_state, site_zip, second_owner, third_owner)


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

        if property != None:
            properties.append(property)

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
    list_of_files = glob.glob("C:/Users/06141\Downloads/liensNames.csv")
    latest_file = max(list_of_files, key=os.path.getctime)
    print(latest_file)

    on, last_stop = 0, 1177

    indx = 0
    # loop through each name and grab their information

    df = pd.read_csv(latest_file)
    names = df["Liens Names"]
    for name in names:
        on+= 1

        print(f"on {on}: {name}, appended: {indx}")
        if on <= last_stop:
            continue
        
        search_person(driver, name)


        if bad_name(driver, name):
            continue

        properties = find_properties(driver)


        if properties == None:
            # go back to search page
            continue
        
        # read each property into excel
        for property in properties:
            data = {
                "Queried Name": name,
                "First Name": property.first,
                "Last Name": property.last,
                "Mail Address": property.mail_address,
                "Mail City": property.mail_city,
                "Mail State": property.mail_zip,
                "Property Address": property.property_address,
                "Property City": property.property_city,
                "Property State": property.property_state,
                "Property Zip": property.property_zip,
                "Second Owner": property.second_owner,
                "Third Owner": property.third_owner
            }

            df = pd.DataFrame(data, index = [indx])

            if indx == 0 and on == 0:
                df.to_csv("liens.csv", mode = "a", header = True, index = False)
            else:
                df.to_csv("liens.csv", mode = "a", header = False, index = False)


            indx+= 1

        driver.get(search_page)

    time.sleep(10)
    driver.quit()


if __name__ == "__main__":
    main()