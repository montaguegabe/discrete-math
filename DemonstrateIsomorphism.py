"""
    Problem 12

    Gabe Montague

    Constructs a permutation in A5 that corresponds to a given matrix
"""

from MultiplyA6Permutations import *
from MultiplyF4Matrices import *

m = Matrix2([[F4("1"), F4("x")], [F4("x + 1"), F4("0")]])

# Determines which line a vector belongs to
lines = [
    [F4("1"), F4("0")],
    [F4("0"), F4("1")],
    [F4("1"), F4("x")],
    [F4("1"), F4("1")],
    [F4("1"), F4("x+1")]
]

# Returns the index of the line that the vector belongs to
def whichLine(vector, lines):

    all_non_zero = all_f4()
    all_non_zero.remove(F4("0"))

    for index, initial in enumerate(lines):
        for scalar in all_non_zero:
            if vector == [initial[0] * scalar, initial[1] * scalar]: return index

    return None

v = [F4("x"), F4("x+1")]
v_line = whichLine(v, lines)

print "Here are our lines:"
for index, line in enumerate(lines):
    print index, ": multiples of", line
print ""
print "Vector", v, "belongs to line", v_line

# Converts a matrix to a line
def matrixToPermutation(matrix, lines):

    # The permutation to return
    permutation = Permutation("I")

    for index, line_member in lines:

        # See where it goes
        from_string = str(index)



        permutation = compose(permutation, )

    return permutation


# Test out matrix multiplication
identity = Matrix2([[F4("1"), F4("0")], [F4("0"), F4("1")]])
m1 = Matrix2([[F4("1"), F4("x")], [F4("x + 1"), F4("0")]])
m2 = Matrix2([[F4("x"), F4("x")], [F4("1"), F4("0")]])

print "Multiplying\n", m1, "\nand\n", m2
print "to get\n", m1 * m2


symbols = ['1', '2', '3', '4', '5', '6']

# Construct permutations from strings
a = Permutation(a, "(132)(465)")
b = Permutation(b, "(13)(24)(65)")

# Compute results
print "a:        ", a
print "b:        ", b
print "ab:       ", compose(a, b)
print "ba:       ", compose(b, a)