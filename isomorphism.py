from permutation import *
from matrix import *
from fields import *

# Returns the index of the line that the vector belongs to. Also takes a list of vectors
def which_line(vector, lines):

    assert lines

    field = type(lines[0][0])

    all_non_zero = []
    for member in field.all_values():
        all_non_zero.append(member)
    all_non_zero.remove(field.add_id())

    for index, initial in enumerate(lines):
        for scalar in all_non_zero:
            if vector == (initial * scalar): return index

    return None

# Converts a matrix to a line
def matrix_to_permutation(matrix, lines):

    # Get symbols from lines
    symbols = range(len(lines))
    symbols.reverse()
    char_symbols = map(str, symbols)

    # The permutation to return
    permutation = Permutation("I", char_symbols)

    # Map each of the lines
    symbols_left_to_map = copy.copy(symbols)
    from_index = symbols_left_to_map.pop()
    while symbols_left_to_map:

        if from_index in symbols_left_to_map:
            symbols_left_to_map.remove(from_index)
            continue

        # See we are taken
        line_vector = lines[from_index]
        to_vector = matrix * line_vector
        to_index = which_line(to_vector, lines)

        # It should always go to a line
        if to_index == None:
            raise ValueError("Found a vector not in any of the lines: " + str(to_vector))

        # If it goes somewhere else update the permutation
        if to_index in symbols_left_to_map:
            smaller = str(min(from_index, to_index))
            larger = str(max(from_index, to_index))
            swap = Permutation("(" + smaller + larger + ")", char_symbols)
            permutation = Permutation.compose(permutation, swap)
            from_index = to_index

        # Otherwise, find a new starting point
        else:
            from_index = symbols_left_to_map.pop()

    return permutation

lines_f4 = [
    Vector([F4("1"), F4("0")]),     # 0
    Vector([F4("0"), F4("1")]),     # 1
    Vector([F4("1"), F4("x")]),     # 2
    Vector([F4("1"), F4("1")]),     # 3
    Vector([F4("1"), F4("x + 1")])  # 4
]

lines_f5 = [
    Vector([F5("1"), F5("0")]), # 0
    Vector([F5("0"), F5("1")]), # 1
    Vector([F5("1"), F5("1")]), # 2
    Vector([F5("1"), F5("2")]), # 3
    Vector([F5("1"), F5("3")]), # 4
    Vector([F5("1"), F5("4")])  # 5
]

def isomorphism_tests():

    m_f4 = Matrix.from_list([[F4("1"), F4("x")], [F4("x + 1"), F4("0")]])
    matrix_permutation = matrix_to_permutation(m_f4, lines_f4)
    assert str(matrix_permutation) == "(041)"

    m_f5 = Matrix.from_list([[F5("1"), F5("3")], [F5("2"), F5("3")]])
    matrix_permutation = matrix_to_permutation(m_f5, lines_f5)
    assert str(matrix_permutation) == "(035412)"
