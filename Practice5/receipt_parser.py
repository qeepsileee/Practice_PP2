import re
pattern = r"ab*"
text = "abbb"
match = re.fullmatch(pattern,text)
print(match)





import re
pattern = r"ab{2,3}"
text = "abb"
match = re.fullmatch(pattern,text)
print(match)





import re
pattern = r"[a-z]_+[a-z]+"
text = "hello_world test_string Invalid_String"
match = re.findall(pattern,text)
print(match)




import re
pattern = r"[A-Z][a-z]+"
text = "Hello World TEST Python"
match = re.findall(pattern , text)
print(match)



import re
pattern = r"^a.*b$"
text = "axxxb"
match = re.fullmatch(pattern, text)
print(match)




import re

text = "Hello, world. Python is fun"
result = re.sub(r"[ ,\.]", ":", text)

print(result)




import re

text = "hello_world_python"

result = re.sub(r"_([a-z])", lambda match: match.group(1).upper(), text)

print(result)




import re
pattern = r"(?=[A-Z])"
text = 'HelloWorldPython'
match = re.split(pattern , text)
print(match)







import re

text = "HelloWorldPython"
result = re.sub(r"(?<!^)(?=[A-Z])", " ", text)

print(result)








import re

def camel_to_snake(text):
    return re.sub(r"(?<!^)(?=[A-Z])", "_", text).lower()

text = "helloWorldPython"
print(camel_to_snake(text))



