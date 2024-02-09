import pandas as pd
import glob
import os
import regex as re
import math
import get_person_data


list_of_files = glob.glob("C:/Users/06141\Downloads/*SearchResults*.csv")
latest_file = max(list_of_files, key=os.path.getctime)

df = pd.read_csv(latest_file)
print(latest_file)

unique_names = []

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


names = df["IndirectName"]
count = 0
for name in names:

    if not pd.isna(name) and not duplicated(name):
        unique_names.append(name)
        count += 1


df = pd.DataFrame({"Liens Names": unique_names})
df.to_csv("C:/Users/06141\Downloads/liensNames.csv", index = False)

get_person_data.main()