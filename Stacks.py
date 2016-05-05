import math

class Stack:
    def __init__(self):
        self.array = []
    def push(self, item):
        self.array.append(item)
    def pop(self):
        item = self.array[-1]
        del self.array[-1]
        return item
    def peek(self):
        return self.array[-1]
    def isEmpty(self):
        return len(self.array) == 0
    def size(self):
        return len(self.array)

def parenChecker(parenString):
    s = Stack() #create the stack
    for p in parenString: #iterate thru characters
        if p == '(': #if this is opening paren
            s.push(p) #add this char to the array
        elif p == ')': #if closing
            if s.isEmpty(): #if no openers left, then not balanced
                return False
            else: #close off this parenthesis
                s.pop()
    return s.isEmpty() #check if is balanced

def balancedSymbols(str):
    s = Stack()
    for p in str:
        if p in "{([":
            s.push(p)
        else:
            if s.isEmpty():
                return False
            elif ("})]")[("{([").index(s.pop())] != p:
                return False
    return s.isEmpty()

def dToB(n):
    s = Stack()
    [s.push(str(thing%2)) for thing in [n/(2**x) for x in range(int(math.log(max(n, 1), 2)) + 1)]]
    return "".join(s.array.__reversed__())

def dToBase(n, base):
    s = Stack()
    [s.push(str(thing%base)) for thing in [n/(base**x) for x in range(int(math.log(max(n, 1), base)) + 1)]]
    return "".join(s.array.__reversed__())

def parenCheckerSansStacks(list):
    ctr = 0
    for ch in list:
        ctr += 1 if ch=='(' else -1
        if ctr < 0:
            return False
    return ctr==0

print dToBase(110, 11)