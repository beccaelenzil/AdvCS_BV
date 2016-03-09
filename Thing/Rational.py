class Rational:
        def __init__(self, num, denom):
            self.numerator = num
            self.denominator = denom
        def __add__(self, other):
            newNum = self.numerator * other.denominator + self.denominator * other.numerator
            newDen = self.denominator * other.denominator
            return Rational(newNum, newDen)
        def __eq__(self, other):
            return self.numerator * other.denominator == self.denominator * other.numerator
        def __ge__(self, other):
            return self.numerator * other.denominator >= self.denominator * other.numerator
        def __str__(self):
            return str(self.numerator) + "/" + str(self.denominator)