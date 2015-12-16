"""
START FIELDS.PY
"""

import copy

# The parent class of all fields
class Field(object):
    def __init__(self):
        super(Field, self).__init__()

    # Gets the identities
    @classmethod
    def mult_id(cls):
        raise NotImplementedError

    @classmethod
    def add_id(cls):
        raise NotImplementedError

# Define a normal number in the real numbers
class R(float):
    def __new__(cls, float_string):
        try: return float.__new__(cls, float_string)
        except (TypeError, ValueError): raise ValueError("Could not make float out of real number")

    @classmethod
    def mult_id(cls):
        return 1

    @classmethod
    def add_id(cls):
        return 0

# The parent class of all finite fields. Uses logarithm tables only for speed
class FiniteField(Field):

    # The characteristic
    characteristic = None

    # Number of copies of the characteristic cyclic group, max power + 1
    r = None

    # The generator of the logarithm table
    primitive = None

    # The logarithm table of the field. Access with method instead
    log_table = None
    log_table_reverse = None # Matches field members to generator orders

    # The irreducible polynomial of the field. Must have leading coefficient of 1
    irreducible_poly = None

    # Gets the identities
    @classmethod
    def mult_id(cls):
        return cls("1")

    @classmethod
    def add_id(cls):
        return cls("0")

    # Define a polynomial multiplier that does it the hard way
    @classmethod
    def poly_mult(cls, p1, p2):

        # Init the new polynomial
        order1 = len(p1) - 1
        order2 = len(p2) - 1
        new_order = order1 + order2

        # Carry out normal polynomial multiplication
        result = [0 for i in xrange(new_order + 1)]
        for power1, coef1 in enumerate(p1):
            for power2, coef2 in enumerate(p2):
                new_power = power1 + power2
                new_coef = (coef1 * coef2) % cls.characteristic
                result[new_power] += new_coef

        # Reduce by the polynomial
        irreducible_poly_order = len(cls.irreducible_poly) - 1
        if new_order > irreducible_poly_order:
            raise ValueError("Poly mult is not meant for this!")

        if new_order == irreducible_poly_order:
            x_to_order_equiv_neg = cls.irreducible_poly[:-1]
            factor = -result[irreducible_poly_order]
            del result[irreducible_poly_order]
            for power in xrange(len(result)):
                result[power] = (result[power] + (x_to_order_equiv_neg[power] * factor)) % cls.characteristic

            # Trim zeros off the end
            for i in xrange(len(result) - 1, 0, -1):
                if result[i] == 0:
                    del result[i]
                else:
                    break

        return result

    # Gets the size of the field
    @classmethod  
    def size(cls):
        return cls.characteristic ** cls.r

    # Gets all elements of the field (as an iterable). Returns in order of primitive powers
    @classmethod
    def all_values(cls):

        # Yield the additive identity first
        yield cls("0")

        # Then yield the multiplicative identity
        yield cls("1")

        # Iterate through the rest of the multiplicative group
        size_f_mult = cls.size() - 1
        value = cls("1")

        # Yield the subsequent powers
        iteration = 1
        while iteration < size_f_mult:

            # Compute the next element
            new_value = cls("0")
            new_value.coefficients = cls.poly_mult(value.coefficients, cls.primitive)
            value = new_value

            if value == cls.mult_id():
                raise ValueError("Invalid primitive element")
            yield value
            iteration += 1

    # Gets the logarithm table for the finite field
    @classmethod
    def get_log_table(cls):

        # Lazily compute the logarithm table
        if cls.log_table == None:

            log_table = []
            log_table_reverse = {}

            power = 0

            # Store finite field members in the table - not polynomial lists
            for value in cls.all_values():

                # The additive identity is not included in the log table
                if value == cls.add_id():
                    continue
                log_table.append(value)
                log_table_reverse[value] = power
                power += 1

            cls.log_table = log_table
            cls.log_table_reverse = log_table_reverse

        return cls.log_table

    # Maps field members to primitive order
    @classmethod
    def get_log_table_reverse(cls):
        cls.get_log_table()
        return cls.log_table_reverse

    # Create a polynomial from a string
    def __init__(self, string):
        super(FiniteField, self).__init__()

        # Store polynomial coefficients (of instances)
        self.coefficients = []

        compact = string.replace(" ", "")

        # Handle zero
        if compact == "0":
            self.coefficients.append(0)

        # Parse terms
        else:
            terms = compact.split("+")
            degree = -1
            for term in list(reversed(terms)):
                coef = None
                power = None

                # Attempt to split cleanly into coef and power
                coef_power = filter(None, term.split("x^"))
                if (len(coef_power) > 1):
                    coef = int(coef_power[0])
                    power = int(coef_power[1])

                else:
                    x_index = term.find("x")

                    if (x_index == -1):
                        # We simply have a constant
                        coef = int(term)
                        power = 0

                    else:
                        # There is an x
                        if term.find("^") == -1:

                            # Power is 1
                            power = 1
                            coef_string = term[:-1]
                            if coef_string == "-": coef_string = "-1"
                            coef = int(coef_string) if term[:-1] else 1
                        else:
                            # Coefficient is 1
                            coef = 1
                            power = int(term[2:])


                if coef == None or power == None:
                    raise ValueError("Could not parse input polynomial")

                # Add the term, first doing some padding with 0 coefficients if necessary
                while degree < power - 1:
                    self.coefficients.append(0)
                    degree += 1
                self.coefficients.append(coef % type(self).characteristic)
                degree = power

    # Adds two field members together
    def __add__(self, other):
        result = type(self)("0")
        result.coefficients = []

        self_coef_num = len(self.coefficients)
        other_coef_num = len(other.coefficients)
        result_coef_num = max(self_coef_num, other_coef_num)

        for power in xrange(result_coef_num):
            self_coef = self.coefficients[power] if power < self_coef_num else 0
            other_coef = other.coefficients[power] if power < other_coef_num else 0
            result.coefficients.append((self_coef + other_coef) % type(self).characteristic)

        # Trim zeros off the end
        for i in xrange(len(result.coefficients) - 1, 0, -1):
            if result.coefficients[i] == 0:
                del result.coefficients[i]
            else:
                break

        return result

    # Hashes a field member
    def __hash__(self):
        val = 0
        for power, coef in enumerate(self.coefficients):
            val += (type(self).characteristic ** power) * coef
        return val

    # Multiplies two field members together
    def __mul__(self, other):
        
        zero = type(self).add_id()
        if other == zero or self == zero: return zero

        prim_power_self = type(self).get_log_table_reverse()[self]
        prim_power_other = type(self).get_log_table_reverse()[other]
        prim_power_result = (prim_power_self + prim_power_other) % (type(self).size() - 1)

        return type(self).log_table[prim_power_result]

    # Divides two field members together
    def __div__(self, other):
        
        zero = type(self).add_id()
        if other == zero: return zero

        prim_power_self = type(self).get_log_table_reverse()[self]
        prim_power_other = -type(self).get_log_table_reverse()[other]
        prim_power_result = (prim_power_self + prim_power_other) % (type(self).size() - 1)

        return type(self).log_table[prim_power_result]

    # Defines equality between two fields
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.coefficients == other.coefficients
        else:
            return TypeError("Cannot compare these types")

    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return self.coefficients != other.coefficients
        else:
            return TypeError("Cannot compare these types")

    # Write the polynomial as a string
    def __unicode__(self):

        written_terms = []

        # Traverse coefficients in reverse order as we write them
        for power, coef in reversed(list(enumerate(self.coefficients))):

            # Add term to written terms
            if coef != 0:

                term = ""

                # Add the coefficient if necessary
                if coef != 1 or power == 0: term += str(coef)

                # Add the x if necessary
                if power != 0:
                    term += "x"

                # Add the power if necessary
                if power > 1:
                    term += "^" + str(power)

                written_terms.append(term)

        # No terms means zero
        if not written_terms: return "0"

        return " + ".join(written_terms)

    def __repr__(self):
        return self.__class__.__name__ + "(" + self.__unicode__() + ")"


