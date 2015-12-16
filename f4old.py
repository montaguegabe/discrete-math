# Define a member of F4
class F4(object):
    def __init__(self, string="0"):
        super(F4, self).__init__()
        
        c = 0
        x = 0

        if string == "1":
            c = 1
        elif string == "x":
            x = 1
        elif string == "x + 1" or string == "x+1":
            x = 1
            c = 1

        self.c_term = c
        self.x_term = x

    # Gets all elements of the field
    @staticmethod
    def all_values():
        return {F4("0"), F4("1"), F4("x"), F4("x + 1")}

    # Gets the identities
    @staticmethod
    def mult_id():
        return F4("1")

    @staticmethod
    def add_id():
        return F4("0")

    # Add two elements of the field
    def __add__(self, other):

        result = F4()

        result.c_term = (self.c_term + other.c_term) % 2
        result.x_term = (self.x_term + other.x_term) % 2

        return result

    # Multiplication
    def __mul__(self, other):

        result = F4()

        # Calculate x^2 term = x + 1
        extra_x = extra_c = self.x_term * other.x_term

        # Calculate x term
        result.x_term = (self.x_term * other.c_term + self.c_term * other.x_term + extra_x) % 2

        # Calculate constant term
        result.c_term = (self.c_term * other.c_term + extra_c) % 2

        return result

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.c_term == other.c_term and self.x_term == other.x_term
        else:
            return False

    def __hash__(self):
        return self.x_term * 2 + self.c_term

    def __unicode__(self):

        if self.x_term == 1 and self.c_term == 1: return "x + 1"
        if self.x_term == 1 and self.c_term == 0: return "x"
        return str(self.c_term)

    def __repr__(self):
        return "F4(" + self.__unicode__() + ")"