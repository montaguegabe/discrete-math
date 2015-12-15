"""
    Problem 12

    Gabe Montague

    Multiplies 2x2 matrices of F4.
"""

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
            x = c = 1

        self.c_term = c
        self.x_term = x

    # Gets all elements of the field
    @staticmethod
    def all_values():
        return [F4("0"), F4("1"), F4("x"), F4("x + 1")]

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

    def __unicode__(self):

        if self.x_term == 1 and self.c_term == 1: return "x + 1"
        if self.x_term == 1 and self.c_term == 0: return "x"
        return str(self.c_term)

    def __repr__(self):
        return self.__unicode__()



# Define a vector
class Vector(object):

    def __init__(self, listForm):
        self.listForm = listForm

    def __add__(self, other):
        result = Vector(self.listForm)

        for i in xrange(len(result.listForm)):
            result[i] += other[i]

        return result

    def __len__(self):
        return len(self.listForm)

    def __getitem__(self, index):
        return self.listForm[index]

    # String representation
    def __unicode__(self):
        return str(self.listForm)

    def __repr__(self):
        return self.__unicode__()


# Define a two by two matrix holding F4
class Matrix(object):

    def __init__(self, listForm):
        super(Matrix2, self).__init__()
        self.listForm = listForm

    # Multiply two matrices
    def __mul__(self, other):

        basis = other.listForm
        trans = self.listForm

        # Instantiate an empty result array
        empty_row = [F4("0")] * len(basis[0])
        result = [empty_row[:] for i in xrange(0, len(trans))]

        # Cycle through the basis matrix rows
        for basis_row, basis_row_entries in enumerate(basis):

            # Cycle through basis matrix entries in the row
            for basis_column, factor in enumerate(basis_row_entries):

                # Cycle through the corresponding column of the transformation matrix,
                # and add a column of products to the result matrix
                for trans_row, trans_row_entries in enumerate(trans):
                    product = trans_row_entries[basis_row] * factor
                    result[trans_row][basis_column] += product

        return Matrix2(result)

    # String representation
    def __unicode__(self):
        result = "\n" + str(self.listForm[0][0]).ljust(6)
        result += str(self.listForm[0][1]).ljust(6) + "\n"
        result += str(self.listForm[1][0]).ljust(6)
        result += str(self.listForm[1][1]).ljust(6) + "\n"
        return result

    def __repr__(self):
        return self.__unicode__()
        




        