class F4(FiniteField):
    characteristic = 2
    r = 2
    primitive = [0, 1]
    log_table = None
    log_table_reverse = None
    irreducible_poly = [1, 1, 1]

class F5(FiniteField):
    characteristic = 5
    r = 1
    primitive = [2]
    log_table = None
    log_table_reverse = None
    irreducible_poly = [0, 1] # This isn't used, but must have order 1

class F7(FiniteField):
    characteristic = 7
    r = 1
    primitive = [3]
    log_table = None
    log_table_reverse = None
    irreducible_poly = [0, 1] # This isn't used, but must have order 1

class F8(FiniteField):
    characteristic = 2
    r = 3
    primitive = [0, 1]
    log_table = None
    log_table_reverse = None
    irreducible_poly = [1, 1, 0, 1]

class F9(FiniteField):
    characteristic = 3
    r = 2
    primitive = [0, 1]
    log_table = None
    log_table_reverse = None
    irreducible_poly = [2, 2, 1]

class F16(FiniteField):
    characteristic = 2
    r = 4
    primitive = [0, 1]
    log_table = None
    log_table_reverse = None
    irreducible_poly = [1, 1, 0, 0, 1]

class F25(FiniteField):
    characteristic = 5
    r = 2
    primitive = [0, 1]
    log_table = None
    log_table_reverse = None
    irreducible_poly = [3, 3, 1]

