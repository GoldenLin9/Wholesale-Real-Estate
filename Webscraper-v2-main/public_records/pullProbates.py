import os, datetime
from Driver import Driver

driver = Driver("probate")
driver.getCSV("PROBATE DOCUMENT", "Last 7 Days")
people = driver.parsePeople()

driver.driver.quit()

with open(f"{os.path.dirname(os.path.realpath(__file__))}\\" + "probate_failsafe.csv", "w+") as f:
    for p in driver.properties:
        f.write(",".join([f"\"{i}\"" for i in p]).replace("\n", "\\n") + "\n")

Driver.upload("probate", "1HuCYlqxeBnuGRQTHzChkqrc_W36sVXQoBs-yzIrBDqY", datetime.datetime.now().strftime("%B"))

print("FINISHED")
