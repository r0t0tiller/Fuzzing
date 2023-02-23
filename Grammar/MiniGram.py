import re
import random

Grammar = {
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

start_symbol = "$START"
RE_NONTERMINAL = re.compile(r'(\$[a-zA-Z_]*)')

def possible_expansions(tree):
    (symbol, children) = tree
    if children is None:
        return 1

    number_of_expansions = sum(possible_expansions(c) for c in children)
    return number_of_expansions

def expansion_to_children(expansion):
    strings  = re.split(RE_NONTERMINAL, expansion)
    return [(s, None) if is_symbol(s) else (s, []) for s in strings if s]

def min_expansions(expansion, grammar, seen=set()):
    symbols  = [s for s in re.findall(RE_NONTERMINAL, expansion)
            if is_symbol(s)]

    if not symbols: 
        return 1

    if any(s in seen for s in symbols):
        return float('inf')

    return sum(symbol_min_cost(s, grammar, seen) for s in symbols) + 1

def symbol_min_cost(nt, grammar, seen=set()):
    expansions = grammar[nt]
    return min(min_expansions(e, grammar, seen | {nt}) for e in expansions)

def is_symbol(s):
    return s[0] == '$'

def expand_node(node, grammar, fast_path):
    (symbol, children) = node

    expansions = grammar[symbol]

    possible_children_with_len = [(expansion_to_children(expansion),
                                   min_expansions(expansion, grammar, {symbol}))
                                  for expansion in expansions]

    min_len = min(s[1] for s in possible_children_with_len)

    shortest_children = [child for (child, clen) in possible_children_with_len
                            if clen == min_len]
    if fast_path:
        children = random.choice(shortest_children)
    else:
        children, _ = random.choice(possible_children_with_len)

    return (symbol, children)

def expand_tree_once(tree, grammar, fast_path):
    (symbol, children) = tree

    if children is None:
        return expand_node(tree, grammar, fast_path)

    expandable_children = [i for (i,c) in enumerate(children) if possible_expansions(c)]
    child_to_be_expanded = random.choice(expandable_children)

    new_child = expand_tree_once(children[child_to_be_expanded], grammar, fast_path)
    
    new_children = (children[:child_to_be_expanded] + 
                    [new_child] +
                    children[child_to_be_expanded + 1:])
                    
    new_tree = (symbol, new_children)

    return new_tree

def expand_tree(tree, grammar, depth):

    while 0 < possible_expansions(tree) < depth:
        tree = expand_tree_once(tree, grammar, False)
        
    while possible_expansions(tree):
        tree = expand_tree_once(tree, grammar, True)

    return tree

def all_terminals(tree):
    (symbol, children) = tree
    if children is None:
        return symbol
    
    if len(children) == 0:
        return symbol
    
    return ''.join([all_terminals(c) for c in children])

def init_tree():
    return (start_symbol, None)

def fuzz():

    tree = init_tree()
    tree = expand_tree(tree, Grammar, 10)
    final = all_terminals(tree)
    return final

while True:
    print(fuzz())