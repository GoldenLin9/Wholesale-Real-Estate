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

import get_data


def main():
    # setup webdriver
    search_page = "https://www.pcpao.gov/quick-search?qu=1&input=GANTT%20CANDACE&search_option=owner"
    driver = get_data.setup()
    driver.get(search_page)

    # grab file of names
    list_of_files = glob.glob("C:/Users/06141\Downloads/probateNames.csv")
    latest_file = max(list_of_files, key=os.path.getctime)

    on, last_stop = 0, 293
    

    # loop through each name and grab their information
    df = pd.read_csv(latest_file)
    names = df["Probate Names"]
    for name in names:
        on+= 1

        print(f"on {on}: {name}")
        if on < last_stop:
            continue

        get_data.search_person(driver, name)

        # check if name is corp or 0 search results
        if get_data.count_search_results(driver, name):
            continue

        properties = get_data.find_properties(driver, name)

        if properties == None:
            continue
        
        # read each property into excel
        for property in properties:
            data = {
                "Queried Name": [name],
                "First Name": [property.first_middle_name],
                "Last": [property.last_name],
                "Mail Address": [property.mail_address],
                "Mail City": [property.mail_city],
                "Mail State": [property.mail_zip],
                "Property Address": [property.property_address],
                "Property City": [property.property_city],
                "Property State": [property.property_state],
                "Property Zip": [property.property_zip],
                "Recent Homestead": [property.recent_homestead]
            }

            df = pd.DataFrame(data)

            try:
                add_header = pd.read_csv("../probates.csv").empty
            except pd.errors.EmptyDataError:
                add_header = True

            df.to_csv("../probates.csv", mode = "a", header = add_header, index = False)

        driver.get(search_page)

    time.sleep(10)
    driver.quit()


if __name__ == "__main__":
    main()