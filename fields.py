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
        return 1

    @staticmethod
    def add_id():
        return 0

# The parent class of all finite fields. Uses logarithm tables only for speed
class FiniteField(Field):

    # The characteristic
    char = None

    # Number of copies of the characteristic cyclic group, max power + 1
    r = None

    # The generator of the logarithm table
    primitive = None

    # The logarithm table of the field. Access with method instead
    log_table = None
    log_table_reverse = None # Matches field members to generator orders

    # The irreducible polynomial of the field. Must have leading coefficient of 1
    irreducible_poly = None

    # Define a polynomial multiplier that does it the hard way
    @staticmethod
    def poly_mult(p1, p2):

        # Init the new polynomial
        order1 = len(p1) - 1
        order2 = len(p2) - 1
        new_order = order1 + order2

        # Carry out normal polynomial multiplication
        result = [0 for i in xrange(new_order + 1)]
        for power1, coef1 in enumerate(p1):
            for power2, coef2 in enumerate(p2):
                new_power = power1 + power2
                new_coef = (coef1 * coef2) % characteristic
                result[new_power] += new_coef

        # Reduce by the polynomial
        irreducible_poly_order = len(irreducible_poly) - 1
        if new_order > irreducible_poly_order:
            raise ValueError("Poly mult is not meant for this!")

        x_to_order_equiv_neg = irreducible_poly[:-1]
        factor = -result[-1]
        for power in xrange(len(x_to_order_equiv_neg)):
            result[power] += (x_to_order_equiv_neg[power] * factor)

        return result

    # Gets the size of the field
    @staticmethod  
    def size():
        return char ** r

    # Gets all elements of the field (as an iterable). Returns in order of primitive powers
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
            if value == mult_id:
                raise ValueError("Invalid primitive element")
            yield value
            iteration += 1

    # Gets the logarithm table for the finite field
    @staticmethod
    def get_log_table():

        # Lazily compute the logarithm table
        if log_table == None:

            log_table = []
            log_table_reverse = {}

            power = 0

            for value in all_values():

                # The additive identity is not included in the log table
                if value == add_id: continue
                log_table.append(value)
                log_table_reverse[value] = power
                power += 1

        return log_table

    # Maps field members to primitive order
    @staticmethod
    def get_log_table_reverse():
        get_log_table()
        return log_table_reverse

    # Create a polynomial from a string
    def __init__(self, string):
        super(FiniteField, self).__init__()

        # Compute the log table if haven't already
        get_log_table()

        # Store polynomial coefficients (of instances)
        self.coefficients = []

        compact = string.replace(" ", "")

        # Handle zero
        if compact != "0":
            self.coefficients.append(0)

        # Parse terms
        else:
            terms = text.split("+")
            degree = -1
            for term in list(reversed(terms)):

                coef = None
                power = None

                # Attempt to split cleanly into coef and power
                coef_power = "x^".split(term)
                if (len(coef_power > 1)):
                    coef = int(coef_power[0])
                    power = int(coef_power[1])

                else:
                    x_index = term.find("x")

                    if (x_index == -1):

                        # We simply have a constant
                        coef = int(term)
                        power = 0

                    else:

                        # We only have a power
                        coef = 1
                        power = 1 if term.find("^") == -1 else int(term[2:])

                if coef == None or power == None:
                    raise ValueError("Could not parse input polynomial")

                # Add the term, first doing some padding with 0 coefficients if necessary
                while degree < power - 1:
                    self.coefficients.append(0)
                self.coef_power.append(coef)

    # Adds two field members together
    def __add__(self, other):
        result = copy.deepcopy(self)

        for power, coef in enumerate(other.coefficients):
            result[power] = (result[power] + coef) % characteristic

        return result

    # Hashes a field member
    def __hash__(self):
        val = 0
        for power, coef in enumerate(self.coefficients):
            val += (characteristic ** power) * coef
        return val

    # Multiplies two field members together
    def __mul__(self, other):
        
        prim_power_self = log_table_reverse[self]
        prim_power_other = log_table_reverse[other]
        prim_power_result = (prim_power_self + prim_power_other) % size()
        return log_table[prim_power_result]

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
        if not terms: return "0"

        return " + ".join(terms)

    def __repr__(self):
        return self.__class__.__name__ + "(" + self.__unicode__() + ")"




# Define F4

field_tests: