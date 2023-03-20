use std::collections::BTreeMap;

pub static mut GRAMMAR: BTreeMap<&str, Vec<&str>> = BTreeMap::new();

#[allow(dead_code)]
pub fn load_expr_grammar() {
    unsafe {
        GRAMMAR.insert(
            "<EXPR>",
            vec![
                "<INT><SYMBOL><INT>",
                "(<INT><SYMBOL><INT>)",
                "(<EXPR><EXPR>)",
            ],
        );
        GRAMMAR.insert("<INT>", vec!["<DIGIT>", "-<DIGIT>", "<FLOAT>"]);
        GRAMMAR.insert("<FLOAT>", vec!["<DIGIT>.<DIGIT>", "-<DIGIT>.<DIGIT>"]);
        GRAMMAR.insert("<SYMBOL>", vec!["+", "-", "*", "/"]);
        GRAMMAR.insert(
            "<DIGIT>",
            vec!["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"],
        );
    }
}

#[allow(dead_code)]
pub fn load_json_grammar() {
    unsafe {
        GRAMMAR.insert("<JSON>", vec!["<OBJECT>", "<ARRAY>"]);
        GRAMMAR.insert("<OBJECT>", vec!["{}", "{<MEMBERS>}", "[<JSON>]"]);
        GRAMMAR.insert("<MEMBERS>", vec!["<PAIR>", "<PAIR>,<MEMBERS>"]);
        GRAMMAR.insert("<PAIR>", vec!["<STRING>:<VALUE>"]);
        GRAMMAR.insert("<ARRAY>", vec!["[]", "[<ELEMENTS>]"]);
        GRAMMAR.insert("<ELEMENTS>", vec!["<VALUE>", "<VALUE>,<ELEMENTS>"]);
        GRAMMAR.insert(
            "<VALUE>",
            vec![
                "<STRING>", "<NUMBER>", "<OBJECT>", "<ARRAY>", "true", "false", "null",
            ],
        );
        GRAMMAR.insert("<STRING>", vec!["\"\"", "\"<CHARS>\""]);
        GRAMMAR.insert("<CHARS>", vec!["<CHAR>", "<CHARS>"]);
        GRAMMAR.insert(
            "<CHAR>",
            vec![
                "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p",
                "q", "r", "s", "t", "v", "w", "x", "y", "z",
            ],
        );
        GRAMMAR.insert(
            "<NUMBER>",
            vec!["<INT>", "<INT><FRAC>", "<INT><EXP>", "<INT><FRAC><EXP>"],
        );
        GRAMMAR.insert("<INT>", vec!["<DIGIT><DIGITS>", "-<DIGIT><DIGITS>"]);
        GRAMMAR.insert("<FRAC>", vec![".<DIGITS>"]);
        GRAMMAR.insert("<EXP>", vec!["<E><DIGITS>"]);
        GRAMMAR.insert("<DIGITS>", vec!["<DIGIT><DIGITS>", "<DIGIT>"]);
        GRAMMAR.insert(
            "<DIGIT>",
            vec!["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"],
        );
        GRAMMAR.insert("<E>", vec!["e", "e+", "e-", "E", "E+", "E-"]);
    }
}
