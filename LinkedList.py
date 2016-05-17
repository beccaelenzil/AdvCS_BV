class Node:
    def __init__(self, initdata):
        self.data = initdata
        self.next = None

    def getData(self):
        return self.data

    def getNext(self):
        return self.next

    def setData(self,newdata):
        self.data = newdata

    def setNext(self,newnext):
        self.next = newnext

class LinkedList:
    def __init__(self):
        self.head = None
    def isEmpty(self):
        return self.head == None
    def add(self, item):
        temp = Node(item)
        temp.next = self.head #set pointer to current head, then set temp as new head
        self.head = temp
    def size(self):
        if self.head == None:
            return 0
        counter = 0
        n = self.head
        while n != None:
            n = n.next
            counter += 1
        return counter
    def search(self, item):
        n = self.head
        while n != None:
            if item == n.data:
                return True
            n = n.next
        return False
    def remove(self, item):
        if self.search(item) == False: #not in list
            return False
        if self.head.data == item: #special case for if head is piece to remove
            self.head = self.head.next
            return True
        n = self.head
        while n.next.data != item:
            n = n.next
        n.next = n.next.next
        return True
    def __repr__(self):
        s = ""
        n = self.head
        while n != None:
            s += str(n.data) + ","
            n = n.next
        return s

l = LinkedList()
l.add(36)
l.add(42)
l.add(12)
print l
l.remove(42)
print l