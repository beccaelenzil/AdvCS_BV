import sys

def minimumInefficient(list):
    currentMin = 0 #assume all positive
    for i in range(len(list)):
        isBestSoFar = True
        for j in range(len(list)):
            if list[i] > list[j]:
                isBestSoFar = False
        if isBestSoFar:
            currentMin = list[i]
    return currentMin

def minimumEfficient(list):
    min = sys.maxint
    for el in list:
        if el < min:
            min = el
    return min