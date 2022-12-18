# Example from: https://github.com/vrthra/pygenfuzz

#!/usr/bin/env python3
# Use a grammar to fuzz, using derivation trees

import random
import re
import sys
import json
import string

# We define a grammar as mappings of nonterminals into possible expansions.
# Possible expansions come as a list of alternatives

json_grammar = {
    "$START":
        ["$OBJECT", "$ARRAY"],

    "$OBJECT":
        ["{}", "{$MEMBERS}"],

    "$MEMBERS":
        ["$PAIR", "$PAIR,$MEMBERS"],

    "$PAIR":
        ["$STRING:$VALUE"],

    "$ARRAY":
        ["[]","[$ELEMENTS]"],

    "$ELEMENTS":
        ["$VALUE", "$VALUE,$ELEMENTS"],

    "$VALUE":
        ["$STRING", "$NUMBER", "$OBJECT", "$ARRAY", "true", "false", " null"],

    "$STRING":
        ["\"\"", "\"$CHARS\""],
    
    "$CHARS":
        ["$CHAR", "$CHARS"],
    
    "$CHAR":
       [c for c in string.printable if c not in ["\"", "\\", "$", "\n", "\r", "\v", "\f"]],

    "$NUMBER":
        ["$INT", "$INT$FRAC", "$INT$EXP", "$INT$FRAC$EXP"],

    "$INT":
        ["$DIGIT$DIGITS", "-$DIGIT$DIGITS"],

    "$FRAC":
        [".$DIGITS"],

    "$EXP":
        ["$E$DIGITS"],

    "$DIGITS":
        ["$DIGIT$DIGITS", "$DIGIT"],

    "$DIGIT":
       [c for c in string.digits],

    "$E":
        ["e", "e+", "e-", "E", "E+", "E-"]

}

term_grammar = {
    "$START":
        ["$EXPR"],

    "$EXPR":
        ["$EXPR + $TERM", "$EXPR - $TERM", "$TERM"],
    
    "$TERM":
        ["$TERM * $FACTOR", "$TERM / $FACTOR", "$FACTOR"],
    
    "$FACTOR":
        ["+$FACTOR", "-$FACTOR", "($EXPR)", "$INTEGER", "$INTEGER.$INTEGER"],

    "$INTEGER":
        ["$INTEGER$DIGIT", "$DIGIT"],

    "$DIGIT":
        ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
}

html_grammar = {
    "$START":
        ["$DOCUMENT"],
    
    "$DOCUMENT":
        ["$DOCTYPE$HTML"],

    "$DOCTYPE":
        ['<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN"\n' + \
         '"http://www.w3.org/TR/html4/strict.dtd">\n'],

    "$HTML":
        ["<HTML>$HEAD$BODY</HTML>\n"],

    "$HEAD":
        ["<HEAD>$TITLE</HEAD>\n"],
        
    "$TITLE":
        ["<TITLE>A generated document</TITLE>\n"],

    "$BODY":
        ["<BODY>$DIVS</BODY>\n"],

    "$DIVS":
        ["$A_DIV", "$A_DIV\n$DIVS"],

    "$A_DIV":
        ["$A_HEADER\n$LIST"],

    "$A_HEADER":
        ["<H1>A header.</H1>", "<H1>Another header.</H1>"],

    "$LIST": 
        ["<UL>$ITEMS</UL>", "<OL>$ITEMS</OL>"],
    
    "$ITEMS":
        ["$AN_ITEM", "$AN_ITEM$ITEMS"],
    
    "$AN_ITEM":
        ["<LI>$TEXT</LI>\n"],

    "$TEXT":
        ["An item", "Another item"]
}

# A regular expression matching the nonterminals used in this grammar
RE_NONTERMINAL = re.compile(r'(\$[a-zA-Z_]*)')

# For debugging:
DEBUG = False
def log(s):
    if DEBUG:
        print(s() if callable(s) else s)


# cache the function calls. We only cache a given call based on the
# indicated argument number per function.
def memoize(argnum):
    def fn_wrap(function):
        memo = {}
        def wrapper(*args):
            if args[argnum] in memo: return memo[args[argnum]]
            rv = function(*args)
            memo[args[argnum]] = rv
            return rv
        return wrapper
    return fn_wrap

# The minimum cost of expansion of this symbol
@memoize(0) # memoize on the first arg
def symbol_min_cost(nt, grammar, seen=set()):
    expansions = grammar[nt]
    return min(min_expansions(e, grammar, seen | {nt}) for e in expansions)

# The minimum cost of expansion of this rule
@memoize(0)
def min_expansions(expansion, grammar, seen=set()):
    symbols  = [s for s in re.findall(RE_NONTERMINAL, expansion)
            if is_symbol(s)]
    # at least one expansion has no variable to expand.
    if not symbols: return 1

    # if a variable present in the expansion is already in the stack, then it is
    # recursion
    if any(s in seen for s in symbols): return float('inf')
    # the value of a expansion is the sum of all expandable variables inside + 1
    return sum(symbol_min_cost(s, grammar, seen) for s in symbols) + 1


