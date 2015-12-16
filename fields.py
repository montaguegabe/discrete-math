# The parent class of all fields
class Field(object):
    def __init__(self):
        super(Field, self).__init__()

    # Gets the identities
    @staticmethod
    def mult_id():
        raise NotImplementedError

    @staticmethod
    def add_id():
        raise NotImplementedError

# Define a normal number in the real numbers
class R(float):
    def __new__(cls, float_string):
        try: return float.__new__(cls, float_string)
        except (TypeError, ValueError): raise ValueError("Could not make float out of real number")

    @staticmethod
    def mult_id():
        return 1.0

    @staticmethod
    def add_id():
        return 0.0

# The parent class of all finite fields
class FiniteField(Field):

    # The characteristic
    char = None

    # Number of copies of the characteristic cyclic group, max power + 1
    r = None

    # The generator of the logarithm table
    primitive = None

    # The logarithm table of the field
    log_table = None

    def __init__(self):
        super(Field, self).__init__()

    # Gets the size of the field
    @staticmethod  
    def size():
        return char ** r

    # Gets all elements of the field (as an iterable)
    @staticmethod
    def all_values():

        # Yield the additive identity first
        yield add_id()

        # Then yield the multiplicative identity
        yield mult_id()

        # Iterate through the rest of the multiplicative group
        size_f_mult = size() - 1
        value = mult_id()

        # Yield the subsequent powers
        iteration = 1
        while iteration < size_f_mult:

            value = value * primitive
            yield value
            iteration += 1


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