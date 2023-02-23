use std::collections::{BTreeMap, BTreeSet, HashMap};
use std::path::Path;
use std::process::Command;
use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize, Default, Debug)]
// Ordered keys
struct Grammar(BTreeMap<String, Vec<Vec<String>>>);

#[derive(Clone, Copy, Debug)]
struct FragmentId(usize);

#[derive(Clone, Debug)]
enum Fragment {
    NonTerminal(Vec<FragmentId>),
    Expression(Vec<FragmentId>),
    Terminal(Vec<u8>),
    Nop,
}

#[derive(Debug, Default)]

struct GrammarRust {
    fragments: Vec<Fragment>,
    start: Option<FragmentId>,
    name_to_fragment: BTreeMap<String, FragmentId>,
}

impl GrammarRust {
    fn new(grammar: &Grammar) -> Self {
        let mut ret = GrammarRust::default();

        for(non_term, _) in grammar.0.iter() {
            let fragment_id = ret.allocate_fragment(Fragment::NonTerminal(Vec::new()));
            ret.name_to_fragment.insert(non_term.clone(), fragment_id);
        }

        for (non_term, fragments) in grammar.0.iter() {
            let fragment_id = ret.name_to_fragment[non_term];
            let mut variants = Vec::new();

            for sub_fragment in fragments {
                let mut options = Vec::new();

                for option in sub_fragment {
                    let fragment_id = if let Some(&non_terminal) = ret.name_to_fragment.get(option) {
                        ret.allocate_fragment(Fragment::NonTerminal(vec![non_terminal]))
                    } else {
                        ret.allocate_fragment(Fragment::Terminal(option.as_bytes().to_vec()))
                    };

                    options.push(fragment_id);
                }

                variants.push(ret.allocate_fragment(Fragment::Expression(options)))
            }

            let fragment = &mut ret.fragments[fragment_id.0];
            *fragment = Fragment::NonTerminal(variants);
        }

        ret.start = Some(ret.name_to_fragment["<start>"]);

        return ret;
    }

    pub fn allocate_fragment(&mut self, fragment: Fragment) -> FragmentId {
        let fragment_id = FragmentId(self.fragments.len());
        self.fragments.push(fragment);

        return fragment_id;
    }
}

fn main() -> std::io::Result<()> {

    let args: Vec<String> = std::env::args().collect();
    if args.len() != 2 {
        return Ok(());
    }

    let grammar: Grammar = serde_json::from_slice(
        &std::fs::read(&args[1])?)?;

    println!("Loaded grammar");

    let mut gram = GrammarRust::new(&grammar);

    println!("Converted grammar to data structure");

    println!("{:?}", gram);

    Ok(())
}
