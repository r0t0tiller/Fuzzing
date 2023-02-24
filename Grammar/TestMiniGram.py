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

class TreeNode:
    def __init__(self, symbol):
        self.symbol = symbol
        self.children = []

class MiniGrammar:
    def __init__(self):
        self = self
        self.queue = set()
        self.depth = 0

    def setup_tree(self):
        tree = TreeNode(start_symbol)
        return tree
    
    def expand_tree(self, tree, grammar, symbol, depth):

        if self.depth == depth:
            return

        current_expansion = grammar[symbol]

        for expansion in current_expansion:
            unwrapped_expansions = re.findall(RE_NONTERMINAL, expansion)
            for new_expansion in unwrapped_expansions:
                self.queue.add(new_expansion)
            
        new_expansion = self.queue.pop()
            
        tree.children.append(TreeNode(current_expansion))
        
        self.depth += 1

        return self.expand_tree(tree, grammar, new_expansion, depth)

    def expand_children(self, tree, grammar):
        for x in tree.children:
            symbol = random.choice(x.symbol)
            if "$" in symbol:
                self.expand_tree(tree, grammar, symbol, depth=10)
        
        for x in tree.children:
            for y in x.symbol:
                print(y)
        

gram = MiniGrammar()
tree = gram.setup_tree()

gram.expand_tree(tree, Grammar, start_symbol, 10)

gram.expand_children(tree, Grammar)
