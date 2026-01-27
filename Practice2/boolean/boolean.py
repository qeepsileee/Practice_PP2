#Boolean Values In programming you often need to know if an expression is True or False. 
#You can evaluate any expression in Python, and get one of two answers, True or False.
#When you compare two values, the expression is evaluated and Python returns the Boolean answer:


print(10 > 9)
print(10 == 9)
print(10 < 9)




a = 200
b = 33

if b > a:
  print("b is greater than a")
else:
  print("b is not greater than a")





print(bool("Hello"))
print(bool(15))





x = "Hello"
y = 15

print(bool(x))
print(bool(y))




bool("abc")
bool(123)
bool(["apple", "cherry", "banana"])






bool(False)
bool(None)
bool(0)
bool("")
bool(())
bool([])
bool({})




def myFunction() :
  return True

print(myFunction())





def myFunction() :
  return True

if myFunction():
  print("YES!")
else:
  print("NO!")