# We create a derivation tree with nodes in the form (SYMBOL, CHILDREN)
# where SYMBOL is either a nonterminal or terminal,
# and CHILDREN is 
# - a list of children (for nonterminals)
# - an empty list for terminals
# - None for nonterminals that are yet to be expanded
# Example:
# ("$START", None) - the initial tree with just the root node
# ("$START", [("$EXPR", None)]) - expanded once into $START -> $EXPR
# ("$START", [("$EXPR", [("$EXPR", None]), (" + ", []]), ("$TERM", None])]) -
#     expanded into $START -> $EXPR -> $EXPR + $TERM

# Return an initialized tree
def init_tree(start_symbol = "$START"):
    return (start_symbol, None)

def is_symbol(s):
    return s[0] == '$'
    
# Convert an expansion rule to children
@memoize(0)
def expansion_to_children(expansion):
    # print("Converting " + repr(expansion))
    # strings contains all substrings -- both terminals and non-terminals such
    # that ''.join(strings) == expansion
    strings  = re.split(RE_NONTERMINAL, expansion)
    return [(s, None) if is_symbol(s) else (s, []) for s in strings if s]
    
# Expand a node
def expand_node(node, grammar, prefer_shortest_expansion):
    (symbol, children) = node
    # print("Expanding " + repr(symbol))
    assert children is None
    
    # Fetch the possible expansions from grammar...
    expansions = grammar[symbol]
    possible_children_with_len = [(expansion_to_children(expansion),
                                   min_expansions(expansion, grammar, {symbol}))
                                  for expansion in expansions]
    min_len = min(s[1] for s in possible_children_with_len)
    
    # ...as well as the shortest ones
    shortest_children = [child for (child, clen) in possible_children_with_len
                               if clen == min_len]
    
    # Pick a child randomly
    if prefer_shortest_expansion:
        children = random.choice(shortest_children)
    else:
        # TODO: Consider preferring children not expanded yet, 
        # and other forms of grammar coverage (or code coverage)
        children, _ = random.choice(possible_children_with_len)

    # Return with a new list
    return (symbol, children)
    
# Count possible expansions - 
# that is, the number of (SYMBOL, None) nodes in the tree
def possible_expansions(tree):
    (symbol, children) = tree
    if children is None:
        return 1

    number_of_expansions = sum(possible_expansions(c) for c in children)
    return number_of_expansions

# short circuit. any will return for the first item that is true without
# evaluating the rest.
def any_possible_expansions(tree):
    (symbol, children) = tree
    if children is None: return True

    return any(any_possible_expansions(c) for c in children)
    
# Expand the tree once
def expand_tree_once(tree, grammar, prefer_shortest_expansion):
    (symbol, children) = tree
    if children is None:
        # Expand this node
        return expand_node(tree, grammar, prefer_shortest_expansion)

    # print("Expanding tree " + repr(tree))

    # Find all children with possible expansions
    expandable_children = [i for (i, c) in enumerate(children) if any_possible_expansions(c)]
    
    # Select a random child
    # TODO: Various heuristics for choosing a child here, 
    # e.g. grammar or code coverage
    child_to_be_expanded = random.choice(expandable_children)
    
    # Expand it
    new_child = expand_tree_once(children[child_to_be_expanded], grammar, prefer_shortest_expansion)

    new_children = (children[:child_to_be_expanded] + 
                    [new_child] +
                    children[child_to_be_expanded + 1:])
    
    new_tree = (symbol, new_children)

    # print("Expanding tree " + repr(tree) + " into " + repr(new_tree))

    return new_tree
    
# Keep on applying productions
# We limit production by the number of minimum expansions
# alternate limits (e.g. length of overall string) are possible too
def expand_tree(tree, grammar, max_symbols):
    # Stage 1: Expand until we reach the max number of symbols
    log("Expanding")
    while 0 < possible_expansions(tree) < max_symbols:
        tree = expand_tree_once(tree, grammar, False)
        log(lambda: all_terminals(tree))
        
    # Stage 2: Keep on expanding, but now focus on the shortest expansions
    log("Closing")
    while any_possible_expansions(tree):
        tree = expand_tree_once(tree, grammar, True)
        log(lambda: all_terminals(tree))

    return tree
    
# The tree as a string
def all_terminals(tree):
    (symbol, children) = tree
    if children is None:
        # This is a nonterminal symbol not expanded yet
        return symbol
    
    if len(children) == 0:
        # This is a terminal symbol
        return symbol
    
    # This is an expanded symbol:
    # Concatenate all terminal symbols from all children
    return ''.join([all_terminals(c) for c in children])

# All together
def produce(grammar, max_symbols = 10):
    # Create an initial derivation tree
    tree = init_tree()
    # print(tree)

    # Expand all nonterminals
    tree = expand_tree(tree, grammar, max_symbols)
    # print(tree)
    
    # Return the string
    return all_terminals(tree)

def using(fn):
    with fn as f: yield f

if __name__ == "__main__":
    # The grammar to use
    grammar = term_grammar
    _symbols,*rest = sys.argv[2:] or ['10']
    symbols = int(_symbols)
    _count, = rest or [1]
    count = int(_count)
    for i in range(count):
        print(produce(grammar, int(symbols)))