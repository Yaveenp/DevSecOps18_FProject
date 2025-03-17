list1 = []
list2 = []
biggerList1 = 0
biggerList2 = 0
for n in range(8):
    numList = int(input("Please enter number: "))
    if n < 4:
        list1.append(numList)
    else:
        list2.append(numList)
for i in range(4):
    if list1[i] > list2[i]:
        biggerList1 += 1
    else:
        biggerList2 += 2
if biggerList1 > biggerList2:
    print("List #1 have bigger numbers")
else:
    print("List #2 have bigger numbers")