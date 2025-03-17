numbers = int(input("Enter a Number: "))
divided_num = []
for i in range(1, numbers+1):
    if numbers % i == 0:
        divided_num.append(i)
print(divided_num)