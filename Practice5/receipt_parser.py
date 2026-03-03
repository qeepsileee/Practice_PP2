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