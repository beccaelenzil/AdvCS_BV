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

def hotPotato(namelist, num):
    q = Queue()
    for name in namelist:
        q.enqueue(name)

    while q.size() > 1:
        for i in range(num):
            q.enqueue(q.dequeue())
        q.dequeue()

    print str(q.array[0]) + " wins"

hotPotato(["Bill","David","Susan","Jane","Kent","Brad"], 7)