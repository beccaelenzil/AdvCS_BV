class Queue:
    def __init__(self):
        self.array = []
    def enqueue(self, item):
        self.array.append(item)
    def dequeue(self):
        item = self.array[0]
        del self.array[0]
        return item
    def isEmpty(self):
        return len(self.array) == 0
    def size(self):
        return len(self.array)

q = Queue()
q.enqueue("hi")
q.enqueue("there")
print q.dequeue()
print q.dequeue()