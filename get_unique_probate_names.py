import pandas as pd
import glob
import os
import regex as re
import math



# REALLY INEFFICIENT O(N^2), could binary search O(logn) on names to check for duplicates but....... rn nah LMAO
def duplicated(name):
    
    # false = not duplicate
    # true = duplicate
    for test in unique_names:
        fixName = lambda x: (x.replace("-", " ").replace(".", " ")).split()
        fixed_name = fixName(name)
        fixed_test = fixName(test)

        longer = shorter = None
        longer_fixed = shorter_fixed = None
        if (len(name) > len(test)):
            longer = name
            shorter = test
            longer_fixed = fixed_name
            shorter_fixed = fixed_test
        else:
            longer = test
            shorter = name
            longer_fixed = fixed_test
            shorter_fixed = fixed_name

        # check for potential duplicate
        for i in range(len(shorter_fixed)):
            if shorter_fixed[i] == longer_fixed[i]:
                continue
            elif len(shorter_fixed[i]) == 0 and longer_fixed[i].startswith(shorter_fixed[i]):
                continue
            else:
                break
        else:
            unique_names.remove(test)
            unique_names.append(longer)
            return True

    return False

def bad(name):
    bad_name = ["LLC", "TRE", "INC", "CORP", "COMPANY", "AND", "TRUST", "TRUSTEE", "ASSOCIATION", "AMERICA", "BANK", "ASSOCIATES", "STUDIO", "CLUB", "ROOFING", "UNION", "DEPARTMENT", "&", "CITY"]
    for part in name.split():
        if part == bad_name or re.match("[0-9]", part):
            return True
        
    return False

list_of_files = glob.glob("C:/Users/06141\Downloads/SearchResults*.csv")
latest_file = max(list_of_files, key=os.path.getctime)

df = pd.read_csv(latest_file)
print(latest_file)

unique_names = []

names = df["DirectName"]
count = 0
for name in names:
    if bad(name):
        continue

    if not pd.isna(name) and not duplicated(name):
        unique_names.append(name)
        count += 1

# fix name format; easier search and check in get_data
for i in range(len(unique_names)):
    name = unique_names[i]
    first, second = name.split(" ", 1)

    # last, first M    Format
    new_name = f"{first}, {second}"
    unique_names[i] = new_name


df = pd.DataFrame({"Probate Names": unique_names})
df.to_csv("C:/Users/06141\Downloads/ProbateNames.csv", index = False)

# get_person_data.main()