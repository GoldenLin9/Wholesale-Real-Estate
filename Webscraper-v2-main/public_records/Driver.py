import os, time, selenium, re
from Google import GoogleManager
from glob import glob

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

PAGE_WAIT = 2.5 
"""
    Amount of seconds it takes for the page to load
"""

class Driver():
    """
        ### Description
        Uses the Selenium Chrome Webdriver to access the Pinellas County Cleark of Court and Pinellas County Property Appraisal Websites.
        Takes a record type, at the moment the only supported types are *probate* and *liens*
    """

    def __init__(self, type: str = "probate") -> None:
        """
        ### Parameters
        @type : Changes how Comma Seperated Values (CSV) files downloaded from the Clerk of Court are managed.
        """
        self.dir = f"{os.path.dirname(os.path.realpath(__file__))}\\records\\" # Grabs the current location of this file and locates the records
        self.type = type

        options = webdriver.ChromeOptions()

        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        options.add_experimental_option("prefs", {
            "download.default_directory": self.dir + "tmp\\",
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        }) # Sets where and how to save the CSV file.
        options.page_load_strategy = 'eager' # Forcing selenium to do it's actions before the page loads (doesn't always work, hence PAGE_WAIT)

        self.driver = webdriver.Chrome(options=options)
        self.latest = "" # The location of the CSV file.

        self.properties = [] # List of property locations in pinellas county matching the records.
    
    def getCSV(self, period: str = "Last 7 Days") -> None:
        """
        ### Parameters
        @period: Simple range select on the Clerk of Court website | ("Today", "Yesterday", "Last 7 Days", "Last 14 Days", "Last Month")
        """

        doctype = ""
        if self.type == "probate": doctype = "PROBATE DOCUMENT"
        elif self.type == "liens": doctype = "LIENS"

        link = "https://officialrecords.mypinellasclerk.org/search/SearchTypeDocType"
        self.driver.get(link)

        try: self.driver.find_element(By.ID, "btnButton").submit()
        except: pass

        self.driver.find_element(By.ID, "DocTypesDisplay-input").send_keys(doctype)
        self.driver.find_element(By.ID, "DateRangeDropDown").find_element(By.CSS_SELECTOR, ".t-arrow-down").click()

        all_options = self.driver.find_elements(By.CSS_SELECTOR, ".t-item")
        for option in all_options:
            if option.text == period:
                option.click()
                break

        self.driver.find_element(By.ID, "btnSearch").click()

        try: self.driver.find_element(By.ID, "btnSearch").click()
        except selenium.common.exceptions.ElementClickInterceptedException: pass

        time.sleep(0.5)

        try: self.driver.find_element(By.ID, "btnSearch").click() # Quicker response times
        except selenium.common.exceptions.ElementClickInterceptedException: pass

        try:
            time.sleep(2)
            WebDriverWait(self.driver, 100).until(
                EC.presence_of_element_located((By.ID, "btnCsvButton"))
            )
            self.driver.find_element(By.ID, "btnCsvButton").click()
        except RecursionError: print("Warning: The CSV file was unable to be downloaded")
        except: self.getCSV(type, period)
    
    def parsePeople(self):
        """
        ### Description:
        Goes through every record and puts it through the pcpao function.
        """
        files = glob(self.dir + "tmp\\*")
        self.latest = max(files, key=os.path.getctime)
        
        csv = []
        for m in open(self.latest).readlines()[1:]: csv.append(m.split(","))

        if self.type == "probate": 
            for record in csv: self.pcpao(record[0])
        elif self.type == "liens": 
            for record in csv: self.pcpao(record[1])
    
    def pcpao(self, name) -> None:
        """
        ### Description:
        Gathers the location from the Pinellas County Property Apraisal Website

        ### Parameters:
        @name: Name in "Lastname, First (Middle)" format
        """
        try:
            self.driver.get(f"https://www.pcpao.gov/quick-search?qu=1&input={str("%20".join(self.filterName(name)))}&search_option=owner")
            time.sleep(PAGE_WAIT)
            rows = self.driver.find_element(By.ID, "quickSearch").find_element(By.CSS_SELECTOR, "tbody").find_elements(By.CSS_SELECTOR, "tr")

            for row in rows:
                r = row.find_element(By.CSS_SELECTOR, "td")

                if r.text == "No Results matched your search criteria. Please modify your search and try again.": continue
                if ["0000" in row.find_element(By.CSS_SELECTOR, "td:nth-child(6)").text, "0110" in row.find_element(By.CSS_SELECTOR, "td:nth-child(6)").text] == [False, False]: continue

                self.driver.get(row.find_element(By.CSS_SELECTOR, "td:nth-child(3)").find_element(By.CSS_SELECTOR, "a").get_attribute("href"))
                
                cname = ""
                names = self.driver.find_element(By.ID, "first_second_owner").text.split("\n")
                siteaddress = self.driver.find_element(By.ID, "site_address").text
                mailaddress = self.driver.find_element(By.ID, "mailling_add").text
                homestead = self.driver.find_element(By.ID, "tblExemptions").find_element(By.CSS_SELECTOR, "tbody").find_element(By.CSS_SELECTOR, "tr:nth-child(1)").find_element(By.CSS_SELECTOR, "td:nth-child(2)").text

                for n in names:
                    if n.split(",")[0].removesuffix(" ") == name.split(" ")[0].removeprefix(" ") and n.split(",")[1].removeprefix(" ").split(" ")[0] == name.split(" ")[1].removeprefix(" "):
                        cname = n
                        continue

                if cname == "": continue
                property = [cname]
                property.extend([cname.split(",")[1].removesuffix(" ").replace(".", ""), cname.split(",")[0].removesuffix(" ")])
                property.extend(self.returnAddCityStateZip(mailaddress))
                property.extend(self.returnAddCityStateZip(siteaddress))
                property.append("".join(homestead).capitalize())
                self.properties.append(property)
        except selenium.common.exceptions.StaleElementReferenceException: print("Warning: Element trying to be accessed doesn't exist anymore. This may be dure to a 404 Website Error.")
        except selenium.common.exceptions.NoSuchElementException: print("Warning: Element trying to be accessed doesn't exist anymore. This may be dure to a 404 Website Error.")
        except selenium.common.exceptions.WebDriverException: print("Warning: Browser has possible closed or crashed.")
        except IndexError: return
        except TypeError: return

    def returnAddCityStateZip(self, address: str = "") -> list:
        """
        ### Description:
        Formats the address into < Property Address, Property City, Property State, Property Zip >

        ### Parameters:
        @address: Full length address
        """
        return [address, address.rsplit("\n", 1)[1].split(",")[0], address.rsplit("\n", 1)[1].split(", ")[1].split(" ")[0], address.rsplit("\n", 1)[1].split(", ")[1].split(" ")[1]]

    def filterName(self, name: str) -> str:
        """
        ### Description:
        Filters Humans from Buisnesses

        ### Parameters:
        @name: Name in "Lastname, First (Middle)" format
        """
        if len(name.split(" ")) < 2: return None
        elif True in [n.removesuffix(" ").removeprefix(" ") in ["LLC", "SERVICE", "TRE", "TAMPA", "OF", "INC", "CORP", "PETERSBURG", "PINELLAS", "CREDIT", "ST", "CORPORATION", "COMPANY", "AND", "TRUST", "TRUSTEE", "ASSOCIATION", "AMERICA", "BANK", "ASSOCIATES", "STUDIO", "CLUB", "ROOFING", "UNION", "DEPARTMENT", "&", "CITY", "STATE", "STATES"] for n in name.split()]: return None
        elif re.match("[0-9]", name): return None
        return [name.split(" ", 1)[0] + ",", name.split(" ", 1)[1].replace(".", "")]

gsm = GoogleManager()
dir = os.path.dirname(os.path.realpath(__file__))

def upload(type, id, sheet):
    data = gsm.read(id, f"{sheet}")
    data.extend([i.split(",") for i in open(f"{dir}\\{type}_" + "failsafe_fixed.csv", "r+").readlines()])
    gsm.update(
        id,
        f"{sheet}",
        "USER_ENTERED",
        data
    )
