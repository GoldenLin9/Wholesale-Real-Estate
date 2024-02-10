import csv, re, time, requests
from urllib.parse import quote
import pandas as pd
from datetime import datetime

class Person:
    def __init__(self, name) -> None:
        self.name = name
        self.ids = []
        self.props = []
        self.listing = []

    def checkValid(self):
        split = self.name.split()
        for s in split:
            if s in ["LLC", "INC", "CORP", "COMPANY", "AND", "TRUST", "TRUSTEE", "ASSOCIATION", "AMERICA", "BANK", "ASSOCIATES", "STUDIO", "CLUB", "ROOFING", "UNION", "DEPARTMENT", "&", "CITY"]:
                return False
            elif re.match("[0-9]", s): return False
        return True
    
    def getIds(self):
        a = " ".join(quote(self.name, safe='').replace(',', '').replace('.', '').split("%20")).split()
        a[0] += (a.pop(1) if a[0] == "ST" else "") + "%2C"
        
        if len(a) <= 2: self.reference(f"https://www.pcpao.org/query_name.php?Text1={'+'.join(a)}&nR=500")
        else:
            self.reference(f"https://www.pcpao.org/query_name.php?Text1={a[0]}+{a[1]}+{a[2][0]}&nR=500")
            if len(self.ids) == 0: self.reference(f"https://www.pcpao.org/query_name.php?Text1={a[0]}+{a[1]}&nR=500")

    def getDetails(self):
        for idx, id in enumerate(self.ids):
            i = id.split('-')
            self.list(f"https://www.pcpao.org/general.php?strap={i[2]}{i[1]}{i[0]}{i[3]}{i[4]}{i[5]}", id, idx)
    
    def getAddress(self, loc):
        location = requests.get(f"https://nominatim.openstreetmap.org/search?q={quote(loc + ' FL', safe='').replace(',', '').replace('.', '').upper().replace('%20', '+')}&format=json").json()
        if len(location) == 0:
            location = requests.get(f"https://nominatim.openstreetmap.org/search?q={quote(loc, safe='').replace(',', '').replace('.', '').upper().replace('%20', '+')}&format=json").json()
        if len(location) == 0:
            location = requests.get(f"https://nominatim.openstreetmap.org/search?q={quote(' '.join(loc.split()[:-1]), safe='').replace(',', '').replace('.', '').upper().replace('%20', '+')}&format=json").json()
        if len(location) == 0:
            location = requests.get(f"https://nominatim.openstreetmap.org/search?q={quote(' '.join(loc.split()[:-2]), safe='').replace(',', '').replace('.', '').upper().replace('%20', '+')}&format=json").json()
        if len(location) == 0:
            location = requests.get(f"https://nominatim.openstreetmap.org/search?q={quote(' '.join(loc.split()[:-3]), safe='').replace(',', '').replace('.', '').upper().replace('%20', '+')}&format=json").json()
        if len(location) == 0:
            return []
        res = location[0]['display_name'].split(',') 
        return [' '.join(res[:2]), res[2], res[-2]]

    def reference(self, url):
        res = pd.read_html(requests.get(url).content)[0]
        props = res.get("Property Use")[:-6]
        results = res.get("Parcel Info")[:-6]
        for idx, r in enumerate(results):
            if r != "Your search returned no records" and props[idx] in ["Single Family Home", "Single Family - more than one house per parcel", "Vacant Residential - lot & acreage less than 5 acres"] and r not in self.ids:
                self.ids.append(r)
                self.props.append(props[idx])
    
    def list(self, url, id, idy):
        res = pd.read_html(requests.get(url).content)[2].get(f"{id} Compact Property Record Card")[1][63:].split("  ")
        use = res[0].split()

        if "EST" in use: use.remove("EST")
        if "(First" in use: return []

        cut = 0
        for idx, p in enumerate(use):
            if re.match("[0-9]", p): 
                cut = idx
                break

        names = []
        temp = []
        for idx, n in enumerate(use[:cut]):
            if "ST" in n:
                use[idx] = n + use[idx]
                continue

            if n.endswith(','):
                if idx != 0 and names != []:
                    names.append(temp)
                temp = []
            elif idx == len(use[:cut]) - 1:
                if len(temp) < 2:
                    temp.append(n)
                names.append(temp)
            elif len(temp) < 2:
                temp.append(n)

        print(names)
        relatives = '\n'.join([i[0] for i in names])
        
        m = self.getAddress(' '.join(use[cut:]))
        if m == []: return
        mail_add = m[0]
        mail_city = m[1]
        mail_st = use[-2]
        mail_zip = use[-1]

        site_add = res[1]
        site_city = ""
        site_st = "FL"

        if res[1].endswith("(Unincorporated)") or mail_add == res[1]:
            site_add = mail_add 
            site_zip = mail_zip
        else: 
            s = self.getAddress(res[1])
            if s == []: return
            site_add = s[0] 
            site_city = s[1] 
            site_zip = s[2]
        if self.checkValid():
            criteria = [self.name.split()[1], self.name.split()[0].removesuffix(','), "", relatives, mail_add, mail_city, mail_st, mail_zip, site_add, "", site_city, site_st, site_zip, f"{datetime.today().strftime('%Y/%m/%d')}, Type: {self.props[idy]}"]
        else: criteria = ["", "", self.name, relatives, mail_add, mail_city, mail_st, mail_zip, site_add, "", site_city, site_st, site_zip, f"{datetime.today().strftime('%Y/%m/%d')}, Type: {self.props[idy]}"]
        if criteria not in self.listing:
            self.listing.append(criteria)

start = time.perf_counter()
people = []
listings = []
with open(r"./SearchResults.csv", "r", encoding='utf-8') as file:
    content = csv.reader(file)
    i = 0
    for c in content:
        print(str(content.line_num))
        ind = 0
        if "PROBATE" in c[3]: ind = 0
        elif "LIEN" in c[3] or "LIS PENDENS" in c[3]: ind = 1

        person = Person(c[ind])
        if c[ind] not in people:
            person.getIds()
            if len(person.ids) > 0: 
                person.getDetails()
                people.append(person.name)
                listings.extend(person.listing)
        i += 1

with open(r"result.csv", "w+", newline='', encoding='utf-8') as file:
    csvwriter = csv.writer(file)
    csvwriter.writerow(["First Name", "Last Name", "LLC Owner", "Relative Name", "Mail Address", "Mail City", "Mail State", "Mail Zip", "Property Address", "Property Address 2", "Property City", "Property State", "Property Zip", "NOTES"])
    csvwriter.writerows(listings) 

print(f"{time.perf_counter() - start:0.4f}s")