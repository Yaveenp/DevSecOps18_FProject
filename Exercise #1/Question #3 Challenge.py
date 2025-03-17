word_counter = {}
while True:
    word = input("Please Type a word: ").lower()
    if word in word_counter:
        word_counter[word] += 1
    else:
        word_counter[word] = 1
    if word_counter[word] == 3:
        print(f'You entered the word: "{word}" more then twice. Good bye!')
        break