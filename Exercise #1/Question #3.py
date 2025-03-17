word_counter = []
while True:
    word = input("Please Type a word: ")
    if word in word_counter:
        print(f'You entered the word: "{word}" twice. Good bye')
        break
    else:
        word_counter.append(word)