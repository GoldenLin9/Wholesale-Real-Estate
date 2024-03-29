import time
import regex as re

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

PAGE_WAIT = 2.5

class Property:

    def __init__(self, last_name = None, first_middle_name = None, mail_address = None, mail_city = None, mail_state = None, mail_zip = None, property_address = None, property_city = None, property_state = None, property_zip = None, recent_homestead = None):
        self.last_name = last_name
        self.first_middle_name = first_middle_name
        self.mail_address = mail_address
        self.mail_city = mail_city
        self.mail_state = mail_state
        self.mail_zip = mail_zip
        self.property_address = property_address
        self.property_city = property_city
        self.property_state = property_state
        self.property_zip = property_zip
        self.recent_homestead = recent_homestead

    
    def __str__(self):
        return f"""
        last:  {self.last_name}
        first_middle_name:  {self.first_middle_name}
        mail_address:  {self.mail_address}
        mail_city:  {self.mail_city}
        mail_state:  {self.mail_state}
        mail_zip:  {self.mail_zip}
        property_address:  {self.property_address}
        property_city:  {self.property_city}
        property_state:  {self.property_state}
        property_zip:  {self.property_zip}
        recent_homestead: {self.recent_homestead}
        """

def corp(name):
    bad_name = ["LLC", "TRE", "INC", "CORP", "COMPANY", "AND", "TRUST", "TRUSTEE", "ASSOCIATION", "AMERICA", "BANK", "ASSOCIATES", "STUDIO", "CLUB", "ROOFING", "UNION", "DEPARTMENT", "&", "CITY"]
    for part in name.split():
        if part in bad_name or re.match("[0-9]", part):
            return True
        
    return False

# operating under the assumption that (entries < 10)
def count_search_results(driver, name):
    rows_info = driver.find_element(By.ID, "quickSearch_info")

    if (rows_info.text == ""): return True

    R = int(rows_info.text.split("of ")[1].split()[0].replace(",", ""))
    
    # person inherited no properties
    if R == 0:
        return True

    if corp(name): return True
        
    return False

# breaks into last, first middle
def break_name(name):
    print(name)
    last, first_middle = name.split(", ")
    first, middle = first_middle.split(" ", 1) if ' ' in first_middle else (first_middle, "")
    return last, first, middle

def search_person(driver, name):
    text_box = driver.find_element(By.ID, "txtKeyWord")

    text_box.clear()
    text_box.send_keys(name)
    text_box.send_keys(Keys.ENTER)

    time.sleep(PAGE_WAIT)

def get_recent_homestead(driver):
    # looks at column of homestead
    tds = driver.find_element(By.ID, "div-exemptions").find_elements(By.CSS_SELECTOR, "td:nth-child(4n + 2)")
    for td in tds:
        homestead = td.text.lower()
        if homestead == "yes":
            return "Yes"
        elif homestead == "no":
            return "No"
        
def get_property_data(driver, property):
    try:
        # check owner names
        # first_second_owner = driver.find_element(By.ID, "first_second_owner").text
        # third_owner = driver.find_element(By.ID, "third_owner").text

        # if "\n" in first_second_owner:
        #     first_owner, second_owner = first_second_owner.split("\n")
        # else:
        #     first_owner, second_owner = first_second_owner, None

        # first_second_owner.replace("\n", " ")
        # if corp(first_second_owner) or corp(third_owner):
        #     return None
        mail_address_elem = driver.find_element(By.ID, "mailling_add")
        mail_address = mail_address_elem.text
        property.mail_address = mail_address
        print(mail_address)

        
        mail = mail_address.split("\n")

        mail_city, mail = mail[-1].split(", ")
        property.mail_city = mail_city

        mail_state, mail_zip = mail.split(" ")
        property.mail_state, property.mail_zip = mail_state, mail_zip


        site_address_elem = driver.find_element(By.ID, "site_address")
        site_address = site_address_elem.text
        property.property_address = site_address

        site_city_state_zip = site_address.split("\n")[1]

        site_city, site_state_zip = site_city_state_zip.split(", ")
        property.property_city = site_city

        site_state_zip = site_state_zip.split()
        site_state, site_zip = site_state_zip[0], site_state_zip[1]
        property.property_state, property.property_zip = site_state, site_zip

        property.recent_homestead = get_recent_homestead(driver)
        # first_owner_last_name, first_owner_first_name = first_owner.split(", ")
    except:
        return None

    return property

# also returns who the good owner is
def good_owners(owners, queried_name):
    matched_last, matched_first_middle = None, None
    queried_last, queried_first, queried_middle = break_name(queried_name)

    i = 0
    for owner in owners:
        if corp(owner) or ',' not in owner:
            return None, None
        
        owner_last, owner_first, owner_middle = break_name(owner)

        # we don't worry about middle since public records may not contain middle
        if owner_last == queried_last and owner_first == queried_first:
            if len(owner_middle) > 0:
                matched_last, matched_first_middle = owner_last, f"{owner_first} {owner_middle}"
            elif len(owner_middle) == 0:
                matched_last, matched_first_middle = owner_last, owner_first
        i+= 1

    return matched_last, matched_first_middle

def good_property(property_use):
    good_property_codes = ["0110", "0000"]
    code, description = property_use.split(" ", 1)
    code = code.strip()

    return code in good_property_codes


# return None for no properties or a list of properties
def find_properties(driver, queried_name):

    tBody = driver.find_element(By.CSS_SELECTOR, "tBody")
    tRows = tBody.find_elements(By.CSS_SELECTOR, "tr")


    good_name_properties = []
    links = []
    # I only create a link when i will click into the page for that property
    # Therefore, num of links = num of properties
    for row in tRows:
        property_use = row.find_element(By.CSS_SELECTOR, "td:nth-child(6)").text
        owners = row.find_element(By.CSS_SELECTOR, "td:nth-child(2)").text.split(" / ")

        matched_last, matched_first_middle = good_owners(owners, queried_name)

        print("testing... ", owners, queried_name)
        if matched_last != None and good_property(property_use):

            property = Property()
            property.last_name = matched_last
            property.first_middle_name = matched_first_middle
            print(property.last_name, property.first_middle_name)
            print("Property Type: ", property_use)
            
            good_name_properties.append(property)
            links.append(row.find_element(By.CSS_SELECTOR, "a").get_attribute("href"))
    
    good_house_properties = []
    # loop through each good property in the table
    for i in range(len(links)):
        driver.get(links[i])

        print("entering get property data")
        property = get_property_data(driver, good_name_properties[i])
        if property != None:
            good_house_properties.append(property)

    
    return good_house_properties if len(good_house_properties) > 0 else None

def setup():
    options = webdriver.ChromeOptions()
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    driver = webdriver.Chrome()
    return driver