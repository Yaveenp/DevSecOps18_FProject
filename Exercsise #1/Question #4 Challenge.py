list1 = []
list2 = []
list1counter = len(list1)
biggerList1 = 0
biggerList2 = 0
for n in range(12):
    numList = int(input("Please enter number: "))
    if n < 4:
        list1.append(numList)
        print(list1)
    else:
        list2.append(numList)
        print(list2)
for i in range(4):
    if list1[i] > list2[0-list1counter]:
        biggerList1 += 1
        print(biggerList1)
    else:
        biggerList2 += 2
        print(biggerList2)
if biggerList1 > biggerList2:
    print("List #1 have bigger numbers")
else:
    print("List #2 have bigger numbers")