class F27(FiniteField):
    characteristic = 3
    r = 3
    primitive = [0, 1]
    log_table = None
    log_table_reverse = None
    irreducible_poly = [1, 2, 0, 1]

class F32(FiniteField):
    characteristic = 2
    r = 5
    primitive = [0, 1]
    log_table = None
    log_table_reverse = None
    irreducible_poly = [1, 0, 1, 0, 0, 1]

class F49(FiniteField):
    characteristic = 7
    r = 2
    primitive = [0, 1]
    log_table = None
    log_table_reverse = None
    irreducible_poly = [3, 1, 1]
        

def field_tests():

    a4 = F4("x + 1")
    b4 = F4("x + 1")
    assert a4 * b4 == F4("x")
    assert a4 + b4 == F4("0")
    assert F4("0") + a4 == a4
    
    a9 = F9("x + 1")
    b9 = F9("x + 1")
    assert a9 * b9 == F9("2")

    a5 = F5("3")
    b5 = F5("3")
    assert a5 * b5 == F5("4")
    assert a5 + b5 == F5("1")

    a7 = F7("3")
    b7 = F7("4")
    assert a7 * b7 == F7("5")
    assert a7 + b7 == F7("0")

    a8 = F8("x^2 + 1")
    b8 = F8("x")
    assert a8 * b8 == F8("1")
    assert a8 + b8 == F8("x^2 + x + 1")
    assert (a8 / b8) * b8 == a8
    assert b8 * (F8("1") / b8) == F8("1")

    a16 = F16("x^3 + 1")
    b16 = F16("x + 1")
    c16 = F16("0")
    assert a16 * b16 == F16("x^3")
    assert a16 * c16 == F16("0")

    a25 = F25("2x + 3")
    b25 = F25("4x + 1")
    c25 = F25("2")
    assert a25 * b25 == F25("4")
    assert a25 + b25 == F25("x + 4")
    assert b25 * b25 == F25("3")
    assert b25 * c25 == F25("3x + 2")

    a27 = F27("x^2 + 2")
    b27 = F27("2x")
    assert a27 * b27 == F27("1")

    a32 = F32("x^3 + x^2 + 1")
    b32 = F32("x^3 + x")
    assert a32 * b32 == F32("x^4 + x^3 + x^2 + 1")

    a49 = F49("6x + 5")
    b49 = F49("6x + 6")
    assert a49 * b49 == F49("2x + 6")
    assert a49 + b49 == F49("5x + 4")
    assert F49("6x") + F49("1") == F49("6x + 1")


"""
END FIELDS.PY
"""
"""
START PERMUTATION.PY
"""

import copy

# A doubly-linked symbol, also representing a cycle
class ChainedSymbol(object):

    def __init__(self, symbol):
        super(ChainedSymbol, self).__init__()
        self.symbol = symbol
        self.next = self
        self.previous = self

    def __repr__(self):
        iterator = self
        start = self.symbol
        string_list = ['(']

        while True:
            string_list.append(iterator.symbol)
            iterator = iterator.next
            if iterator.symbol == start:
                break

        string_list.append(')')
        return ''.join(string_list)

    def __str__(self):
        return repr(self)


