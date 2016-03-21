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
        #the array representing the number of days in each month
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

        Switches through 3 cases:
        a. December 31st, in which case the new date is Jan 1 of the next year
        b. Last day of another non-December month, in which month is incremented and day is set to 1
        c. Not the last day of the month, in which case day is incremented
        """
        if(self.days[self.month-1] == self.day):
            if(self.month == 12):
                self.month = 1
                self.day = 1
                self.year += 1
                self.days[1] = 28 + self.isLeapYear() #update days in month array to account for current year's leap status
            else:
                self.month += 1
                self.day = 1
        else:
            self.day += 1

    def yesterday(self):
        """
        Changes to the date of the previous day

        Switches through 3 cases:
        a. Jan 1, in which case the new date is Dec 31 of the previous year
        b. First day of another non-January month, in which month is decremented and day is set to however many days are in the new month
        c. Not the first day of the month, in which case day is decremented
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
        Adds n days to the date (or subtracts for n < 0)
        """
        while n != 0: #go until all days are added/subtracted
            if (n > 0): #if you are heading forwards or backwards
                self.tomorrow()
                n -= 1
            else:
                self.yesterday()
                n += 1

    def subNDays(self, n):
        return self.addNDays(-n)

    def isBefore(self, d2):
        """
        Looks at the elements of each date in order of decreasing significance, exiting the function when one element is greater
        """
        if self.year != d2.year:
            return self.year < d2.year
        elif self.month != d2.month:
            return self.month < d2.month
        else:
            return self.day < d2.day

    def isAfter(self, d2):
        #Same principle of operation as isBefore
        if self.year != d2.year:
            return self.year > d2.year
        elif self.month != d2.month:
            return self.month > d2.month
        else:
            return self.day > d2.day

    def diff(self, d2):
        """
        Difference in days between self and d2.
        Positive when d2 is after self, or negative otherwise
        """
        test = self.copy() #create a copy to avoid changing the current date
        counter = 0 #variable to count number of days traveled
        if d2.isAfter(self): #if traveling forwards rather than backwards, do this
            while not test.equals(d2): #count and increment test until it equals d2
                test.tomorrow()
                counter -= 1
        else:
            while not test.equals(d2): #same but decrement counter to account for going backwards
                test.yesterday()
                counter += 1
        return counter

    #this is the old one that doesn't quite work
    #def diff(self, d2):
    #    if(d2.isBefore(self)):
    #        start = d2
    #        end = self
    #    else:
    #        start = self
    #        end = d2
    #    dayDays = end.day - start.day
    #    monthDays = 0
    #    for i in range(min(start.month, end.month), max(start.month, end.month)):
    #        monthDays += (Date(1, 1, end.year if start.month<end.month else start.year).days[i-1] * (1 if start.month<end.month else -1))
    #    yearDays = 0
    #    for i in range(start.year, end.year):
    #        yearDays += (366 if Date(1, 1, i + (start.month>2)).isLeapYear() else 365)
    #    total = dayDays + monthDays + yearDays
    #    return total * (1 if d2.isAfter(self) else -1)

    def dow(self):
        """
        Gives the day of the week of the current object in text.
        Looks at the difference between self and a 3/6/2016, which is known to be a Sunday. Then gets the remainder when
        divided by 7 to find index of day of week.
        """
        return self.dows[self.diff(Date(3, 6, 2016)) % 7]


#self-test:
print Date(12, 31, 2099).dow()
print Date(1, 1, 2100).dow()