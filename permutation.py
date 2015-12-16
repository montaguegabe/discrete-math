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


permutation_tests()        