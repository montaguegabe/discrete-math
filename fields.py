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
                self.coefficients.append(coef)
                degree = power

    # Adds two field members together
    def __add__(self, other):
        result = copy.deepcopy(self)

        for power, coef in enumerate(other.coefficients):
            result.coefficients[power] = (result.coefficients[power] + coef) % type(self).characteristic

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
        if other == zero: return zero

        prim_power_self = type(self).get_log_table_reverse()[self]
        prim_power_other = type(self).get_log_table_reverse()[other]
        prim_power_result = (prim_power_self + prim_power_other) % (type(self).size() - 1)

        return type(self).log_table[prim_power_result]

    # Defines equality between two fields
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.coefficients == other.coefficients
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


# Define F4
class F4(FiniteField):

    # The characteristic
    characteristic = 2

    # Number of copies of the characteristic cyclic group, max power + 1
    r = 2

    # The generator of the logarithm table
    primitive = [0, 1] # x

    # The logarithm table of the field. Access with method instead
    log_table = None
    log_table_reverse = None # Matches field members to generator orders

    # The irreducible polynomial of the field. Must have leading coefficient of 1
    irreducible_poly = [1, 1, 1]

    # Gets the identities
    @classmethod
    def mult_id(cls):
        return F4("1")

    @classmethod
    def add_id(cls):
        return F4("0")

    def __init__(self, string):
        super(F4, self).__init__(string)
        

def field_tests():

    a = F4("x + 1")
    b = F4("x + 1")

    assert a * b == F4("x")
    assert a + b == F4("0")
    


field_tests()
