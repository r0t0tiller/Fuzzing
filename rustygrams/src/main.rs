use rand::Rng;
use regex::Regex;
use std::{collections::VecDeque, ops::Index};

mod grammar;
use grammar::*;

static mut TERMINALS: VecDeque<String> = VecDeque::new();

fn expand_symbol(symbol: &str) {
    let mut rng = rand::thread_rng();
    let extract_data = Regex::new(r"(.*)(<[a-zA-Z_]*>)(.*)").unwrap();
    let groups = extract_data.captures(symbol);

    if !symbol.contains("<") || !symbol.contains(">") {
        unsafe { TERMINALS.push_back(symbol.to_string()) };
    }

    if symbol.contains("<") || symbol.contains(">") {
        if groups.is_some() {
            let ref_groups = groups.as_ref();
            let group_data_left = ref_groups.unwrap().get(1).unwrap().as_str();
            let group_data_middle = ref_groups.unwrap().get(2).unwrap().as_str();
            let group_data_right = ref_groups.unwrap().get(3).unwrap().as_str();

            if group_data_left.contains("<") || group_data_left.contains(">") {
                expand_symbol(group_data_left);
            } else if group_data_right.contains("<") || group_data_right.contains(">") {
                expand_symbol(group_data_right);
            } else {
                unsafe { TERMINALS.push_back(group_data_left.to_string()) };
            }

            let new_symbol = unsafe { GRAMMAR.get(group_data_middle) }.unwrap();
            let new_expansion = new_symbol.index(rng.gen_range(0..new_symbol.len()));

            expand_symbol(new_expansion);

            unsafe { TERMINALS.push_back(group_data_right.to_string()) };
        } else {
            let new_symbol = unsafe { GRAMMAR.get(symbol) };
            if new_symbol.is_some() {
                let new_symbol = new_symbol.unwrap();
                let new_expansion = new_symbol.index(rng.gen_range(0..new_symbol.len()));
                expand_symbol(new_expansion);
            }
        }
    }
}

fn main() {
    load_json_grammar();

    let mut rng = rand::thread_rng();
    let start = unsafe { GRAMMAR.get("<JSON>") };

    if start.is_some() {
        let possible_expansions = start.unwrap();
        let expansion = possible_expansions.index(rng.gen_range(0..possible_expansions.len()));
        expand_symbol(expansion)
    }

    unsafe {
        for terms in TERMINALS.iter() {
            print!("{}", terms);
        }
    }
}
