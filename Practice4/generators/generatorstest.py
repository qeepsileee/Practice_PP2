def square_generator(n):
    for i in range(n + 1):
        yield i * i

for num in square_generator(5):
    print(num)






    n = int(input())

for i in range(0, n + 1, 2):
    if i != n and n % 2 == 0:
        print(i, end=",")
    else:
        print(i)







def divisible_by_3_and_4(n):
    for i in range(n + 1):
        if i % 3 == 0 and i % 4 == 0:
            yield i

for num in divisible_by_3_and_4(50):
    print(num)









def squares(a, b):
    for i in range(a, b + 1):
        yield i * i

for value in squares(3, 7):
    print(value)




def countdown(n):
    while n >= 0:
        yield n
        n -= 1


for num in countdown(5):
    print(num)
