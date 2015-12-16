from permutation import *
from fields import *
from matrix import *
from isomorphism import *
import sys
import random

# Ensure everything is working like it did for me
print "Running checks..."
matrix_vector_tests()
permutation_tests()
field_tests()
isomorphism_tests()
print "Checks completed.\n"


# Number 5
def str_to_class(str):
    return getattr(sys.modules[__name__], str)

print "EXPLORATORY PROBLEMS 2: #5 - FINITE FIELDS"
while True:

    field_string = raw_input("Enter in a field name e.g. F32, *OR leave empty* to move on to the next question.\n> ")
    if not field_string: break

    # Get class
    cls = None
    try:
        cls = str_to_class(field_string)
    except AttributeError:
        print "Could not find finite field. Either mistyped or not one of the ones from the problem."
        continue

    poly = cls.irreducible_poly
    field_member = cls("0")
    field_member.coefficients = poly
    print "Irreducible polynomial used for the selected field is", unicode(field_member), "."

    a_string = raw_input("\nSpecify first field member in standard polynomial order. Use smallest positive integer for coefficients (e.g. x^2 + 1).\n> a = ")
    b_string = raw_input("\nSpecify second field member in standard polynomial order. Use smallest positive integer for coefficients (e.g. x^2 + 1).\n> b = ")

    a = cls(a_string)
    b = cls(b_string)

    print ""
    print "a =", unicode(a)
    print "b =", unicode(b)
    print ""
    print "a * b =", unicode(a * b)
    print "a / b =", unicode(a / b)
    print "a + b =", unicode(a + b)
    print ""


print "EXPLORATORY PROBLEMS 3: #12 - MATRIX ISOMORPHISMS (Finite field matrices)"
while True:

    field_string = raw_input("Enter in a field name *OR leave empty* to move on to the next question.\n> ")
    if not field_string: break

    # Get class
    cls = None
    try:
        cls = str_to_class(field_string)
    except AttributeError:
        print "Could not find finite field. Either mistyped or not one of the ones from the problem."
        continue

    CURSOR_UP_ONE = '\x1b[1A'
    ERASE_LINE = '\x1b[2K'

    print("\nSpecify first matrix entry by entry, in reading order. Use field-specifying rules from before.")
    a1_str = raw_input("> a = [[")
    a2_str = raw_input(CURSOR_UP_ONE + ERASE_LINE + "> a = [[" + a1_str + ", ")
    a3_str = raw_input(CURSOR_UP_ONE + ERASE_LINE + "> a = [[" + a1_str + ", " + a2_str + "], [")
    a4_str = raw_input(CURSOR_UP_ONE + ERASE_LINE + "> a = [[" + a1_str + ", " + a2_str + "], [" + a3_str + ", ")
    print CURSOR_UP_ONE + ERASE_LINE + "> a = [[" + a1_str + ", " + a2_str + "], [" + a3_str + ", " + a4_str + "]]\n"

    a = Matrix.from_list([[cls(a1_str), cls(a2_str)], [cls(a3_str), cls(a4_str)]])

    print("\nSpecify second matrix entry by entry, in reading order. Use field-specifying rules from before.")
    b1_str = raw_input("> b = [[")
    b2_str = raw_input(CURSOR_UP_ONE + ERASE_LINE + "> b = [[" + b1_str + ", ")
    b3_str = raw_input(CURSOR_UP_ONE + ERASE_LINE + "> b = [[" + b1_str + ", " + b2_str + "], [")
    b4_str = raw_input(CURSOR_UP_ONE + ERASE_LINE + "> b = [[" + b1_str + ", " + b2_str + "], [" + b3_str + ", ")
    print CURSOR_UP_ONE + ERASE_LINE + "> b = [[" + b1_str + ", " + b2_str + "], [" + b3_str + ", " + b4_str + "]]\n"

    b = Matrix.from_list([[cls(b1_str), cls(b2_str)], [cls(b3_str), cls(b4_str)]])

    print "a * b =", unicode(a * b)


print "EXPLORATORY PROBLEMS 3: #12 - MATRIX ISOMORPHISMS (Permutations)"
while True:

    f_string = raw_input("Enter in a permutation in cycle notation (can be of A6) *OR leave empty* to move on to the next question. I is the identity.\n> f = ")
    if not f_string: break

    g_string = raw_input("Enter in another permutation in cycle notation (can be of A6). I is the identity.\n> g = ")

    symbols = map(str, list(range(1, 10)))
    f = Permutation(f_string, symbols)
    g = Permutation(g_string, symbols)

    print "g * f = ", Permutation.compose(g, f)
    print "f * g = ", Permutation.compose(f, g)
    print ""


