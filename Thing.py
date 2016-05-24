class Person():
    def __init__(self, thing):
        self.name = thing

    def __repr__(self):
        s = "My name is "+self.name+"."
        return s

class Student(Person):
    def __init__(self, name, grade):
        Person.__init__(name, grade)
        self.name = name
        self.grade = grade
    def __repr__(self):
        s = "I am " + name + " and i am " + str(grade) + "."
        return s

plug = Student("plug", 9)
print plug