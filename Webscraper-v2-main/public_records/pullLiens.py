import os, datetime
from Driver import Driver

driver = Driver("liens")
driver.getCSV("LIENS", "Last 7 Days")
people = driver.parsePeople()

driver.driver.quit()

with open(f"{os.path.dirname(os.path.realpath(__file__))}\\" + "liens_failsafe.csv", "w+") as f:
    for p in driver.properties:
        f.write(",".join([f"\"{i}\"" for i in p]).replace("\n", "\\n") + "\n")

Driver.upload("liens", "11oogJgfy7CRXAXGAzm-qts1UcZqKSzPbF4OUcpmQ7yk", datetime.datetime.now().strftime("%B"))

print("FINISHED")
