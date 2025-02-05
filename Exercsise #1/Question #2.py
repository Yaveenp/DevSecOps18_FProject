counter = 0
numbers_sum = 0
while True:
    if counter < 1:
        number = int(input("Please enter number #1: "))
        numbers_sum += number
        counter += 1
        print(counter)
    elif counter >= 1:
        number = float(input(f"Please enter number #{counter} (avg={numbers_sum / counter}. Sum={numbers_sum}): "))
        if number < 0:
            print("Thank you. Goodbye.")
            break

        numbers_sum += number
        counter += 1