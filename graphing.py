import matplotlib.pyplot as plt

x = [i for i in range(0, 10)]
print len(x)
y = [i for i in range(-100, 100, 20)]
print len(y)

plt.plot(x, y)
plt.show()