numWords = 0
ok = False
while not ok:
    ok = True
    try:
        numWords = int(input("How many words? "))
    except:
        ok = False
    if numWords <= 0:
        ok = False

#words = ["hello", "haha"]
words = [''] * numWords
for i in range(numWords):
    words[i] = raw_input("enter word " + str(i) + ": ")

#matrix = [['h', 'e', 'l', 'l', 'o', 'h', 'h', 'h', 'h', 'h'],\
#          ['h', 'h', 'h', 'h', 'h', 'h', 'h', 'h', 'h', 'h'],\
#          ['h', 'h', 'h', 'h', 'h', 'h', 'h', 'h', 'h', 'h'],\
#          ['h', 'h', 'h', 'h', 'h', 'h', 'h', 'h', 'h', 'h'],\
#          ['h', 'h', 'h', 'h', 'h', 'a', 'h', 'a', 'h', 'h'],\
#          ['h', 'h', 'h', 'h', 'h', 'h', 'h', 'h', 'h', 'h'],\
#          ['h', 'h', 'h', 'h', 'h', 'h', 'h', 'h', 'h', 'h'],\
#          ['h', 'h', 'h', 'h', 'h', 'h', 'h', 'h', 'h', 'h'],\
#          ['h', 'h', 'h', 'h', 'h', 'h', 'h', 'h', 'h', 'h'],\
#          ['h', 'h', 'h', 'h', 'h', 'h', 'h', 'h', 'h', 'h']]

matrix = [[]] * 10
for i in range(10):
    matrix[i] = raw_input("enter row " + str(i) + ": ").split()

coords = []
for word in words:
    for row in range(10):
        for col in range(11-len(word)): #only go as far as needed
            match = True
            for check in range(len(word)):
                if matrix[row][col+check] != word[check]:
                    match = False
            if match:
                coords.append((row, col))
    for row in range(11-len(word)):
        for col in range(10):
            match = True
            for check in range(len(word)):
                if matrix[row+check][col] != word[check]:
                    match = False
            if match:
                coords.append((row, col))

print coords