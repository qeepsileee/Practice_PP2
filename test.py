import re
a = input()

match = re.search(r"Name:\s(.+),\sAge:\s(.+)",a)
if match:
    name = match.group(1)
    age = match.group(2)
    print(name,age)
