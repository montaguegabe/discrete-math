from permutation import *
from fields import *
from matrix import *

# Determines which line a vector belongs to
lines = [
    [F4("1"), F4("0")],
    [F4("0"), F4("1")],
    [F4("1"), F4("x")],
    [F4("1"), F4("1")],
    [F4("1"), F4("x+1")]
]

# Test out matrix multiplication
mId = Matrix.from_list([[F4("1"), F4("0")], [F4("0"), F4("1")]])
m1 = Matrix.from_list([[F4("1"), F4("x")], [F4("x + 1"), F4("0")]])
m2 = Matrix.from_list([[F4("x"), F4("x")], [F4("1"), F4("0")]])
m3 = Matrix.from_list([[F4("1"), F4("x")], [F4("x + 1"), F4("0")]])

print "Multiplying\n", mId, "\nand\n", m2
print "to get\n", mId * m2


symbols = ['1', '2', '3', '4', '5', '6']

# Construct permutations from strings
a = Permutation("(132)(465)", symbols)
b = Permutation("(13)(24)(65)", symbols)

# Compute results
print "a:        ", a
print "b:        ", b
print "ab:       ", Permutation.compose(a, b)
print "ba:       ", Permutation.compose(b, a)
