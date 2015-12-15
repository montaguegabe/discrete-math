"""
    Problem 12

    Gabe Montague

    Multiplies matrices of A6 together. This is a modified version of the programming
    project from the first homework, since the same logic works.
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
    stringList = ["("]
    #counter = 0
    while True:
      stringList.append(iterator.symbol)
      iterator = iterator.next
      if iterator.symbol == start:
        break
      #if counter > 5:
      #  break
      #counter += 1

    stringList.append(")")
    return "".join(stringList)

  def __str__(self):
    return repr(self)

# A permutation - a list of cycles and dictionary from symbol to cycles
class Permutation(object):
  def __init__(self, string, symbols):
    super(Permutation, self).__init__()

    symbols.reverse()

    # Represent the identity either way
    if string == "I": string = ""

    self.cycleList = []
    self.symbolDict = {}
    cycleOpenIndex = 0
    cycleElement = None
    lastAddedSymbol = None

    # The symbols that still have to be mapped
    symbolsLeftToMap = copy.deepcopy(symbols)

    # Iterate over the string
    for index in xrange(0, len(string)):
      char = string[index]
      if char == ')':
        continue
      
      nextChar = string[index + 1]  # Don't need to worry about out-of-bounds

      if char == '(':
        # Begin a new cycle
        lastAddedSymbol = ChainedSymbol(nextChar)
        symbolsLeftToMap.remove(nextChar)
        self.cycleList.append(lastAddedSymbol)
        cycleOpenIndex = index

      else:

        # Add to the existing cycle being constructed
        nextSymbol = None
        if nextChar == ')':

          # Close off the cycle
          nextSymbol = self.cycleList[-1]
        else:
          # Construct the next symbol, and remove from to-map set
          nextSymbol = ChainedSymbol(nextChar)
          symbolsLeftToMap.remove(nextChar)

        # Link
        lastAddedSymbol.next = nextSymbol
        nextSymbol.previous = lastAddedSymbol

        # Add to dictionary
        self.symbolDict[nextSymbol.symbol] = nextSymbol

        lastAddedSymbol = nextSymbol

    # Add remaining symbols as identity mappings
    for symbol in symbolsLeftToMap:
      chainedSymbol = ChainedSymbol(symbol)
      self.symbolDict[symbol] = chainedSymbol
      self.cycleList.append(chainedSymbol)

  # Returns a new permutation in reversed form
  def inverse(self):
    retPerm = copy.deepcopy(self)

    # Reverse next-previous relationship
    for _, chainedSymbol in retPerm.symbolDict.iteritems():
      previous = chainedSymbol.previous
      chainedSymbol.previous = chainedSymbol.next
      chainedSymbol.next = previous

    return retPerm

  # Prints in standard notation
  def __str__(self):
    def filterFn(chainedSymbol):
      return chainedSymbol.next != chainedSymbol

    def mapFn(chainedSymbol):
      return str(chainedSymbol)

    filteredList = filter(filterFn, self.cycleList)
    stringList = map(mapFn, filteredList)
    return "".join(stringList) if len(stringList) else "I"


# Returns the result of ba (permutations not strings)
def compose(b, a):

  # Symbols could be set to the union of a and b's symbols here
  aDict = a.symbolDict
  bDict = b.symbolDict

  #symbols = set(aDict.keys()).union(set(bDict.keys()))
  symbolsLeftToMap = copy.deepcopy(symbols)

  cycleList = []
  symbolDict = {}

  while symbolsLeftToMap:

    # Grab the next symbol to map
    seedSymbol = symbolsLeftToMap.pop()

    # Get the bijection in a that will serve as the starting point
    seedChainedSymbolA = aDict[seedSymbol]

    # Construct the beginning of a new cycle that will become ba and add it to list/dict
    currentChainedSymbolBA = ChainedSymbol(seedSymbol)
    cycleList.append(currentChainedSymbolBA)

    # Define an iterator in A
    currentChainedSymbolA = seedChainedSymbolA

    # Fill out the cycle that corresponds to the seed
    while True:

      # Get the next element specified by a
      nextA = currentChainedSymbolA.next

      # Look up that element in b, and determine the result of applying b
      resultBA = bDict[nextA.symbol].next
      resultSymbol = resultBA.symbol

      # Create an element in the seed's cycle, link it, add it to structures
      resultChainedSymbol = ChainedSymbol(resultSymbol)
      symbolDict[resultSymbol] = resultChainedSymbol  # Add to dictionary
      currentChainedSymbolBA.next = resultChainedSymbol
      resultChainedSymbol.previous = currentChainedSymbolBA

      # Advance the iterator in BA
      currentChainedSymbolBA = resultChainedSymbol

      # Set iterator to the new chained symbol in a
      currentChainedSymbolA = aDict[resultSymbol]

      # Break from the loop if we are back to where we started
      if currentChainedSymbolA == seedChainedSymbolA:
        break
      else:
        # If we are not back to the beginning, we need to mark the symbol as explored
        symbolsLeftToMap.remove(resultSymbol)

    # Round out the cycle by connecting the last element to the first
    currentChainedSymbolBA.previous.next = cycleList[-1]
    cycleList[-1].previous = currentChainedSymbolBA.previous
    symbolDict[seedSymbol] = cycleList[-1]  # Add the first chained symbol to the dict

  retPerm = Permutation("", [])
  retPerm.cycleList = cycleList
  retPerm.symbolDict = symbolDict

  return retPerm


