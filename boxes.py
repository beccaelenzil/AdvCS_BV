from visual import *
b = box()
b.length = 0.5
b.width = 2.0
b.height = 1.5
b.color = (0.0, 1.0, 0.0)
b.pos = vector(0, 1, 2)
#while True:
#    rate(60)
#    b.rotate(angle=pi/100)

boxList = []
for boxNumber in range(10):
    x = random.randint(-5, 5) # integer between -5,5
    y = random.randint(-5, 5)
    z = random.randint(-5, 5)
    red = random.random()     # real number between 0 & 1
    green = random.random()
    blue = random.random()
    newBox = box(pos = vector(x, y, z),
                 color = (red, green, blue) )
    boxList.append(newBox)
while True:
    for myBox in boxList:
        rate(120)
        myBox.rotate(angle=pi/100)