# A permutation - a list of cycles and dictionary from symbol to cycles
class Permutation(object):

    def __init__(self, string, symbols):
        super(Permutation, self).__init__()

        # Represent the identity either way
        if string == 'I':
            string = ''

        self.cycle_list = []
        self.symbol_dict = {}
        cycle_open_index = 0
        cycle_element = None
        last_added_symbol = None

        # The symbols that still have to be mapped
        symbols_left_to_map = copy.deepcopy(symbols)

        # Iterate over the string
        for index in xrange(0, len(string)):
            char = string[index]
            if char == ')':
                continue

            next_char = string[index + 1]  # Don't need to worry about out-of-bounds

            if char == '(':

                # Begin a new cycle
                last_added_symbol = ChainedSymbol(next_char)
                symbols_left_to_map.remove(next_char)
                self.cycle_list.append(last_added_symbol)
                cycle_open_index = index

            else:

                # Add to the existing cycle being constructed
                next_symbol = None
                if next_char == ')':

                    # Close off the cycle
                    next_symbol = self.cycle_list[-1]

                else:

                    # Construct the next symbol, and remove from to-map set
                    next_symbol = ChainedSymbol(next_char)
                    symbols_left_to_map.remove(next_char)

                # Link
                last_added_symbol.next = next_symbol
                next_symbol.previous = last_added_symbol

                # Add to dictionary
                self.symbol_dict[next_symbol.symbol] = next_symbol
                last_added_symbol = next_symbol

        # Add remaining symbols as identity mappings
        for symbol in symbols_left_to_map:
            chained_symbol = ChainedSymbol(symbol)
            self.symbol_dict[symbol] = chained_symbol
            self.cycle_list.append(chained_symbol)

    # Returns a new permutation in reversed form
    def inverse(self):
        result = copy.deepcopy(self)

        # Reverse next-previous relationship
        for (_, chained_symbol) in result.symbol_dict.iteritems():
            previous = chained_symbol.previous
            chained_symbol.previous = chained_symbol.next
            chained_symbol.next = previous

        return result

    # Prints in standard notation
    def __str__(self):

        def filterer(chained_symbol):
            return chained_symbol.next != chained_symbol

        def mapper(chained_symbol):
            return str(chained_symbol)

        filtered_list = filter(filterer, self.cycle_list)
        string_list = map(mapper, filtered_list)
        return (''.join(string_list) if len(string_list) else 'I')


    # Returns the result of ba (permutations not strings)
    @staticmethod
    def compose(b, a, sort_output=True):

        # Symbols could be set to the union of a and b's symbols here
        a_dict = a.symbol_dict
        b_dict = b.symbol_dict

        symbols_union = set(a_dict.keys()).union(set(b_dict.keys()))
        symbols = sorted(list(symbols_union), reverse=True) if sort_output else list(symbols_union)
        symbols_left_to_map = copy.deepcopy(symbols)

        cycle_list = []
        symbol_dict = {}

        while symbols_left_to_map:

            # Grab the next symbol to map
            seed_symbol = symbols_left_to_map.pop()

            # Get the bijection in a that will serve as the starting point
            seed_chained_symbol_a = a_dict[seed_symbol]

            # Construct the beginning of a new cycle that will become ba and add it to list/dict
            current_chained_symbol_ba = ChainedSymbol(seed_symbol)
            cycle_list.append(current_chained_symbol_ba)

            # Define an iterator in A
            current_chained_symbol_a = seed_chained_symbol_a

            # Fill out the cycle that corresponds to the seed
            while True:

                # Get the next element specified by a
                next_a = current_chained_symbol_a.next

                # Look up that element in b, and determine the result of applying b
                result_ba = b_dict[next_a.symbol].next
                result_symbol = result_ba.symbol

                # Create an element in the seed's cycle, link it, add it to structures
                resultChainedSymbol = ChainedSymbol(result_symbol)
                symbol_dict[result_symbol] = resultChainedSymbol  # Add to dictionary
                current_chained_symbol_ba.next = resultChainedSymbol
                resultChainedSymbol.previous = current_chained_symbol_ba

                # Advance the iterator in BA
                current_chained_symbol_ba = resultChainedSymbol

                # Set iterator to the new chained symbol in a
                current_chained_symbol_a = a_dict[result_symbol]

                # Break from the loop if we are back to where we started
                if current_chained_symbol_a == seed_chained_symbol_a:
                    break
                else:

                    # If we are not back to the beginning, we need to mark the symbol as explored
                    symbols_left_to_map.remove(result_symbol)

            # Round out the cycle by connecting the last element to the first
            current_chained_symbol_ba.previous.next = cycle_list[-1]
            cycle_list[-1].previous = current_chained_symbol_ba.previous
            symbol_dict[seed_symbol] = cycle_list[-1]  # Add the first chained symbol to the dict

        result = Permutation('', [])
        result.cycle_list = cycle_list
        result.symbol_dict = symbol_dict

        return result


def permutation_tests():

    indices = range(5)
    symbols = map(str, indices)
    symbols = ["0", "1", "2", "3", "4"]
    pId = Permutation("I", symbols)
    p = Permutation("(14)", symbols)

    assert str(Permutation.compose(pId, p)) == "(14)"

    # ...

    
"""
END PERMUTATION.PY
""" 
"""
START MATRIX.PY
"""

import copy
"""from fields import *"""

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
        result = "["
        length = len(self.list_form)
        for i, v in enumerate(self.list_form):
            result += unicode(v) + (", " if i != length - 1 else "")
        result += "]"
        return result

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
            result += unicode(self.get_row(r))
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

"""
END MATRIX.PY
"""
"""
START ISOMORPHISM.PY
"""

"""from permutation import *
from matrix import *
from fields import *"""

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


"""
END ISOMORPHISM.PY
"""
"""
START __MAIN__.PY
"""

