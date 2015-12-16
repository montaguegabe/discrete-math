import copy
from fields import *

# Define a vector
class Vector(object):

    def __init__(self, list_form):
        self.list_form = list_form

    def __add__(self, other):
        result = Vector(self.list_form[:])

        for i in xrange(len(result.list_form)):
            result[i] += other[i]

        return result

    def __mul__(self, other):

        result = Vector(self.list_form[:])

        if not isinstance(other, Vector):
            for i in xrange(len(result.list_form)):
                result.list_form[i] *= other
        else:
            raise TypeError("Vector multiplication is ambiguous")

        return result

    @staticmethod
    def dot_product(a, b):
        sum_prod = a[0].add_id()
        length = len(a)
        if length != len(b): raise ValueError("Dot product vectors must be same length")

        for i in xrange(length):
            sum_prod += a[i] * b[i]

        return sum_prod

    # Equality
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.list_form == other.list_form
        else:
            return False

    # List-style access
    def __len__(self):
        return len(self.list_form)

    def __getitem__(self, index):
        return self.list_form[index]

    def __setitem__(self, index, val):
        self.list_form[index] = val

    # String representation
    def __unicode__(self):
        return str(self.list_form)

    def __repr__(self):
        return "Vector(" + self.__unicode__() + ")"


# Define a matrix
class Matrix(object):

    def __init__(self, vector_list):
        super(Matrix, self).__init__()
        self.vector_list = vector_list

    # Makes a matrix from a list of row entries
    @staticmethod
    def from_list(list2D):
        height = len(list2D)
        width = len(list2D[0]) if height != 0 else 0

        vector_list = [Vector([]) for i in xrange(width)]
        result = Matrix([])
 
        for r in xrange(height):
            for c in xrange(width):
                vector_list[c].list_form.append(list2D[r][c])

        result.vector_list = vector_list
        return result

    # Determines dimensions
    def width(self):
        return len(self.vector_list)
    def height(self):
        return len(self.vector_list[0]) if self.vector_list else 0

    # Gets a row vector
    def get_row(self, i):
        width = self.width()
        result = Vector([])
        for c in xrange(width):
            result.list_form.append(self.vector_list[c][i])
        return result

    # Multiply
    def __mul__(self, other):

        result = None

        # Vector multiplication
        if isinstance(other, Vector):

            if len(other) != self.width():
                raise IndexError("Attempting to multiply matrix with a vector of incompatible dimensions.")

            result = Vector([])
            for i in xrange(self.height()):
                matrix_row = self.get_row(i)
                result.list_form.append(Vector.dot_product(matrix_row, other))

        # Matrix multiplication
        elif isinstance(other, Matrix):

            if other.height() != self.width():
                raise IndexError("Attempting to multiply matrix with another matrix of incompatible dimensions.")

            result = Matrix([])
            for other_vector in other.vector_list:
                result.vector_list.append(self * other_vector)

        # Scalar multiplication
        else:
            result = Matrix(copy.deepcopy(self.vector_list))
            length = len(result.vector_list)
            for i in xrange(length):
                result.vector_list[i] *= other

        return result

    # Equality
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.vector_list == other.vector_list
        else:
            return False

    # String representation
    def __unicode__(self):
        result = "\n"
        for r in xrange(self.height()):
            result += str(self.get_row(r))
            result += "\n"
        return result

    def __repr__(self):
        return "Matrix.from_list(" + self.__unicode__() + ")"

     
def matrix_vector_tests():

    m1 = Matrix.from_list([[R(0.5), R(0.3), R(4.5)], [R(2.0), R(-1.5), R(-2.2)]])
    m2 = Matrix.from_list([[R(0.7), R(-1.6)], [R(2.2), R(0.0)], [R(0.5), R(1.0)]])
    m3 = m1 * m2
    assert m3.vector_list[0][0] == R(3.26)
    assert m3.vector_list[1][0] == R(3.7)
    assert m3.vector_list[1][1] == R(-5.4)

    v = Vector([F4("x + 1"), F4("x")])
    scaled_v = v * F4("x")
    assert scaled_v == Vector([F4("1"), F4("x + 1")])

matrix_vector_tests()
