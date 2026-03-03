import re
pattern = r"ab*"
text = open("raw.txt","r")
match = re.fullmatch(pattern,text)
print(match)





import re
pattern = r"ab{2,3}"
text = open("raw.txt","r")
match = re.fullmatch(pattern,text)
print(match)





import re
pattern = r"[a-z]_+[a-z]+"
text = open("raw.txt","r")
match = re.findall(pattern,text)
print(match)




import re
pattern = r"[A-Z][a-z]+"
text = open("raw.txt","r")
match = re.findall(pattern , text)
print(match)



import re
pattern = r"^a.*b$"
text = open("raw.txt","r")
match = re.fullmatch(pattern, text)
print(match)




import re

text = open("raw.txt","r")
result = re.sub(r"[ ,\.]", ":", text)

print(result)




import re

text = open("raw.txt","r")

result = re.sub(r"_([a-z])", lambda match: match.group(1).upper(), text)

print(result)




import re
pattern = r"(?=[A-Z])"
text = open("raw.txt","r")
match = re.split(pattern , text)
print(match)







import re

text = open("raw.txt","r")
result = re.sub(r"(?<!^)(?=[A-Z])", " ", text)

print(result)








import re

def camel_to_snake(text):
    return re.sub(r"(?<!^)(?=[A-Z])", "_", text).lower()

text = open("raw.txt","r")
print(camel_to_snake(text))