"""from permutation import *
from fields import *
from matrix import *
from isomorphism import *"""
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
for i in xrange(1): #while True:

    field_string = "F8" #raw_input("Enter in a field name e.g. F32, *OR leave empty* to move on to the next question.\n> ")
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

    a_string = "x^2 + 1" #raw_input("\nSpecify first field member in standard polynomial order. Use smallest positive integer for coefficients (e.g. x^2 + 1).\n> a = ")
    b_string = "x" #raw_input("\nSpecify second field member in standard polynomial order. Use smallest positive integer for coefficients (e.g. x^2 + 1).\n> b = ")

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
for i in xrange(1): #while True:

    field_string = "F7" #raw_input("Enter in a field name *OR leave empty* to move on to the next question.\n> ")
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
    a1_str = "3" #raw_input("> a = [[")
    a2_str = "6" #raw_input(CURSOR_UP_ONE + ERASE_LINE + "> a = [[" + a1_str + ", ")
    a3_str = "1" #raw_input(CURSOR_UP_ONE + ERASE_LINE + "> a = [[" + a1_str + ", " + a2_str + "], [")
    a4_str = "2" #raw_input(CURSOR_UP_ONE + ERASE_LINE + "> a = [[" + a1_str + ", " + a2_str + "], [" + a3_str + ", ")
    print CURSOR_UP_ONE + ERASE_LINE + "> a = [[" + a1_str + ", " + a2_str + "], [" + a3_str + ", " + a4_str + "]]\n"

    a = Matrix.from_list([[cls(a1_str), cls(a2_str)], [cls(a3_str), cls(a4_str)]])

    print("\nSpecify second matrix entry by entry, in reading order. Use field-specifying rules from before.")
    b1_str = "3" #raw_input("> b = [[")
    b2_str = "0" #raw_input(CURSOR_UP_ONE + ERASE_LINE + "> b = [[" + b1_str + ", ")
    b3_str = "1" #raw_input(CURSOR_UP_ONE + ERASE_LINE + "> b = [[" + b1_str + ", " + b2_str + "], [")
    b4_str = "5" #raw_input(CURSOR_UP_ONE + ERASE_LINE + "> b = [[" + b1_str + ", " + b2_str + "], [" + b3_str + ", ")
    print CURSOR_UP_ONE + ERASE_LINE + "> b = [[" + b1_str + ", " + b2_str + "], [" + b3_str + ", " + b4_str + "]]\n"

    b = Matrix.from_list([[cls(b1_str), cls(b2_str)], [cls(b3_str), cls(b4_str)]])

    print "a * b =", unicode(a * b)


print "EXPLORATORY PROBLEMS 3: #12 - MATRIX ISOMORPHISMS (Permutations)"
for i in xrange(1): # while True:

    f_string = "(123)(45)" #raw_input("Enter in a permutation in cycle notation (can be of A6) *OR leave empty* to move on to the next question. I is the identity.\n> f = ")
    if not f_string: break

    g_string = "(124)(35)" #raw_input("Enter in another permutation in cycle notation (can be of A6). I is the identity.\n> g = ")

    symbols = map(str, list(range(1, 10)))
    f = Permutation(f_string, symbols)
    g = Permutation(g_string, symbols)

    print "g * f = ", Permutation.compose(g, f)
    print "f * g = ", Permutation.compose(f, g)
    print ""


print "EXPLORATORY PROBLEMS 3: #12 - MATRIX ISOMORPHISMS (Matrix -> Permutation)"
for i in xrange(1): #while True:
    field_string = "F4" #raw_input("Enter in a field name: either F4 or F5, *OR leave empty* to move on to the next question.\n> ")
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
    a1_str = "x" #raw_input("> m = [[")
    a2_str = "1" #raw_input(CURSOR_UP_ONE + ERASE_LINE + "> m = [[" + a1_str + ", ")
    a3_str = "x+1" #raw_input(CURSOR_UP_ONE + ERASE_LINE + "> m = [[" + a1_str + ", " + a2_str + "], [")
    a4_str = "0" #raw_input(CURSOR_UP_ONE + ERASE_LINE + "> m = [[" + a1_str + ", " + a2_str + "], [" + a3_str + ", ")
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
        print str(symbol) + ":", line
    print ""

print "EXPLORATORY PROBLEMS 3: #12 - MATRIX ISOMORPHISMS (Demonstrate isomorphism)"
for i in xrange(1): #while True:
    field_string = "F5" #raw_input("Enter in a field name: either F4 or F5, *OR leave empty* to move on to the next question.\n> ")
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



"""
END __MAIN__.PY
"""