def valid_num(a):
    b = a % 10
    if b % 2 == 0:
        print('Valid')
    else:
        print('Not valid')
        
a = int(input())
valid_num(a)
