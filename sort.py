import matplotlib.pyplot as plt
import random

def selectionSort(list):
    for start in range(len(list)):
        lidx = start #lowest value index
        for el in range(start+1, len(list)):
            if list[el] < list[lidx]:
                lidx = el
        list[lidx], list[start] = list[start], list[lidx]

def bubbleSort(list):
    k = len(list) - 1
    flip = True
    while flip:
        flip = False
        for i in range(0, k):
            if list[i] > list[i+1]:
                list[i], list[i+1] = list[i+1], list[i]
                flip = True
        k -= 1
    return list

def create_random_list(length):
    return random.sample(range(length), length)

def display(list):
    plt.clf()
    plt.bar(range(len(list)), list)
    plt.draw()

plt.ion()

list = create_random_list(10)
selectionSort(list)
display(list)

plt.pause(1000)