import re
import random

Grammar = {
    "<start>":
        ["<expr>"],

    "<expr>":
        ["<term> + <expr>", "<term> - <expr>", "<term>"],

    "<term>":
        ["<factor> * <term>", "<factor> / <term>", "<factor>"],

    "<factor>":
        ["+<factor>",
         "-<factor>",
         "(<expr>)",
         "<integer>.<integer>",
         "<integer>"],

    "<integer>":
        ["<digit><integer>", "<digit>"],

    "<digit>":
        ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
}

START_SYMBOL = "<start>"
RE_NONTERMINAL = re.compile(r'(<[^<> ]*>)')

def nonterminals(expansion):
    return RE_NONTERMINAL.findall(expansion)

def fuzz(depth, attempts):
    term = START_SYMBOL
    while len(nonterminals(term)) > 0:
        
        # print("term: " + str(term))

        symbol_to_expand = random.choice(nonterminals(term))
        expansions = Grammar[symbol_to_expand]
        expansion = random.choice(expansions)

        new_term = term.replace(symbol_to_expand, expansion, 1)

        # print("symbol_to_expand: " + str(symbol_to_expand))
        # print("expansions: " + str(expansions))
        # print("expansion: " + str(expansion))
        # print("new_term: " + str(new_term))

        # input()

        if len(nonterminals(new_term)) < depth:
            term = new_term
            expansion_trials = 0
        else:
            expansion_trials += 1
            if expansion_trials >= attempts:
                return None
    return term

print(fuzz(10, 10))