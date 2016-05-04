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
        return len(self.array)==0
    def size(self):
        return len(self.array)

s = Stack()
s.push(1)
print s.pop()