import matplotlib.pyplot as plt
import random

def selectionSort(list):
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

iterations = 0
for i in range(100):
    iterations += selectionSort(create_random_list(100))
iterations /= 100

print "ave iterations: " + str(iterations)

plt.pause(1000)