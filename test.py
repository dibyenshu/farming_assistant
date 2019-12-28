import table_user_crops as crops
from inspect import getmembers, isfunction

print(len(getmembers(crops)))

for o in range(0,len(getmembers(crops))-8):
    print(getmembers(crops)[o][0])