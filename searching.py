import random

#Big-O: n
#best: 1
#worse: n
#avg: n/2
def sequentialSearch(list, el):
    for i in list:
        if i == el:
            return True
    return False

counter = 0

#Big-O: log n
#Best case: 1
#Worst case: log n
#Avg case: floor(log(n-1))
def binarySearch(list, el):
    val = list[len(list)/2]
    global counter
    counter += 1
    if len(list) == 1:
        return list[0] == el
    elif val > el: #search in lower half
        return binarySearch(list[:len(list)/2], el)
    elif val < el: #search in upper half
        return binarySearch(list[len(list)/2:], el)
    else: #equal to
        return True

#test
list = random.sample(range(100), 50)
list.sort()
print list
elyes = random.choice(list)
elno = random.choice([e for e in range(100) if e not in list])
print str(elyes) + " should be in the list"
print str(elno) + " shouldn't be in the list"
print binarySearch(list, elyes)
print binarySearch(list, elno)

#average
n = 256 #length of list
intrange = 1000 #range of integers inside it
iters = 1000 #iterations to get average

list = random.sample(range(intrange), n)
avg = 0
for i in range(iters):
    counter = 0
    binarySearch(list, random.randrange(intrange))
    avg += counter
avg /= iters

print "\naverage iterations: " + str(avg)