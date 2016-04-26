def find_palendrome(word):
    if len(word) <= 1:
        return True
    if word[0].lower()==word[-1].lower():
        return find_palendrome(word[1:-1])
    return False

def alt_palendrome(word):
    return sum([word[i].lower()==word[-i-1].lower() for i in range(len(word)/2)])==len(word)/2

word = "hannah"
print find_palendrome(word)
print alt_palendrome(word)