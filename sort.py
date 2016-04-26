import matplotlib.pyplot as plt
import random

def quickSort(list, start = 0, stop = -1):
    if stop == -1: #if defaulted
        stop = len(list)-1
    if stop-start < 1:
        return
    left = start
    right = stop
    pivot = list[0]
    while left < right:
        while list[left] < pivot:
            left += 1
        while list[right] > pivot:
            right -= 1
        if left <= right:
            list[left], list[right] = list[right], list[left]
            left += 1
            right -= 1
            print list
    quickSort(list, start, right)
    quickSort(list, left, stop)

def insertionSort(list):
    iterations = 0
    for i in range(1, len(list)):
        for j in range(i, 0, -1):
            iterations += 1
            if list[j] < list[j-1]:
                list[j], list[j-1] = list[j-1], list[j]
            else:
                break
    return iterations

def selectionSort(list):
    #iterate through which value to start at
    iterations = 0
    for start in range(len(list)):
        lidx = start #lowest value index
        for el in range(start+1, len(list)):
            iterations += 1
            if list[el] < list[lidx]:
                lidx = el
        list[lidx], list[start] = list[start], list[lidx]
    return iterations

def bubbleSort(list):
    k = len(list) - 1
    flip = True
    iterations = 0
    while flip:
        flip = False
        for i in range(0, k):
            iterations += 1
            if list[i] > list[i+1]:
                list[i], list[i+1] = list[i+1], list[i]
                flip = True
        k -= 1
    return iterations

def create_random_list(length):
    return random.sample(range(length), length)

def display(list):
    plt.clf()
    plt.bar(range(len(list)), list)
    plt.draw()

list = [39, 30, 45, 55, 20, 61, 36, 5, 31, 64]
quickSort(list)
print list

#iterations = 0
#for i in range(100):
#    iterations += insertionSort(create_random_list(100))
#iterations /= 100

#print "ave iterations: " + str(iterations)

#plt.pause(1000)