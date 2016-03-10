# python 2
#
# Problem Set 1, Problem 1: Dates
#
# Name:
#

class Date:
    """ a user-defined data structure that
        stores and manipulates dates
    """
    # the constructor is always named __init__ !
    def __init__(self, month, day, year):
        """ the constructor for objects of type Date """
        self.month = month
        self.day = day
        self.year = year
        self.days = [31, 28 + self.isLeapYear(), 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        self.dows = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

    # the "printing" function is always named __repr__ !
    def __repr__(self):
        """ This method returns a string representation for the
            object of type Date that calls it (named self).

             ** Note that this _can_ be called explicitly, but
                it more often is used implicitly via the print
                statement or simply by expressing self's value.
        """
        s =  "%02d/%02d/%04d" % (self.month, self.day, self.year)
        return s


    # here is an example of a "method" of the Date class:
    def isLeapYear(self):
        """ Returns True if the calling object is
            in a leap year; False otherwise. """
        if self.year % 400 == 0: return True
        elif self.year % 100 == 0: return False
        elif self.year % 4 == 0: return True
        return False

    def copy(self):
        """ Returns a new object with the same month, day, year
            as the calling object (self).
        """
        dnew = Date(self.month, self.day, self.year)
        return dnew

    def equals(self, d2):
        """ Decides if self and d2 represent the same calendar date,
            whether or not they are the in the same place in memory.
        """
        return (self.year == d2.year and self.month == d2.month and self.day == d2.day)

    def tomorrow(self):
        """
        Changes to the date of the following day
        """

        if(self.days[self.month-1] == self.day):
            if(self.month == 12):
                self.month = 1
                self.day = 1
                self.year += 1
                self.days[1] = 28 + self.isLeapYear()
            else:
                self.month += 1
                self.day = 1
        else:
            self.day += 1

    def yesterday(self):
        """
        Changes to the date of the previous day
        """
        if(self.day == 1):
            if(self.month == 1):
                self.month = 12
                self.day = 31
                self.year -= 1
                self.days[1] = 28 + self.isLeapYear()
            else:
                self.month -= 1
                self.day = self.days[self.month-1]
        else:
            self.day -= 1

    def addNDays(self, n):
        """
        Adds n days to the date
        """
        while n != 0:
            if (n > 0):
                self.tomorrow()
                n -= 1
            else:
                self.yesterday()
                n += 1

    def isBefore(self, d2):
        if self.year != d2.year:
            return self.year < d2.year
        elif self.month != d2.month:
            return self.month < d2.month
        else:
            return self.day < d2.day

    def isAfter(self, d2):
        if self.year != d2.year:
            return self.year > d2.year
        elif self.month != d2.month:
            return self.month > d2.month
        else:
            return self.day > d2.day

    def diff(self, d2):
        if(d2.isBefore(self)):
            start = d2
            end = self
        else:
            start = self
            end = d2
        dayDays = end.day - start.day
        monthDays = 0
        for i in range(start.month, end.month):
            monthDays += self.days[i-1]
        yearDays = 0
        for i in range(start.year, end.year):
            yearDays += (366 if Date(1, 1, i).isLeapYear() else 365)
        total = dayDays + monthDays + yearDays
        if start.isLeapYear() and start.month>2:
            total -= 1
        return total * (1 if d2.isAfter(self) else -1)

    def dow(self):
        return self.dows[Date(3, 6, 2016).diff(self) % 7]


print Date(2, 29, 1952).diff(Date(2, 29, 2016))