print "EXPLORATORY PROBLEMS 3: #12 - MATRIX ISOMORPHISMS (Matrix -> Permutation)"
while True:
    field_string = raw_input("Enter in a field name: either F4 or F5, *OR leave empty* to move on to the next question.\n> ")
    if not field_string: break

    # Get class
    cls = None
    try:
        cls = str_to_class(field_string)
    except AttributeError:
        print "Could not find finite field. Either mistyped or not one of the ones from the problem."
        continue

    CURSOR_UP_ONE = '\x1b[1A'
    ERASE_LINE = '\x1b[2K'

    print("\nSpecify a *determinant 1* matrix entry by entry, in reading order. Use field-specifying rules from before.")
    a1_str = raw_input("> m = [[")
    a2_str = raw_input(CURSOR_UP_ONE + ERASE_LINE + "> m = [[" + a1_str + ", ")
    a3_str = raw_input(CURSOR_UP_ONE + ERASE_LINE + "> m = [[" + a1_str + ", " + a2_str + "], [")
    a4_str = raw_input(CURSOR_UP_ONE + ERASE_LINE + "> m = [[" + a1_str + ", " + a2_str + "], [" + a3_str + ", ")
    print CURSOR_UP_ONE + ERASE_LINE + "> m = [[" + a1_str + ", " + a2_str + "], [" + a3_str + ", " + a4_str + "]]\n"

    a1 = cls(a1_str)
    a2 = cls(a2_str)
    a3 = cls(a3_str)
    a4 = cls(a4_str)
    if (a1 * a4) + (a2 * a3) * cls("-1") != cls.mult_id():
        print "Determinant is not 1!"
        print ""
        continue

    a = Matrix.from_list([[a1, a2], [a3, a4]])

    lines = None
    if field_string == "F4":
        lines = lines_f4
    elif field_string == "F5" or field_string == "Z5": 
        lines = lines_f5
    else:
        print "Fields other than F4 or F5 don't have lines loaded in to check for a permutation."
        continue

    print "m corresponds to permutation:", unicode(matrix_to_permutation(a, lines))
    print "0 is the lowest symbol. These lines are being used:"
    for symbol, line in enumerate(lines):
        print symbol + ":", line
    print ""

print "EXPLORATORY PROBLEMS 3: #12 - MATRIX ISOMORPHISMS (Demonstrate isomorphism)"
while True:
    field_string = raw_input("Enter in a field name: either F4 or F5, *OR leave empty* to move on to the next question.\n> ")
    if not field_string: break

    # Get class
    cls = None
    try:
        cls = str_to_class(field_string)
    except AttributeError:
        print "Could not find finite field. Either mistyped or not one of the ones from the problem."
        continue
    print ""

    lines = None
    if field_string == "F4":
        lines = lines_f4
    elif field_string == "F5" or field_string == "Z5": 
        lines = lines_f5
    else:
        print "Fields other than F4 or F5 don't have lines loaded in to check for a permutation."
        continue

    print "Finding two random members of SL(2,", field_string + ")..."

    # Find all members
    all_members = []
    for member in cls.all_values():
        all_members.append(member)

    a1 = None
    a2 = None
    a3 = None
    a4 = None

    # Find at random
    while (True):
        a1 = random.choice(all_members)
        a2 = random.choice(all_members)
        a3 = random.choice(all_members)
        a4 = random.choice(all_members)

        if (a1 * a4) + (a2 * a3) * cls("-1") == cls.mult_id(): break

    a = Matrix.from_list([[a1, a2], [a3, a4]])
    print "Selected matrix a:", unicode(a),

    p_a = matrix_to_permutation(a, lines)
    print "Corresponding permutation:", unicode(p_a)


    b1 = None
    b2 = None
    b3 = None
    b4 = None

    # Find at random
    while (True):
        b1 = random.choice(all_members)
        b2 = random.choice(all_members)
        b3 = random.choice(all_members)
        b4 = random.choice(all_members)

        if (b1 * b4) + (b2 * b3) * cls("-1") == cls.mult_id(): break

    b = Matrix.from_list([[b1, b2], [b3, b4]])
    print "Selected matrix b:", unicode(b),

    p_b = matrix_to_permutation(b, lines)
    print "Corresponding permutation:", unicode(p_b)

    p_ab = matrix_to_permutation(a * b, lines)

    print ""
    print "Check that perm(a * b) = perm(a) * perm(b)..."
    print "perm(a) * perm(b) =", unicode(p_a), "*", unicode(p_b)
    print "=", unicode(Permutation.compose(p_a, p_b))
    print "\n"
    print "perm(a * b) = ", "perm(", unicode(a * b), ")"
    print "=", unicode(p_ab)

    assert unicode(p_ab) == unicode(Permutation.compose(p_a, p_b))
    print ""



