import pandas as pd
import glob
import os
import regex as re
import math

def break_name(name):
    last, first_middle = name.split(" ", 1)
    first, middle = first_middle.split(" ", 1) if ' ' in first_middle else (first_middle, None)
    return last, first, middle

previous_names = None
unique_names = []

# REALLY INEFFICIENT O(N^2), could binary search O(logn) on names to check for duplicates but....... rn nah LMAO
def duplicated(name):
    
    # shorter = better since i have more options
    for i, other in enumerate(unique_names):
        last, first, middle = break_name(name)
        other_last, other_first, other_middle = break_name(other)

        if first == other_first and last == other_last:
            print(name, other)
            if middle == None:
                unique_names[i] = name
                print(f"replaced {other} with {name}")
                return True
            
            if other_middle == None:
                return True
            
            # fix wierdness of middl name
            middle.replace(".", "").replace("-", " ")
            other_middle.replace(".", "").replace("-", " ")

            # check if one string is string substring of another, if so, replace with shorter string
            # why? more possibility for results to show up on pcp
            middle_parts = middle.split(" ")
            other_middle_parts = middle.split(" ")
            print(name, other)
            print(middle_parts, other_middle_parts)
            # middle is shorter than other middle and middle has all substring parts of other_middle
            if len(middle) < len(other_middle) and all([other_middle_parts[i].startswith(middle_parts[i]) for i in range(len(middle_parts))]):
                unique_names[i] = name
                print(f"replaced {other} with {name}")

            return True
        
    return False

def bad(name):
    bad_name = ["LLC", "TRE", "INC", "CORP", "COMPANY", "AND", "TRUST", "TRUSTEE", "ASSOCIATION", "AMERICA", "BANK", "ASSOCIATES", "STUDIO", "CLUB", "ROOFING", "UNION", "DEPARTMENT", "&", "CITY"]
    for part in name.split():
        if part in bad_name or re.match("[0-9]", part):
            return True
        
    return False

list_of_files = glob.glob("C:/Users/06141\Downloads/SearchResults*.csv")
latest_file = max(list_of_files, key=os.path.getctime)

prev_df = pd.read_csv("../pulls/all_liens.csv")
previous_names = prev_df["Previous Liens"]


df = pd.read_csv(latest_file)


names = df["IndirectName"]
count = 0
for name in names:
    if pd.isna(name) or ' ' not in name or bad(name):
        continue

    if previous_names.str.contains(name).any():
        print("SKIP TO LOAFER")
        continue
    # avoid adding duplicates into excel to save memory storage
    elif name not in unique_names:
        # add name to previous records if not found

        data = { "Previous Liens": [name]}
        data_df = pd.DataFrame(data)
        data_df.to_csv("../pulls/all_liens.csv", mode = "a", header = False, index = False)

    if not duplicated(name):
        unique_names.append(name)
        count += 1

# fix name format; easier search and check in get_data
for i in range(len(unique_names)):

    name = unique_names[i]
    first, second = name.split(" ", 1)

    # last, first M    Format
    new_name = f"{first}, {second}"
    unique_names[i] = new_name


df = pd.DataFrame({"Liens Names": unique_names})
df.to_csv("C:/Users/06141\Downloads/LiensNames.csv", index = False)

# get_person_data.main()